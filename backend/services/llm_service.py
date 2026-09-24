import json
import os
from typing import Any, Dict

import requests


def _fallback_response(stage_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    idea = context.get("idea", "")
    audience = context.get("audience", "")
    industry = context.get("industry", "")

    if stage_name == "discover":
        return {
            "core_problem": f"People struggle to transform a rough idea into a clear, credible market-facing brand.",
            "target_users": ["founders", "early-stage startups", "creative builders"],
            "user_needs": ["clarity", "direction", "positioning", "quick validation"],
            "context": f"The user is working on: {idea} for {audience or 'a broad audience'} in {industry or 'a growing market'}.",
            "constraints": ["limited time", "incomplete idea", "need for fast validation"],
            "open_questions": [
                "What is the most important problem this idea solves?",
                "Who is the first customer to care most?",
                "How is this different from current market alternatives?"
            ]
        }

    if stage_name == "position":
        return {
            "category": "AI brand strategy platform",
            "value_proposition": "NEXIRA helps founders turn vague concepts into focused, launch-ready brand systems in minutes.",
            "differentiator": "It combines idea discovery, positioning, critique, and final launch messaging in one adaptive workflow.",
            "competitive_angle": "Instead of static branding advice, it produces an evolving strategic narrative grounded in the original idea.",
            "positioning_statement": f"For {audience or 'ambitious builders'}, NEXIRA is the AI-powered brand system that transforms an early idea into a compelling, differentiated market story."
        }

    if stage_name == "shape":
        return {
            "personality": [
                {"trait": "Strategic", "reason": "The brand must help users think clearly under uncertainty."},
                {"trait": "Confident", "reason": "The experience should feel decisive and credible."},
                {"trait": "Human", "reason": "The brand should remain approachable instead of feel like a generic AI tool."}
            ],
            "avoid": ["Overly corporate", "Generic", "Childish"],
            "naming_territories": [
                {
                    "territory": "Human-centered",
                    "names": ["Northstar", "Signal", "Clarity"],
                    "reason": "Puts the founder and customer experience at the center."
                },
                {
                    "territory": "Technology-centered",
                    "names": ["Vector", "Forge", "PilotAI"],
                    "reason": "Creates a modern and intelligent feel."
                },
                {
                    "territory": "Purpose-centered",
                    "names": ["Purposely", "Origin", "Northbound"],
                    "reason": "Emphasizes meaning and mission."
                }
            ]
        }

    if stage_name == "visualize":
        return {
            "color_mood": ["Modern", "Confident", "Trustworthy"],
            "typography": "Modern geometric sans-serif with strong contrast and clear hierarchy.",
            "composition": "Clean product-first layout with ample white space and confident consistency.",
            "imagery": "Smart, constructive visuals that emphasise momentum and clarity.",
            "symbol_direction": "Abstract, directional forms with simple geometric linework and product-led shapes.",
            "visual_concepts_to_avoid": ["Overloaded gradients", "Corporate stock art", "Generic startup clichés"]
        }

    if stage_name == "challenge":
        return {
            "issues": [
                {
                    "type": "Generic positioning",
                    "severity": "medium",
                    "description": "The current direction risks sounding like a generic AI tool without a distinct point of view.",
                    "alternative": "Anchor the brand around clarity and transformation for founders with constrained time."
                },
                {
                    "type": "Audience mismatch",
                    "severity": "low",
                    "description": "If the product is positioned for enterprise users too early, it could lose an early-stage founder audience.",
                    "alternative": "Focus on founders, makers, and early builders first."
                }
            ]
        }

    if stage_name == "consistency":
        return {
            "checks": [
                {"element": "Name ↔ Positioning", "status": "PASS", "reason": "The name signals direction and clarity, matching the intended strategic value proposition."},
                {"element": "Visual ↔ Audience", "status": "PASS", "reason": "The visual system feels contemporary and credible for founders and digital builders."},
                {"element": "Voice ↔ Mission", "status": "WARNING", "reason": "The voice should avoid sounding too polished or corporate if the product aims to feel approachable."}
            ]
        }

    if stage_name == "deliver":
        return {
            "one_line_pitch": "A faster way to turn a raw idea into a focused, launch-ready brand system.",
            "landing_headline": "From raw idea to launch-ready brand.",
            "product_description": "NEXIRA helps founders and creators turn an early concept into a coherent brand strategy through structured thinking, critique, and launch messaging.",
            "social_post": "Your idea deserves a stronger story. NEXIRA helps turn rough concepts into clear brand direction, sharper positioning, and launch-ready messaging.",
            "launch_message": "We built NEXIRA to help ambitious builders move from vague idea to compelling brand with more clarity, confidence, and speed."
        }

    return {"message": "Fallback output generated successfully."}


def generate_stage(stage_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        try:
            payload = {
                "model": "gpt-4o-mini",
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a strategic brand advisor. Return valid JSON only. Make the output specific, concise, and useful."
                    },
                    {
                        "role": "user",
                        "content": json.dumps({"stage": stage_name, "context": context}, ensure_ascii=False)
                    }
                ]
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=40,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception:
            return _fallback_response(stage_name, context)

    return _fallback_response(stage_name, context)
