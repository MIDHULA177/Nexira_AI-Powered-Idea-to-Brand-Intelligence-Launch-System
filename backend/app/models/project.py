from datetime import datetime, timezone
from bson import ObjectId

STAGE_ORDER = ["discovery", "positioning", "shape", "visualize", "challenge", "consistency", "launch"]

STAGE_DEPENDENCIES = {
    "discovery":    [],
    "positioning":  ["discovery"],
    "shape":        ["discovery", "positioning"],
    "visualize":    ["discovery", "positioning", "shape"],
    "challenge":    ["discovery", "positioning", "shape", "visualize"],
    "consistency":  ["discovery", "positioning", "shape", "visualize", "challenge"],
    "launch":       ["discovery", "positioning", "shape", "visualize", "challenge", "consistency"],
}

DOWNSTREAM_STAGES = {
    "discovery":   ["positioning", "shape", "visualize", "challenge", "consistency", "launch"],
    "positioning": ["shape", "visualize", "challenge", "consistency", "launch"],
    "shape":       ["visualize", "challenge", "consistency", "launch"],
    "visualize":   ["challenge", "consistency", "launch"],
    "challenge":   ["consistency", "launch"],
    "consistency": ["launch"],
    "launch":      [],
}


def _empty_stage(status="locked"):
    return {
        "status": status,
        "version": 0,
        "data": None,
        "generated_at": None,
        "approved_at": None,
        "source": None,
        "approved_by": None,
    }


def create_project(db, user_id, name, initial_prompt):
    now = datetime.now(timezone.utc)
    project = {
        "user_id": ObjectId(user_id),
        "name": name.strip(),
        "initial_prompt": initial_prompt.strip(),
        "status": "draft",
        "current_stage": "discovery",
        "progress": 0,
        "stages": {
            "discovery":   {**_empty_stage("available")},
            "positioning": {**_empty_stage("locked")},
            "shape":       {**_empty_stage("locked")},
            "visualize":   {**_empty_stage("locked")},
            "challenge":   {**_empty_stage("locked")},
            "consistency": {**_empty_stage("locked")},
            "launch":      {**_empty_stage("locked")},
        },
        "created_at": now,
        "updated_at": now,
    }
    result = db.projects.insert_one(project)
    project["_id"] = result.inserted_id
    _save_version(db, project, "project_created", user_id)
    return project


def get_project(db, project_id, user_id):
    try:
        project = db.projects.find_one({
            "_id": ObjectId(project_id),
            "user_id": ObjectId(user_id)
        })
        return project
    except Exception:
        return None


def get_user_projects(db, user_id):
    return list(db.projects.find(
        {"user_id": ObjectId(user_id)},
        sort=[("updated_at", -1)]
    ))


def update_project_field(db, project_id, fields: dict):
    fields["updated_at"] = datetime.now(timezone.utc)
    db.projects.update_one({"_id": ObjectId(project_id)}, {"$set": fields})


def set_stage_status(db, project_id, stage, status):
    """Set a stage to an arbitrary status (e.g. generating, available, outdated)."""
    db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {
            f"stages.{stage}.status": status,
            "updated_at": datetime.now(timezone.utc),
        }}
    )


def save_stage_result(db, project_id, stage, data, source="ai"):
    now = datetime.now(timezone.utc)
    project = db.projects.find_one({"_id": ObjectId(project_id)})
    current_version = project["stages"][stage].get("version", 0)

    db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {
            f"stages.{stage}.status": "review",
            f"stages.{stage}.data": data,
            f"stages.{stage}.version": current_version + 1,
            f"stages.{stage}.generated_at": now,
            f"stages.{stage}.approved_at": None,
            f"stages.{stage}.source": source,
            "updated_at": now,
        }}
    )


def restore_stage_on_failure(db, project_id, stage):
    """
    Called when LLM generation fails after setting status to 'generating'.
    Restores the stage to its previous usable status so the user can retry.
    Per README §49: failed operations must not leave the stage in a broken state.
    """
    project = db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        return
    stage_doc = project["stages"].get(stage, {})
    # If it was generating with existing data -> back to review
    # If it was generating with no data -> back to available
    restore_status = "review" if stage_doc.get("data") else "available"
    db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {
            f"stages.{stage}.status": restore_status,
            "updated_at": datetime.now(timezone.utc),
        }}
    )


def approve_stage(db, project_id, stage, user_id):
    now = datetime.now(timezone.utc)
    project = db.projects.find_one({"_id": ObjectId(project_id)})

    next_stage_index = STAGE_ORDER.index(stage) + 1
    next_stage = STAGE_ORDER[next_stage_index] if next_stage_index < len(STAGE_ORDER) else None

    approved_count = sum(
        1 for s in STAGE_ORDER
        if project["stages"][s]["status"] == "approved" or s == stage
    )
    progress = int((approved_count / len(STAGE_ORDER)) * 100)

    updates = {
        f"stages.{stage}.status": "approved",
        f"stages.{stage}.approved_at": now,
        f"stages.{stage}.approved_by": str(user_id),
        "progress": progress,
        "updated_at": now,
    }

    if next_stage:
        updates[f"stages.{next_stage}.status"] = "available"
        updates["current_stage"] = next_stage

    # README §54: finalized trigger when all stages approved (progress == 100)
    if progress == 100:
        updates["status"] = "completed"
        updates["current_stage"] = "launch"
    else:
        updates["status"] = "in_progress"

    db.projects.update_one({"_id": ObjectId(project_id)}, {"$set": updates})

    updated = db.projects.find_one({"_id": ObjectId(project_id)})
    trigger = "finalized" if progress == 100 else f"{stage}_approved"
    _save_version(db, updated, trigger, user_id)


def mark_downstream_outdated(db, project_id, changed_stage):
    downstream = DOWNSTREAM_STAGES.get(changed_stage, [])
    now = datetime.now(timezone.utc)
    updates = {"updated_at": now}
    for stage in downstream:
        updates[f"stages.{stage}.status"] = "outdated"
    if updates:
        db.projects.update_one({"_id": ObjectId(project_id)}, {"$set": updates})


def edit_stage(db, project_id, stage, data, user_id):
    now = datetime.now(timezone.utc)
    project = db.projects.find_one({"_id": ObjectId(project_id)})
    current_version = project["stages"][stage].get("version", 0)

    db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {
            f"stages.{stage}.data": data,
            f"stages.{stage}.source": "user_edited",
            f"stages.{stage}.version": current_version + 1,
            f"stages.{stage}.status": "review",
            "updated_at": now,
        }}
    )
    mark_downstream_outdated(db, project_id, stage)
    updated = db.projects.find_one({"_id": ObjectId(project_id)})
    _save_version(db, updated, "manual_edit", user_id)


def delete_project(db, project_id, user_id):
    db.projects.delete_one({"_id": ObjectId(project_id), "user_id": ObjectId(user_id)})
    db.project_versions.delete_many({"project_id": ObjectId(project_id)})
    db.agent_runs.delete_many({"project_id": ObjectId(project_id)})


def _save_version(db, project, trigger, user_id):
    last = db.project_versions.find_one(
        {"project_id": project["_id"]},
        sort=[("version_number", -1)]
    )
    version_number = (last["version_number"] + 1) if last else 1

    snapshot = {stage: project["stages"].get(stage, {}) for stage in STAGE_ORDER}

    db.project_versions.insert_one({
        "project_id": project["_id"],
        "version_number": version_number,
        "trigger": trigger,
        "snapshot": snapshot,
        "created_by": {"type": "user", "user_id": str(user_id)},
        "created_at": datetime.now(timezone.utc),
    })


def get_project_versions(db, project_id):
    return list(db.project_versions.find(
        {"project_id": ObjectId(project_id)},
        sort=[("version_number", -1)]
    ))


def serialize_project(project):
    if not project:
        return None
    p = dict(project)
    p["id"] = str(p.pop("_id"))
    p["user_id"] = str(p["user_id"])
    for stage in STAGE_ORDER:
        stage_data = p["stages"].get(stage, {})
        if stage_data.get("approved_by"):
            stage_data["approved_by"] = str(stage_data["approved_by"])
    if p.get("created_at"):
        p["created_at"] = p["created_at"].isoformat()
    if p.get("updated_at"):
        p["updated_at"] = p["updated_at"].isoformat()
    return p
