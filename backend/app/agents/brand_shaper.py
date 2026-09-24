import json
from typing import Any, Dict, Optional

from app.agents.base_agent import BaseAgent
from app.services.llm_service import call_llm_validated
from app.models.project import save_stage_result

# ── Prompt ────────────────────────────────────────────────────────────────────
# Owner: AI Workflow Engineer
# Contract: output must satisfy SHAPE_SCHEMA in app/schemas/stage_schemas.py
#
# Required output fields:
#   personality: {
#     traits      : list of {name, rationale}
#     avoid_traits: list of {name, reason}
#   }
#   naming: {
#     territories : list of {name, concept, rationale, keywords[], naming_characteristics}
#     candidates  : list of {name, concept, rationale, positioning_alignment, concerns[]}
#     selected_name: str or null
#   }
#   tagline: str  (or list of str for multiple options)
#   voice: {
#     description      : str
#     tone             : str
#     writing_principles: list of str
#     preferred_words  : list of str
#     words_to_avoid   : list of str
#     example_messaging: str
#   }

SYSTEM_PROMPT = """
You are NEXIRA's Brand Shaper Agent — a verbal and conceptual brand identity expert.

Using the approved discovery and positioning information, develop the complete verbal brand identity.

Return a JSON object with these exact fields:
- personality: Object with:
  - traits: Array of objects with "name" and "rationale" (3-5 personality traits)
  - avoid_traits: Array of objects with "name" and "reason" (traits to actively avoid)
- naming: Object with:
  - territories: Array of 3-4 naming territory objects, each with "name", "concept", "rationale", "keywords" (array), "naming_characteristics"
  - candidates: Array of name candidate objects, each with "name", "concept", "rationale", "positioning_alignment", "concerns" (array)
  - selected_name: null (user will select)
- tagline: A single recommended tagline string (the best option given the positioning)
- voice: Object with:
  - description: Overall voice description
  - tone: Tone descriptor
  - writing_principles: Array of writing principle strings
  - preferred_words: Array of words/phrases to use
  - words_to_avoid: Array of words/phrases to avoid
  - example_messaging: A short example message in this voice

Do not claim trademark, domain, or legal availability for any names.
Return only valid JSON with all fields present.
"""

# Prompt used when generating names after a territory is selected
NAMES_PROMPT = """
You are NEXIRA's Brand Shaper Agent generating name candidates for a selected naming territory.

Generate 5-6 name candidates that fit the selected territory and are grounded in the approved brand context.

Return a JSON object with:
- candidates: Array of objects, each with "name", "concept", "rationale", "positioning_alignment", "concerns" (array)

Do not claim trademark, domain, or legal availability.
Return only valid JSON.
"""


class BrandShaperAgent(BaseAgent):
    AGENT_NAME    = "brand_shaper"
    STAGE         = "shape"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def build_context(self, project: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "initial_prompt": project["initial_prompt"],
            "discovery":      self._approved_data(project, "discovery"),
            "positioning":    self._approved_data(project, "positioning"),
        }

    # ── Territory selection ───────────────────────────────────────────────────

    def select_territory(self, db, project: Dict[str, Any], territory_name: str) -> Dict[str, Any]:
        """
        Record the user's selected naming territory on the shape stage data.
        Does not call the LLM — purely a state update.
        Returns updated shape data.
        """
        from bson import ObjectId
        from datetime import datetime, timezone

        project_id = str(project["_id"])
        shape_data = project["stages"]["shape"].get("data") or {}

        naming = shape_data.get("naming", {})
        naming["selected_territory"] = territory_name
        shape_data["naming"] = naming

        db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "stages.shape.data": shape_data,
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        return shape_data

    # ── Name generation after territory selected ──────────────────────────────

    def generate_names(self, db, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate name candidates for the selected territory.
        Called after the user selects a territory.
        Returns updated shape data with candidates populated.
        """
        from bson import ObjectId
        from datetime import datetime, timezone

        project_id = str(project["_id"])
        shape_data = project["stages"]["shape"].get("data") or {}
        naming     = shape_data.get("naming", {})
        selected   = naming.get("selected_territory")

        context = {
            "initial_prompt":     project["initial_prompt"],
            "discovery":          self._approved_data(project, "discovery"),
            "positioning":        self._approved_data(project, "positioning"),
            "personality":        shape_data.get("personality"),
            "selected_territory": selected,
            "territories":        naming.get("territories", []),
        }

        result = call_llm_validated(
            db            = db,
            project_id    = project_id,
            agent         = self.AGENT_NAME,
            stage         = self.STAGE,
            trigger       = "name_generation",
            system_prompt = NAMES_PROMPT,
            user_content  = self._serialise_context(context),
            input_context = context,
        )

        naming["candidates"] = result.get("candidates", [])
        shape_data["naming"] = naming

        db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "stages.shape.data": shape_data,
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        return shape_data

    # ── Name selection ────────────────────────────────────────────────────────

    def select_name(self, db, project: Dict[str, Any], name: str) -> Dict[str, Any]:
        """
        Record the user's selected name on the shape stage data.
        Marks all other candidates as not selected.
        Returns updated shape data.
        """
        from bson import ObjectId
        from datetime import datetime, timezone

        project_id = str(project["_id"])
        shape_data = project["stages"]["shape"].get("data") or {}
        naming     = shape_data.get("naming", {})

        for candidate in naming.get("candidates", []):
            candidate["selected"] = (candidate.get("name") == name)
        naming["selected_name"] = name
        shape_data["naming"] = naming

        db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "stages.shape.data": shape_data,
                "updated_at": datetime.now(timezone.utc),
            }}
        )
        return shape_data
