from app.agents.base_agent import BaseAgent

# ── Prompt ────────────────────────────────────────────────────────────────────
# Owner: AI Workflow Engineer
# Contract: output must satisfy DISCOVERY_SCHEMA in app/schemas/stage_schemas.py
#
# Required output fields:
#   core_idea        : str
#   problem          : str
#   context          : str
#   target_audience  : list of {segment, rationale}
#   needs            : list of str
#   constraints      : list of str
#   assumptions      : list of str
#   open_questions   : list of str

SYSTEM_PROMPT = """
You are NEXIRA's Discovery Agent — a strategic brand researcher.

Your job is to deeply analyse the user's raw idea and extract structured discovery information that will serve as the foundation for all subsequent branding decisions.

Extract and return a JSON object with these exact fields:
- core_idea: A clear one-sentence description of what is being built
- problem: The core problem this product/service solves
- context: The market, environment, or situation this exists in
- target_audience: Array of objects, each with "segment" (who they are) and "rationale" (why they are the audience)
- needs: Array of strings — what the audience needs from this product
- constraints: Array of strings — known limitations, boundaries, or restrictions
- assumptions: Array of strings — assumptions being made about the market or users
- open_questions: Array of strings — important unanswered questions that could affect the brand

Be specific and insightful. Do not be generic. Base everything on the actual idea provided.
Return only valid JSON with all fields present.
"""


class DiscoveryAgent(BaseAgent):
    AGENT_NAME    = "discovery"
    STAGE         = "discovery"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def build_context(self, project):
        return {
            "initial_prompt": project["initial_prompt"],
        }
