from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.auth.decorators import jwt_required_custom
from app.db.connection import get_db
from app.models.project import get_project, serialize_project
from app.agents.supervisor import supervisor
from app.services.llm_service import get_agent_runs
from app.utils.helpers import success, error, serialize_doc, sanitize, MAX_PROMPT_LEN, MAX_NAME_LEN

workflow_bp = Blueprint("workflow", __name__)

# ── Shared helpers ────────────────────────────────────────────────────────────

def _load_project(project_id, user_id):
    """Return project or None. Always scoped to the authenticated user."""
    return get_project(get_db(), project_id, user_id)


def _run_supervisor(action, project_id, user_id, **kwargs):
    """
    Wrapper that:
    - Loads the project (404 if not found / not owned)
    - Calls the supervisor action
    - Returns a success response with the updated serialized project
    - Maps ValueError (business logic) -> 400
    - Maps RuntimeError (LLM / infra) -> appropriate 5xx
    """
    db      = get_db()
    project = get_project(db, project_id, user_id)
    if not project:
        return error("Project not found", 404)

    try:
        updated = action(db=db, project=project, **kwargs)
        return success({"project": serialize_project(updated)})
    except ValueError as e:
        return error(str(e), 400)
    except RuntimeError as e:
        msg = str(e)
        if "timed out" in msg.lower():
            return error("AI generation timed out. Your previous data is safe. Please try again.", 504)
        if "rate limit" in msg.lower():
            return error("AI service is busy. Please try again in a moment.", 429)
        if "invalid output" in msg.lower() or "validation" in msg.lower():
            return error("AI returned an unexpected response. Your previous data is safe. Please try again.", 422)
        return error("AI generation failed. Your previous data is safe. Please try again.", 503)


# ── Generic stage routes (discovery / positioning / visualize / launch) ───────
# Shape and challenge have extra endpoints below.

GENERIC_STAGES = {"discovery", "positioning", "visualize", "launch"}


@workflow_bp.route("/<project_id>/stages/<stage>/generate", methods=["POST"])
@jwt_required_custom
def stage_generate(project_id, stage):
    if stage not in GENERIC_STAGES | {"shape", "challenge", "consistency"}:
        return error(f"Unknown stage '{stage}'", 400)
    user_id = get_jwt_identity()
    return _run_supervisor(
        lambda db, project: supervisor.generate(db, project, stage),
        project_id, user_id,
    )


@workflow_bp.route("/<project_id>/stages/<stage>/regenerate", methods=["POST"])
@jwt_required_custom
def stage_regenerate(project_id, stage):
    if stage not in GENERIC_STAGES | {"shape", "challenge", "consistency"}:
        return error(f"Unknown stage '{stage}'", 400)
    user_id = get_jwt_identity()
    return _run_supervisor(
        lambda db, project: supervisor.regenerate(db, project, stage),
        project_id, user_id,
    )


@workflow_bp.route("/<project_id>/stages/<stage>/approve", methods=["POST"])
@jwt_required_custom
def stage_approve(project_id, stage):
    user_id = get_jwt_identity()
    return _run_supervisor(
        lambda db, project: supervisor.approve(db, project, stage, user_id),
        project_id, user_id,
    )


@workflow_bp.route("/<project_id>/stages/<stage>/edit", methods=["POST"])
@jwt_required_custom
def stage_edit(project_id, stage):
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    payload = data.get("data")

    if not payload or not isinstance(payload, dict):
        return error("Request body must include a 'data' object with the edited stage content")

    # Enforce max payload size — serialize and check character count
    import json as _json
    if len(_json.dumps(payload)) > 50_000:
        return error("Edit payload is too large")

    return _run_supervisor(
        lambda db, project: supervisor.edit(db, project, stage, payload, user_id),
        project_id, user_id,
    )


# ── Shape-specific ────────────────────────────────────────────────────────────

@workflow_bp.route("/<project_id>/stages/shape/select-territory", methods=["POST"])
@jwt_required_custom
def shape_select_territory(project_id):
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    territory = data.get("territory", "").strip()

    if not territory:
        return error("'territory' name is required")

    return _run_supervisor(
        lambda db, project: supervisor.select_territory(db, project, territory),
        project_id, user_id,
    )


@workflow_bp.route("/<project_id>/stages/shape/generate-names", methods=["POST"])
@jwt_required_custom
def shape_generate_names(project_id):
    user_id = get_jwt_identity()
    return _run_supervisor(
        lambda db, project: supervisor.generate_names(db, project),
        project_id, user_id,
    )


@workflow_bp.route("/<project_id>/stages/shape/select-name", methods=["POST"])
@jwt_required_custom
def shape_select_name(project_id):
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    name    = data.get("name", "").strip()

    if not name:
        return error("'name' is required")

    return _run_supervisor(
        lambda db, project: supervisor.select_name(db, project, name),
        project_id, user_id,
    )


# ── Visualize moodboard (optional) ────────────────────────────────────────────

@workflow_bp.route("/<project_id>/stages/visualize/moodboard", methods=["POST"])
@jwt_required_custom
def visualize_moodboard(project_id):
    user_id = get_jwt_identity()
    return _run_supervisor(
        lambda db, project: supervisor.generate_moodboard(db, project),
        project_id, user_id,
    )


# ── Challenge fix (targeted refinement) ──────────────────────────────────────

@workflow_bp.route("/<project_id>/stages/challenge/fix", methods=["POST"])
@jwt_required_custom
def challenge_fix(project_id):
    """
    Targeted refinement — re-run only the specified stage agent.
    Body: { "stage": "shape" }  (the stage to fix, not "challenge")
    Per README §23: only regenerates the broken component.
    """
    user_id      = get_jwt_identity()
    data         = request.get_json(silent=True) or {}
    target_stage = data.get("stage", "").strip()

    valid_targets = {"discovery", "positioning", "shape", "visualize"}
    if target_stage not in valid_targets:
        return error(
            f"'stage' must be one of: {', '.join(sorted(valid_targets))}"
        )

    return _run_supervisor(
        lambda db, project: supervisor.targeted_refinement(
            db, project, target_stage, user_id
        ),
        project_id, user_id,
    )


# ── Agent runs ────────────────────────────────────────────────────────────────

@workflow_bp.route("/<project_id>/agent-runs", methods=["GET"])
@jwt_required_custom
def list_agent_runs(project_id):
    user_id = get_jwt_identity()
    db      = get_db()
    project = get_project(db, project_id, user_id)

    if not project:
        return error("Project not found", 404)

    runs = get_agent_runs(db, project_id)
    return success({"agent_runs": [serialize_doc(r) for r in runs]})


# ── Workflow status (available actions per stage) ─────────────────────────────

@workflow_bp.route("/<project_id>/workflow/actions", methods=["GET"])
@jwt_required_custom
def workflow_actions(project_id):
    """
    Returns what actions are available for each stage right now.
    Used by the frontend to know which buttons to enable.
    """
    user_id = get_jwt_identity()
    db      = get_db()
    project = get_project(db, project_id, user_id)

    if not project:
        return error("Project not found", 404)

    actions = supervisor.get_available_actions(project)
    return success({
        "actions":       actions,
        "current_stage": project["current_stage"],
        "progress":      project["progress"],
    })
