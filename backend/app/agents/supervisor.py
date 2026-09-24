from typing import Any, Dict, Optional

from app.models.project import (
    STAGE_ORDER, STAGE_DEPENDENCIES,
    approve_stage as model_approve_stage,
    edit_stage as model_edit_stage,
    save_stage_result,
    get_project,
)
from app.agents.discovery    import DiscoveryAgent
from app.agents.positioning  import PositioningAgent
from app.agents.brand_shaper import BrandShaperAgent
from app.agents.visual       import VisualAgent
from app.agents.critic       import CriticAgent
from app.agents.consistency  import ConsistencyAgent
from app.agents.launch       import LaunchAgent


# ── Agent registry ────────────────────────────────────────────────────────────

_AGENTS = {
    "discovery":   DiscoveryAgent(),
    "positioning": PositioningAgent(),
    "shape":       BrandShaperAgent(),
    "visualize":   VisualAgent(),
    "challenge":   CriticAgent(),
    "consistency": ConsistencyAgent(),
    "launch":      LaunchAgent(),
}

# Stages that support edit + approve (challenge/consistency are run-only)
_EDITABLE_STAGES   = {"discovery", "positioning", "shape", "visualize", "launch"}
_APPROVABLE_STAGES = {"discovery", "positioning", "shape", "visualize", "launch"}


# ── Supervisor ────────────────────────────────────────────────────────────────

class Supervisor:

    # ── Stage generation ──────────────────────────────────────────────────────

    def generate(self, db, project: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """
        Run the agent for the given stage.
        Enforces: stage must be available/outdated, all dependencies approved.
        Returns updated project.
        """
        self._assert_stage_runnable(project, stage)
        agent = self._get_agent(stage)
        agent.run(db, project, trigger="initial_generation")
        return get_project(db, str(project["_id"]), str(project["user_id"]))

    def regenerate(self, db, project: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """
        Regenerate output for a stage that is in review, approved, or outdated.
        Preserves existing approved data until new result is accepted.
        """
        self._assert_stage_has_data(project, stage)
        self._assert_dependencies_approved(project, stage)
        agent = self._get_agent(stage)
        agent.regenerate(db, project, trigger="user_regenerate")
        return get_project(db, str(project["_id"]), str(project["user_id"]))

    # ── Approval ──────────────────────────────────────────────────────────────

    def approve(self, db, project: Dict[str, Any], stage: str, user_id: str) -> Dict[str, Any]:
        """
        Approve a stage that is in review status.
        Unlocks the next stage. Creates a version snapshot.
        """
        if stage not in _APPROVABLE_STAGES:
            raise ValueError(f"Stage '{stage}' does not support approval")

        stage_doc = project["stages"][stage]
        if stage_doc["status"] not in ("review", "approved"):
            raise ValueError(
                f"Stage '{stage}' must be in review status to approve "
                f"(current: {stage_doc['status']})"
            )
        if not stage_doc.get("data"):
            raise ValueError(f"Stage '{stage}' has no data to approve")

        model_approve_stage(db, str(project["_id"]), stage, user_id)
        return get_project(db, str(project["_id"]), user_id)

    # ── Edit ──────────────────────────────────────────────────────────────────

    def edit(
        self, db, project: Dict[str, Any], stage: str,
        data: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """
        Save user-edited data for a stage.
        Marks downstream stages as outdated.
        Creates a version snapshot.
        """
        if stage not in _EDITABLE_STAGES:
            raise ValueError(f"Stage '{stage}' does not support editing")

        stage_doc = project["stages"][stage]
        if stage_doc["status"] == "locked":
            raise ValueError(f"Stage '{stage}' is locked and cannot be edited")
        if not stage_doc.get("data"):
            raise ValueError(f"Stage '{stage}' has no existing data to edit")

        model_edit_stage(db, str(project["_id"]), stage, data, user_id)
        return get_project(db, str(project["_id"]), user_id)

    # ── Targeted refinement (README §23) ──────────────────────────────────────

    def targeted_refinement(
        self, db, project: Dict[str, Any], stage: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Re-run only the specified stage agent without touching other approved stages.
        Used after Critic identifies an issue in a specific component.
        Example: if only naming is broken, re-run shape only — not visual/consistency.
        """
        self._assert_dependencies_approved(project, stage)
        agent = self._get_agent(stage)
        agent.regenerate(db, project, trigger="targeted_refinement")
        return get_project(db, str(project["_id"]), user_id)

    # ── Shape-specific actions ────────────────────────────────────────────────

    def select_territory(
        self, db, project: Dict[str, Any], territory_name: str
    ) -> Dict[str, Any]:
        agent = _AGENTS["shape"]
        agent.select_territory(db, project, territory_name)
        return get_project(db, str(project["_id"]), str(project["user_id"]))

    def generate_names(self, db, project: Dict[str, Any]) -> Dict[str, Any]:
        agent = _AGENTS["shape"]
        agent.generate_names(db, project)
        return get_project(db, str(project["_id"]), str(project["user_id"]))

    def select_name(
        self, db, project: Dict[str, Any], name: str
    ) -> Dict[str, Any]:
        agent = _AGENTS["shape"]
        agent.select_name(db, project, name)
        return get_project(db, str(project["_id"]), str(project["user_id"]))

    # ── Visual moodboard ──────────────────────────────────────────────────────

    def generate_moodboard(self, db, project: Dict[str, Any]) -> Dict[str, Any]:
        stage_doc = project["stages"]["visualize"]
        if stage_doc.get("status") not in ("approved", "review"):
            raise ValueError("Visual stage must be approved or in review before generating moodboard")
        agent = _AGENTS["visualize"]
        agent.generate_moodboard(db, project)
        return get_project(db, str(project["_id"]), str(project["user_id"]))

    # ── Workflow state query ──────────────────────────────────────────────────

    def get_available_actions(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a map of stage -> available actions based on current project state.
        Used by the frontend to know what buttons to show.
        """
        actions = {}
        for stage in STAGE_ORDER:
            stage_doc = project["stages"][stage]
            status    = stage_doc["status"]
            has_data  = bool(stage_doc.get("data"))
            deps_ok   = self._dependencies_approved(project, stage)

            available = []
            if status in ("available", "outdated") and deps_ok:
                available.append("generate")
            if status in ("review", "approved", "outdated") and has_data and deps_ok:
                available.append("regenerate")
            if status == "review" and has_data and stage in _APPROVABLE_STAGES:
                available.append("approve")
            if status in ("review", "approved") and has_data and stage in _EDITABLE_STAGES:
                available.append("edit")

            actions[stage] = {
                "status":  status,
                "actions": available,
            }
        return actions

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get_agent(self, stage: str):
        agent = _AGENTS.get(stage)
        if not agent:
            raise ValueError(f"No agent registered for stage '{stage}'")
        return agent

    def _assert_stage_runnable(self, project: Dict[str, Any], stage: str):
        stage_doc = project["stages"][stage]
        status    = stage_doc["status"]
        if status == "locked":
            raise ValueError(
                f"Stage '{stage}' is locked. "
                "Complete and approve all prerequisite stages first."
            )
        if status == "generating":
            raise ValueError(f"Stage '{stage}' is already generating.")
        self._assert_dependencies_approved(project, stage)

    def _assert_stage_has_data(self, project: Dict[str, Any], stage: str):
        stage_doc = project["stages"][stage]
        if not stage_doc.get("data"):
            raise ValueError(
                f"Stage '{stage}' has no existing data. Use generate instead."
            )

    def _assert_dependencies_approved(self, project: Dict[str, Any], stage: str):
        not_approved = self._unapproved_dependencies(project, stage)
        if not_approved:
            raise ValueError(
                f"Stage '{stage}' requires these stages to be approved first: "
                + ", ".join(not_approved)
            )

    def _dependencies_approved(self, project: Dict[str, Any], stage: str) -> bool:
        return len(self._unapproved_dependencies(project, stage)) == 0

    def _unapproved_dependencies(
        self, project: Dict[str, Any], stage: str
    ) -> list:
        deps = STAGE_DEPENDENCIES.get(stage, [])
        return [
            dep for dep in deps
            if project["stages"][dep]["status"] != "approved"
        ]


# ── Module-level singleton ────────────────────────────────────────────────────

supervisor = Supervisor()
