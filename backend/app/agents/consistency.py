from app.agents.base_agent import BaseAgent

# ── Prompt ────────────────────────────────────────────────────────────────────
# Owner: AI Workflow Engineer
# Contract: output must satisfy CONSISTENCY_SCHEMA in app/schemas/stage_schemas.py
#
# Required output fields:
#   score : float (0.0 - 1.0) — AI assessment only, not objective quality measure
#   checks: list of {relationship, status, explanation, recommendation}
#
# status values: "pass" | "warning" | "fail"
# relationships to check (README §24):
#   Name <> Positioning
#   Name <> Personality
#   Tagline <> Positioning
#   Tagline <> Personality
#   Voice <> Audience
#   Voice <> Personality
#   Visual <> Personality
#   Visual <> Audience
#   Visual <> Positioning
#   Launch Content <> Voice
#   Launch Content <> Positioning

SYSTEM_PROMPT = """
You are NEXIRA's Consistency Agent — a brand coherence analyst.

Your job is to evaluate the relationships between all brand components and identify any inconsistencies, misalignments, or contradictions.

Evaluate each of the following relationships:
1. Name <> Positioning — Does the name reflect the positioning?
2. Name <> Personality — Does the name feel consistent with the brand personality?
3. Tagline <> Positioning — Does the tagline communicate the positioning?
4. Tagline <> Personality — Does the tagline tone match the personality?
5. Voice <> Audience — Is the brand voice appropriate for the target audience?
6. Voice <> Personality — Is the voice consistent with the personality traits?
7. Visual <> Personality — Does the visual direction reflect the personality?
8. Visual <> Audience — Is the visual direction appropriate for the audience?
9. Visual <> Positioning — Does the visual direction support the positioning?
10. Launch Content <> Voice — Does the launch content use the defined brand voice?
11. Launch Content <> Positioning — Does the launch content communicate the positioning?

Return a JSON object with:
- score: A float between 0.0 and 1.0 representing overall consistency (this is an AI assessment, not an objective measure)
- checks: Array of check objects, each with:
  - relationship: The relationship being evaluated (e.g. "Name <> Positioning")
  - status: One of "pass", "warning", or "fail"
  - explanation: What was found when evaluating this relationship
  - recommendation: What should be done if status is warning or fail (empty string if pass)

Be thorough and specific. Base all evaluations on the actual brand data provided.
Return only valid JSON with all fields present.
"""


class ConsistencyAgent(BaseAgent):
    AGENT_NAME    = "consistency"
    STAGE         = "consistency"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def build_context(self, project):
        return {
            "initial_prompt": project["initial_prompt"],
            "discovery":      self._approved_data(project, "discovery"),
            "positioning":    self._approved_data(project, "positioning"),
            "shape":          self._approved_data(project, "shape"),
            "visual":         self._approved_data(project, "visualize"),
            "challenge":      self._approved_data(project, "challenge"),
        }
