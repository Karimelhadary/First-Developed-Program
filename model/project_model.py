"""Project model.

Projects help group tasks and provide additional CRUD pages/collections
for the rubric. Each project belongs to a user.
"""

from __future__ import annotations

from datetime import datetime
from bson import ObjectId
from flask import current_app


def list_projects(user_id: str):
    docs = list(current_app.projects.find({"user_id": user_id}).sort("name", 1))
    return [{"id": str(d["_id"]), "name": d.get("name", "")} for d in docs]


def get_project(user_id: str, project_id: str):
    doc = current_app.projects.find_one({"_id": ObjectId(project_id), "user_id": user_id})
    if not doc:
        return None
    return {"id": str(doc["_id"]), "name": doc.get("name", "")}


def create_project(user_id: str, name: str) -> str:
    name = name.strip()
    result = current_app.projects.insert_one(
        {"user_id": user_id, "name": name, "created_at": datetime.utcnow()}
    )
    current_app.audit_logs.insert_one(
        {
            "user_id": user_id,
            "action": "CREATE_PROJECT",
            "created_at": datetime.utcnow(),
            "payload": {"project_id": str(result.inserted_id)},
        }
    )
    return str(result.inserted_id)


def update_project(user_id: str, project_id: str, name: str) -> bool:
    result = current_app.projects.update_one(
        {"_id": ObjectId(project_id), "user_id": user_id},
        {"$set": {"name": name.strip()}},
    )
    return result.modified_count > 0


def delete_project(user_id: str, project_id: str) -> bool:
    # Optional safety: unassign tasks that reference this project
    current_app.tasks.update_many(
        {"user_id": user_id, "project_id": project_id},
        {"$set": {"project_id": None}},
    )
    result = current_app.projects.delete_one({"_id": ObjectId(project_id), "user_id": user_id})
    return result.deleted_count > 0
