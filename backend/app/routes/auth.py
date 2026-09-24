from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from app.db.connection import get_db
from app.models.user import (
    create_user, find_user_by_email, find_user_by_id,
    verify_password, update_last_login, serialize_user
)
from app.auth.decorators import jwt_required_custom
from app.utils.helpers import success, error, sanitize
import re

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    first_name = sanitize(data.get("first_name", ""), 80)
    last_name  = sanitize(data.get("last_name", ""), 80)
    email      = sanitize(data.get("email", ""), 254).lower()
    password   = data.get("password", "")

    if not all([first_name, last_name, email, password]):
        return error("first_name, last_name, email and password are required")

    if not EMAIL_RE.match(email):
        return error("Invalid email address")

    if len(password) < 6:
        return error("Password must be at least 6 characters")

    if len(password) > 128:
        return error("Password must be 128 characters or fewer")

    db = get_db()

    if find_user_by_email(db, email):
        return error("An account with this email already exists", 409)

    user = create_user(db, first_name, last_name, email, password)
    token = create_access_token(identity=str(user["_id"]))

    return success({"user": serialize_user(user), "token": token}, 201)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return error("Email and password are required")

    db   = get_db()
    user = find_user_by_email(db, email)

    if not user or not verify_password(user, password):
        return error("Invalid email or password", 401)

    if not user.get("is_active"):
        return error("Account is inactive", 403)

    update_last_login(db, str(user["_id"]))
    token = create_access_token(identity=str(user["_id"]))

    return success({"user": serialize_user(user), "token": token})


@auth_bp.route("/me", methods=["GET"])
@jwt_required_custom
def me():
    user_id = get_jwt_identity()
    db      = get_db()
    user    = find_user_by_id(db, user_id)

    if not user:
        return error("User not found", 404)

    return success({"user": serialize_user(user)})
