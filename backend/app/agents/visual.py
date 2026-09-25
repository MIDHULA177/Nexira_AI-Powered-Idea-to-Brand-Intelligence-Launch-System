import os
import json
import requests
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.agents.base_agent import BaseAgent
from app.services.llm_service import call_llm_validated

SYSTEM_PROMPT = """
You are NEXIRA's Visual Agent — a visual brand identity director.

Using the approved discovery, positioning, and brand shape information, develop a complete visual identity direction.

This is a direction document — not a final design. It defines the visual language the brand should use.

Return a JSON object with these exact fields:
- concept: A short paragraph describing the overall visual concept and what it communicates
- color_direction: Object with:
  - primary: The primary color description (name + hex if possible, e.g. "Deep Navy #1B2A4A")
  - secondary: Array of secondary color descriptions
  - accent: Array of accent color descriptions
  - rationale: Why these colors fit the brand personality and audience
- typography: Object with:
  - heading_character: Description of heading typeface character (e.g. "Bold geometric sans-serif, confident and modern")
  - body_character: Description of body typeface character (e.g. "Clean humanist sans-serif, readable and approachable")
  - rationale: Why this typography fits the brand
- imagery: Description of the imagery style and direction
- composition: Description of layout and composition principles
- logo_direction: Description of the logo/symbol concept and direction
- visual_rules: Object with:
  - do: Array of visual rules to follow
  - avoid: Array of visual elements to avoid

Ground every decision in the brand personality, positioning, and target audience.
Be specific and directional — not generic.
Return only valid JSON with all fields present.
"""

MOODBOARD_IMAGE_PROMPT_TEMPLATE = (
    "A moodboard image for a brand with the following visual direction: "
    "{concept}. Color palette: {colors}. Style: {imagery}. "
    "Composition: {composition}. Professional brand photography, editorial quality."
)


class VisualAgent(BaseAgent):
    AGENT_NAME    = "visual"
    STAGE         = "visualize"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def build_context(self, project: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "initial_prompt": project["initial_prompt"],
            "discovery":      self._approved_data(project, "discovery"),
            "positioning":    self._approved_data(project, "positioning"),
            "shape":          self._approved_data(project, "shape"),
        }

    # ── Optional moodboard generation ─────────────────────────────────────────

    def generate_moodboard(self, db, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to generate moodboard images using DALL-E 3.
        If image generation is unavailable or fails, returns a
        not_requested status without raising — workflow continues.
        Per README §21: never pretend a moodboard exists if generation failed.
        """
        from bson import ObjectId

        project_id = str(project["_id"])
        visual_data = project["stages"]["visualize"].get("data") or {}

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._moodboard_unavailable(db, project_id, visual_data)

        image_prompt = self._build_image_prompt(visual_data)
        images = []

        # Generate 3 moodboard images
        for image_type in ["brand atmosphere", "product context", "audience lifestyle"]:
            try:
                url = self._generate_image(api_key, f"{image_prompt} Focus: {image_type}.")
                if url:
                    images.append({
                        "url":   url,
                        "prompt": f"{image_prompt} Focus: {image_type}.",
                        "type":  image_type,
                    })
            except Exception:
                # Per README §21: if image generation fails, skip gracefully
                continue

        if not images:
            return self._moodboard_unavailable(db, project_id, visual_data)

        moodboard = {
            "status":     "generated",
            "images":     images,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        visual_data["moodboard"] = moodboard

        db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "stages.visualize.data": visual_data,
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        return moodboard

    # ── Moodboard helpers ──────────────────────────────────────────────────────

    def _generate_image(self, api_key: str, prompt: str) -> Optional[str]:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model":   "dall-e-3",
                "prompt":  prompt,
                "n":       1,
                "size":    "1024x1024",
                "quality": "standard",
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["data"][0]["url"]

    def _build_image_prompt(self, visual_data: Dict[str, Any]) -> str:
        color_dir = visual_data.get("color_direction", {})
        colors = ", ".join(filter(None, [
            color_dir.get("primary", ""),
            *color_dir.get("secondary", [])[:2],
        ])) or "neutral tones"

        return MOODBOARD_IMAGE_PROMPT_TEMPLATE.format(
            concept    = visual_data.get("concept", "modern brand"),
            colors     = colors,
            imagery    = visual_data.get("imagery", "clean and professional"),
            composition= visual_data.get("composition", "minimal"),
        )

    def _moodboard_unavailable(
        self, db, project_id: str, visual_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        from bson import ObjectId
        moodboard = {"status": "not_requested"}
        visual_data["moodboard"] = moodboard
        db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "stages.visualize.data.moodboard": moodboard,
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        return moodboard
