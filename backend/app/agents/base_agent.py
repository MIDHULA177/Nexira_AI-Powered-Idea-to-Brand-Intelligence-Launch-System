from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.services.llm_service import call_llm_validated
from app.models.project import save_stage_result, restore_stage_on_failure
from app.schemas.stage_schemas import ValidationError


class BaseAgent:
    """
    Base class for all NEXIRA agents.

    Subclasses must define:
        AGENT_NAME   : str  - matches agent_runs.agent field
        STAGE        : str  - matches project stages key
        SYSTEM_PROMPT: str  - filled by AI Workflow Engineer (or owner for visual/launch)

    Subclasses must implement:
        build_context(project) -> dict  - assembles the user_content dict sent to LLM
    """

    AGENT_NAME    = NotImplemented
    STAGE         = NotImplemented
    SYSTEM_PROMPT = NotImplemented

    # ── Public interface ──────────────────────────────────────────────────────

    def run(self, db, project, trigger: str = "initial_generation") -> Dict[str, Any]:
        """
        Generate output for this agent's stage.
        Validates output, persists to project, logs agent run.
        Returns the validated data dict.
        Raises RuntimeError on LLM or validation failure — does NOT overwrite
        any existing approved state.
        """
        self._assert_configured()
        project_id   = str(project["_id"])
        input_context = self.build_context(project)
        user_content  = self._serialise_context(input_context)

        # Mark stage as generating so frontend can show loading state
        self._set_generating(db, project_id)

        try:
            data = call_llm_validated(
                db          = db,
                project_id  = project_id,
                agent       = self.AGENT_NAME,
                stage       = self.STAGE,
                trigger     = trigger,
                system_prompt = self.SYSTEM_PROMPT,
                user_content  = user_content,
                input_context = input_context,
            )
        except RuntimeError:
            # Restore stage to a usable status — never leave it stuck on 'generating'
            restore_stage_on_failure(db, project_id, self.STAGE)
            raise

        save_stage_result(db, project_id, self.STAGE, data, source="ai")
        return data

    def regenerate(self, db, project, trigger: str = "user_regenerate") -> Dict[str, Any]:
        """
        Regenerate output for this stage.
        Identical to run() but uses a different trigger label.
        Existing approved data is preserved if this call fails — save_stage_result
        only writes on success, and call_llm_validated raises before returning
        on failure.
        """
        return self.run(db, project, trigger=trigger)

    # ── Subclass contract ─────────────────────────────────────────────────────

    def build_context(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the context dict passed as user content to the LLM.
        Must be implemented by each subclass.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement build_context()"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_generating(self, db, project_id: str):
        """Mark stage status as generating so the frontend can show a loading state."""
        from datetime import datetime, timezone
        db.projects.update_one(
            {"_id": __import__("bson").ObjectId(project_id)},
            {"$set": {
                f"stages.{self.STAGE}.status": "generating",
                "updated_at": datetime.now(timezone.utc),
            }}
        )

    def _serialise_context(self, context: Dict[str, Any]) -> str:
        """Convert context dict to a JSON string for the LLM user message."""
        import json
        return json.dumps(context, ensure_ascii=False, default=str)

    def _assert_configured(self):
        for attr in ("AGENT_NAME", "STAGE", "SYSTEM_PROMPT"):
            val = getattr(self, attr, NotImplemented)
            if val is NotImplemented:
                raise RuntimeError(
                    f"{self.__class__.__name__}.{attr} must be defined"
                )
            if attr == "SYSTEM_PROMPT" and not val:
                raise RuntimeError(
                    f"{self.__class__.__name__}.SYSTEM_PROMPT is empty — "
                    "AI Workflow Engineer must fill this prompt before use"
                )

    # ── Approved stage data helper ────────────────────────────────────────────

    @staticmethod
    def _approved_data(project: Dict[str, Any], stage: str) -> Optional[Dict[str, Any]]:
        """Return approved stage data or None if not yet approved."""
        stage_doc = project.get("stages", {}).get(stage, {})
        if stage_doc.get("status") == "approved":
            return stage_doc.get("data")
        return None
