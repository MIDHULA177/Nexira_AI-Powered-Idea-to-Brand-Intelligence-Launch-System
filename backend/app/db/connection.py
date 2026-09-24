import os
from datetime import datetime, timezone

import bcrypt
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure


_client = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI environment variable is not set")
        _client = MongoClient(uri)
        _client.admin.command("ping")
        _db = _client[os.getenv("MONGODB_DB_NAME", "nexira")]
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db):
    db.users.create_index("email", unique=True)

    db.projects.create_index("user_id")
    db.projects.create_index("status")
    db.projects.create_index([("user_id", ASCENDING), ("updated_at", DESCENDING)])

    db.project_versions.create_index([("project_id", ASCENDING), ("version_number", ASCENDING)])

    db.agent_runs.create_index([("project_id", ASCENDING), ("created_at", DESCENDING)])
    db.agent_runs.create_index([("project_id", ASCENDING), ("stage", ASCENDING)])
    db.agent_runs.create_index([("project_id", ASCENDING), ("status", ASCENDING)])


def init_default_admin():
    db = get_db()
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@nexira.com")

    existing = db.users.find_one({"email": admin_email})
    if existing:
        return

    password = os.getenv("DEFAULT_ADMIN_PASSWORD", "nexira_admin_2024")
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    now = datetime.now(timezone.utc)
    db.users.insert_one({
        "first_name": os.getenv("DEFAULT_ADMIN_FIRST_NAME", "Nexira"),
        "last_name": os.getenv("DEFAULT_ADMIN_LAST_NAME", "Admin"),
        "email": admin_email,
        "password_hash": password_hash,
        "role": "admin",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
    })
    print(f"[NEXIRA] Default admin created: {admin_email}")
