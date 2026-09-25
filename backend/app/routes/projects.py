from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from app.db.connection import get_db
from app.models.project import (
    create_project, get_project, get_user_projects,
    update_project_field, delete_project, serialize_project,
    get_project_versions
)
from app.auth.decorators import jwt_required_custom
from app.utils.helpers import success, error, MAX_PROMPT_LEN, MAX_NAME_LEN, sanitize

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("", methods=["GET"])
@jwt_required_custom
def list_projects():
    user_id  = get_jwt_identity()
    db       = get_db()
    projects = get_user_projects(db, user_id)
    return success({"projects": [serialize_project(p) for p in projects]})


@projects_bp.route("", methods=["POST"])
@jwt_required_custom
def new_project():
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}

    name           = sanitize(data.get("name", ""), MAX_NAME_LEN)
    initial_prompt = sanitize(data.get("initial_prompt", ""), MAX_PROMPT_LEN)

    if not name:
        return error("Project name is required")
    if not initial_prompt:
        return error("Initial prompt is required")
    if len(data.get("initial_prompt", "")) > MAX_PROMPT_LEN:
        return error(f"Initial prompt must be {MAX_PROMPT_LEN} characters or fewer")

    db      = get_db()
    project = create_project(db, user_id, name, initial_prompt)
    return success({"project": serialize_project(project)}, 201)


@projects_bp.route("/<project_id>", methods=["GET"])
@jwt_required_custom
def get_one_project(project_id):
    user_id = get_jwt_identity()
    db      = get_db()
    project = get_project(db, project_id, user_id)

    if not project:
        return error("Project not found", 404)

    return success({"project": serialize_project(project)})


@projects_bp.route("/<project_id>", methods=["PATCH"])
@jwt_required_custom
def update_project(project_id):
    user_id = get_jwt_identity()
    db      = get_db()
    project = get_project(db, project_id, user_id)

    if not project:
        return error("Project not found", 404)

    data    = request.get_json(silent=True) or {}
    allowed = {}

    if "name" in data:
        name = sanitize(data["name"], MAX_NAME_LEN)
        if name:
            allowed["name"] = name
    if "initial_prompt" in data:
        prompt = sanitize(data["initial_prompt"], MAX_PROMPT_LEN)
        if prompt:
            allowed["initial_prompt"] = prompt

    if not allowed:
        return error("No valid fields to update")

    update_project_field(db, project_id, allowed)
    updated = get_project(db, project_id, user_id)
    return success({"project": serialize_project(updated)})


@projects_bp.route("/<project_id>", methods=["DELETE"])
@jwt_required_custom
def remove_project(project_id):
    user_id = get_jwt_identity()
    db      = get_db()
    project = get_project(db, project_id, user_id)

    if not project:
        return error("Project not found", 404)

    delete_project(db, project_id, user_id)
    return success({"message": "Project deleted"})


@projects_bp.route("/<project_id>/workflow", methods=["GET"])
@jwt_required_custom
def get_workflow(project_id):
    user_id = get_jwt_identity()
    db      = get_db()
    project = get_project(db, project_id, user_id)

    if not project:
        return error("Project not found", 404)

    return success({"stages": project["stages"], "current_stage": project["current_stage"], "progress": project["progress"]})


@projects_bp.route("/<project_id>/versions", methods=["GET"])
@jwt_required_custom
def get_versions(project_id):
    user_id = get_jwt_identity()
    db      = get_db()
    project = get_project(db, project_id, user_id)

    if not project:
        return error("Project not found", 404)

    from app.utils.helpers import serialize_doc
    versions = get_project_versions(db, project_id)
    return success({"versions": [serialize_doc(v) for v in versions]})
