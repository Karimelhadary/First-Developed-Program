
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


# Function: _mongo_to_task (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: _mongo_to_task
# What happens here: inputs -> logic -> output/return
# -------------------------------
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


importance_rank = {"Low": 1, "Medium": 2, "High": 3}


# Function: get_all_tasks_sorted (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: get_all_tasks_sorted
# What happens here: inputs -> logic -> output/return
# -------------------------------
def get_all_tasks_sorted(user_id: str, sort_param: str, project_id: str | None = None):
    query = {"user_id": user_id}
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if project_id:
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if project_id == "__none__":
            query["project_id"] = None
        else:
            query["project_id"] = project_id

    # MongoDB operation: read/write data in a collection
    docs = list(current_app.tasks.find(query))

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if sort_param == "importance":
        docs.sort(key=lambda d: importance_rank.get(d.get("importance", "Low"), 0), reverse=True)
    elif sort_param == "complexity":
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    else:
        docs.sort(key=lambda d: d.get("due_date", ""))

    return [_mongo_to_task(d) for d in docs]


# Function: get_tasks_for_dashboard (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: get_tasks_for_dashboard
# What happens here: inputs -> logic -> output/return
# -------------------------------
def get_tasks_for_dashboard(user_id: str, mood: str):
    # MongoDB operation: read/write data in a collection
    docs = list(current_app.tasks.find({"user_id": user_id}))

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
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


# Function: get_task_by_id (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: get_task_by_id
# What happens here: inputs -> logic -> output/return
# -------------------------------
def get_task_by_id(user_id: str, task_id: str):
    oid = _safe_object_id(task_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not oid:
        return None
    doc = current_app.tasks.find_one({"_id": oid, "user_id": user_id})
    return _mongo_to_task(doc) if doc else None


# Function: insert_task (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: insert_task
# What happens here: inputs -> logic -> output/return
# -------------------------------
def insert_task(user_id: str, task_data: dict):
    task_data = {**task_data, "user_id": user_id}
    # MongoDB operation: read/write data in a collection
    result = current_app.tasks.insert_one(task_data)
    _audit(user_id, "CREATE_TASK", {"task_id": str(result.inserted_id)})
    return str(result.inserted_id)



# -------------------------------
# FUNCTION: update_task
# What happens here: inputs -> logic -> output/return
# -------------------------------
def update_task(user_id: str, task_id: str, updates: dict) -> bool:
    oid = _safe_object_id(task_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not oid:
        return False
    # MongoDB operation: read/write data in a collection
    result = current_app.tasks.update_one({"_id": oid, "user_id": user_id}, {"$set": updates})
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if result.modified_count > 0:
        _audit(user_id, "UPDATE_TASK", {"task_id": task_id, "updates": list(updates.keys())})
        return True
    return False



# -------------------------------
# FUNCTION: delete_task
# What happens here: inputs -> logic -> output/return
# -------------------------------
def delete_task(user_id: str, task_id: str) -> bool:
    oid = _safe_object_id(task_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not oid:
        return False
    # MongoDB operation: read/write data in a collection
    result = current_app.tasks.delete_one({"_id": oid, "user_id": user_id})
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if result.deleted_count > 0:
        _audit(user_id, "DELETE_TASK", {"task_id": task_id})
        return True
    return False


# Function: toggle_task_complete (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: toggle_task_complete
# What happens here: inputs -> logic -> output/return
# -------------------------------
def toggle_task_complete(user_id: str, task_id: str):
    oid = _safe_object_id(task_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not oid:
        return False

    doc = current_app.tasks.find_one({"_id": oid, "user_id": user_id})
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not doc:
        return False

    new_value = not doc.get("completed", False)
    # MongoDB operation: read/write data in a collection
    current_app.tasks.update_one({"_id": oid, "user_id": user_id}, {"$set": {"completed": new_value}})
    _audit(user_id, "TOGGLE_TASK", {"task_id": task_id, "completed": new_value})
    return new_value
