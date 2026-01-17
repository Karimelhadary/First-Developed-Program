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


def _mongo_to_task(doc):
    return {
        "id": str(doc["_id"]),
        "user_id": doc.get("user_id"),
        "project_id": doc.get("project_id"),
        "tags": doc.get("tags", []),
        "title": doc.get("title", ""),
        "description": doc.get("description", ""),
        "due_date": doc.get("due_date", ""),
        "importance": doc.get("importance", "Low"),
        "complexity": doc.get("complexity", 1),
        "energy": doc.get("energy", 1),
        "completed": doc.get("completed", False),
    }


def _audit(user_id: str, action: str, payload: dict):
    try:
        current_app.audit_logs.insert_one(
            {"user_id": user_id, "action": action, "created_at": datetime.utcnow(), "payload": payload}
        )
    except Exception:
        pass


importance_rank = {"Low": 1, "Medium": 2, "High": 3}


def get_all_tasks_sorted(user_id: str, sort_param: str):
    docs = list(current_app.tasks.find({"user_id": user_id}))

    if sort_param == "importance":
        docs.sort(key=lambda d: importance_rank.get(d.get("importance", "Low"), 0), reverse=True)
    elif sort_param == "complexity":
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    else:
        docs.sort(key=lambda d: d.get("due_date", ""))

    return [_mongo_to_task(d) for d in docs]


def get_tasks_for_dashboard(user_id: str, mood: str):
    docs = list(current_app.tasks.find({"user_id": user_id}))

    if mood == "energetic":
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    elif mood == "focused":
        docs.sort(
            key=lambda d: (importance_rank.get(d.get("importance", "Low"), 0), d.get("complexity", 1)),
            reverse=True,
        )
    elif mood == "calm":
        docs.sort(key=lambda d: d.get("complexity", 1))
    elif mood == "creative":
        docs.sort(key=lambda d: d.get("energy", 1))
    else:
        docs.sort(key=lambda d: d.get("due_date", ""))

    return [_mongo_to_task(d) for d in docs]


def get_task_by_id(user_id: str, task_id: str):
    oid = _safe_object_id(task_id)
    if not oid:
        return None
    doc = current_app.tasks.find_one({"_id": oid, "user_id": user_id})
    return _mongo_to_task(doc) if doc else None


def insert_task(user_id: str, task_data: dict):
    task_data = {**task_data, "user_id": user_id}
    result = current_app.tasks.insert_one(task_data)
    _audit(user_id, "CREATE_TASK", {"task_id": str(result.inserted_id)})
    return str(result.inserted_id)


def update_task(user_id: str, task_id: str, updates: dict) -> bool:
    oid = _safe_object_id(task_id)
    if not oid:
        return False
    result = current_app.tasks.update_one({"_id": oid, "user_id": user_id}, {"$set": updates})
    if result.modified_count > 0:
        _audit(user_id, "UPDATE_TASK", {"task_id": task_id, "updates": list(updates.keys())})
        return True
    return False


def delete_task(user_id: str, task_id: str) -> bool:
    oid = _safe_object_id(task_id)
    if not oid:
        return False
    result = current_app.tasks.delete_one({"_id": oid, "user_id": user_id})
    if result.deleted_count > 0:
        _audit(user_id, "DELETE_TASK", {"task_id": task_id})
        return True
    return False


def toggle_task_complete(user_id: str, task_id: str):
    oid = _safe_object_id(task_id)
    if not oid:
        return False

    doc = current_app.tasks.find_one({"_id": oid, "user_id": user_id})
    if not doc:
        return False

    new_value = not doc.get("completed", False)
    current_app.tasks.update_one({"_id": oid, "user_id": user_id}, {"$set": {"completed": new_value}})
    _audit(user_id, "TOGGLE_TASK", {"task_id": task_id, "completed": new_value})
    return new_value
