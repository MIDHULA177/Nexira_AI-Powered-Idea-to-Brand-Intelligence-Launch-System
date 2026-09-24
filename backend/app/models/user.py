from datetime import datetime, timezone
from bson import ObjectId
import bcrypt


def serialize_user(user, include_sensitive=False):
    if not user:
        return None
    result = {
        "id": str(user["_id"]),
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "role": user["role"],
        "is_active": user["is_active"],
        "created_at": user["created_at"].isoformat() if user.get("created_at") else None,
        "last_login_at": user["last_login_at"].isoformat() if user.get("last_login_at") else None,
    }
    return result


def create_user(db, first_name, last_name, email, password, role="user"):
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    now = datetime.now(timezone.utc)
    user = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "role": role,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
    }
    result = db.users.insert_one(user)
    user["_id"] = result.inserted_id
    return user


def verify_password(user, password):
    return bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))


def find_user_by_email(db, email):
    return db.users.find_one({"email": email.lower().strip()})


def find_user_by_id(db, user_id):
    try:
        return db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def update_last_login(db, user_id):
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"last_login_at": datetime.now(timezone.utc)}}
    )


def update_user_role(db, user_id, role):
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": role, "updated_at": datetime.now(timezone.utc)}}
    )


def get_all_users(db):
    return list(db.users.find({}, {"password_hash": 0}))
