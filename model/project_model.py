
# --- Imports used in this file (what we need from libraries/modules) ---
from __future__ import annotations

from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app




# Function: _safe_object_id (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: _safe_object_id
# What happens here: inputs -> logic -> output/return
# -------------------------------
def _safe_object_id(oid: str):
    # Control-flow: starts a 'try:' block (indentation shows what belongs to it).
    try:
        return ObjectId(oid)
    except (InvalidId, TypeError):
        return None


# Function: _audit (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: _audit
# What happens here: inputs -> logic -> output/return
# -------------------------------
def _audit(user_id: str, action: str, payload: dict):
    # Control-flow: starts a 'try:' block (indentation shows what belongs to it).
    try:
        # MongoDB operation: read/write data in a collection
        current_app.audit_logs.insert_one(
            {"user_id": user_id, "action": action, "created_at": datetime.utcnow(), "payload": payload}
        )
    except Exception:
        pass


# Function: list_projects (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: list_projects
# What happens here: inputs -> logic -> output/return
# -------------------------------
def list_projects(user_id: str):
    # MongoDB operation: read/write data in a collection
    docs = list(current_app.projects.find({"user_id": user_id}).sort("name", 1))
    return [{"id": str(d["_id"]), "name": d.get("name", "")} for d in docs]


# Function: get_project (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: get_project
# What happens here: inputs -> logic -> output/return
# -------------------------------
def get_project(user_id: str, project_id: str):
    oid = _safe_object_id(project_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not oid:
        return None
    doc = current_app.projects.find_one({"_id": oid, "user_id": user_id})
    return {"id": str(doc["_id"]), "name": doc.get("name", "")} if doc else None



# -------------------------------
# FUNCTION: create_project
# What happens here: inputs -> logic -> output/return
# -------------------------------
def create_project(user_id: str, name: str) -> str:
    name = (name or "").strip()
    # MongoDB operation: read/write data in a collection
    result = current_app.projects.insert_one({"user_id": user_id, "name": name, "created_at": datetime.utcnow()})
    _audit(user_id, "CREATE_PROJECT", {"project_id": str(result.inserted_id)})
    return str(result.inserted_id)



# -------------------------------
# FUNCTION: update_project
# What happens here: inputs -> logic -> output/return
# -------------------------------
def update_project(user_id: str, project_id: str, name: str) -> bool:
    oid = _safe_object_id(project_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not oid:
        return False
    # MongoDB operation: read/write data in a collection
    result = current_app.projects.update_one({"_id": oid, "user_id": user_id}, {"$set": {"name": (name or "").strip()}})
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if result.modified_count > 0:
        _audit(user_id, "UPDATE_PROJECT", {"project_id": project_id})
        return True
    return False



# -------------------------------
# FUNCTION: delete_project
# What happens here: inputs -> logic -> output/return
# -------------------------------
def delete_project(user_id: str, project_id: str) -> bool:
    oid = _safe_object_id(project_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not oid:
        return False

    current_app.tasks.update_many({"user_id": user_id, "project_id": project_id}, {"$set": {"project_id": None}})
    # MongoDB operation: read/write data in a collection
    result = current_app.projects.delete_one({"_id": oid, "user_id": user_id})

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if result.deleted_count > 0:
        _audit(user_id, "DELETE_PROJECT", {"project_id": project_id})
        return True
    return False
