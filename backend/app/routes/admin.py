from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.auth.decorators import admin_required
from app.db.connection import get_db
from app.models.user import get_all_users, update_user_role, serialize_user, find_user_by_id
from app.utils.helpers import success, error

admin_bp = Blueprint("admin", __name__)

VALID_ROLES = {"user", "admin"}


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    db    = get_db()
    users = get_all_users(db)
    return success({"users": [serialize_user(u) for u in users]})


@admin_bp.route("/users/<user_id>/role", methods=["PATCH"])
@admin_required
def change_role(user_id):
    requesting_admin_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    role = data.get("role", "").strip().lower()

    if role not in VALID_ROLES:
        return error(f"Role must be one of: {', '.join(sorted(VALID_ROLES))}")

    db   = get_db()
    user = find_user_by_id(db, user_id)

    if not user:
        return error("User not found", 404)

    if str(user["_id"]) == requesting_admin_id:
        return error("You cannot change your own role")

    update_user_role(db, user_id, role)
    updated = find_user_by_id(db, user_id)
    return success({"user": serialize_user(updated)})
