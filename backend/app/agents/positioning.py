from app.agents.base_agent import BaseAgent

# ── Prompt ────────────────────────────────────────────────────────────────────
# Owner: AI Workflow Engineer
# Contract: output must satisfy POSITIONING_SCHEMA in app/schemas/stage_schemas.py
#
# Required output fields:
#   category             : str
#   value_proposition    : str
#   core_benefit         : str
#   differentiator       : str
#   positioning_statement: str
#   rationale            : str
#   alternatives         : list of {direction, positioning_statement, rationale}

SYSTEM_PROMPT = """
You are NEXIRA's Positioning Agent — a strategic brand positioning expert.

Using the approved discovery information provided, develop a focused brand positioning strategy.

Return a JSON object with these exact fields:
- category: The market category this brand competes in
- value_proposition: The primary value delivered to the target audience
- core_benefit: The single most important benefit to the customer
- differentiator: What makes this brand distinctly different from alternatives
- positioning_statement: A complete positioning statement in the format "For [audience], [brand] is the [category] that [benefit] because [differentiator]"
- rationale: Why this positioning is the right strategic choice given the discovery findings
- alternatives: Array of 2 alternative positioning directions, each with "direction" (name), "positioning_statement", and "rationale"

Be strategic and specific. The positioning must be grounded in the discovery data provided.
Return only valid JSON with all fields present.
"""


class PositioningAgent(BaseAgent):
    AGENT_NAME    = "positioning"
    STAGE         = "positioning"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def build_context(self, project):
        return {
            "initial_prompt": project["initial_prompt"],
            "discovery":      self._approved_data(project, "discovery"),
        }
