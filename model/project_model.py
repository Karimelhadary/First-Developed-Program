from __future__ import annotations

from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app


def _safe_object_id(oid: str):
    try:
        return ObjectId(oid)
    except (InvalidId, TypeError):
        return None


def _audit(user_id: str, action: str, payload: dict):
    try:
        current_app.audit_logs.insert_one(
            {"user_id": user_id, "action": action, "created_at": datetime.utcnow(), "payload": payload}
        )
    except Exception:
        pass


def list_projects(user_id: str):
    docs = list(current_app.projects.find({"user_id": user_id}).sort("name", 1))
    return [{"id": str(d["_id"]), "name": d.get("name", "")} for d in docs]


def get_project(user_id: str, project_id: str):
    oid = _safe_object_id(project_id)
    if not oid:
        return None
    doc = current_app.projects.find_one({"_id": oid, "user_id": user_id})
    return {"id": str(doc["_id"]), "name": doc.get("name", "")} if doc else None


def create_project(user_id: str, name: str) -> str:
    name = (name or "").strip()
    result = current_app.projects.insert_one({"user_id": user_id, "name": name, "created_at": datetime.utcnow()})
    _audit(user_id, "CREATE_PROJECT", {"project_id": str(result.inserted_id)})
    return str(result.inserted_id)


def update_project(user_id: str, project_id: str, name: str) -> bool:
    oid = _safe_object_id(project_id)
    if not oid:
        return False
    result = current_app.projects.update_one({"_id": oid, "user_id": user_id}, {"$set": {"name": (name or "").strip()}})
    if result.modified_count > 0:
        _audit(user_id, "UPDATE_PROJECT", {"project_id": project_id})
        return True
    return False


def delete_project(user_id: str, project_id: str) -> bool:
    oid = _safe_object_id(project_id)
    if not oid:
        return False

    current_app.tasks.update_many({"user_id": user_id, "project_id": project_id}, {"$set": {"project_id": None}})
    result = current_app.projects.delete_one({"_id": oid, "user_id": user_id})

    if result.deleted_count > 0:
        _audit(user_id, "DELETE_PROJECT", {"project_id": project_id})
        return True
    return False
