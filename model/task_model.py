from flask import current_app
from bson import ObjectId


# ---------- helpers ----------

def _mongo_to_task(doc):
    """Convert a MongoDB document to a simple dict usable in templates."""
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "description": doc.get("description", ""),
        "due_date": doc.get("due_date", ""),
        "importance": doc.get("importance", "Low"),
        "complexity": doc.get("complexity", 1),
        "energy": doc.get("energy", 1),
        "completed": doc.get("completed", False),
    }


importance_rank = {"Low": 1, "Medium": 2, "High": 3}


# ---------- list / sorting ----------

def get_all_tasks_sorted(sort_param: str):
    """
    Return all tasks as a list of dicts, sorted according to sort_param.

    sort_param in {"due_date", "importance", "complexity"}.
    """
    docs = list(current_app.tasks.find())

    if sort_param == "importance":
        # High -> Medium -> Low
        docs.sort(
            key=lambda d: importance_rank.get(d.get("importance", "Low"), 0),
            reverse=True,
        )
    elif sort_param == "complexity":
        # 5 -> 1
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    else:
        # due_date: earliest -> latest
        docs.sort(key=lambda d: d.get("due_date", ""))

    return [_mongo_to_task(d) for d in docs]


def get_tasks_for_dashboard(mood: str):
    """
    Return tasks sorted based on the user's mood.

    energetic -> most complex first
    focused   -> high importance & complex first
    calm      -> easiest first
    creative  -> lowest "energy" first
    default   -> by due date
    """
    docs = list(current_app.tasks.find())

    if mood == "energetic":
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    elif mood == "focused":
        docs.sort(
            key=lambda d: (
                importance_rank.get(d.get("importance", "Low"), 0),
                d.get("complexity", 1),
            ),
            reverse=True,
        )
    elif mood == "calm":
        docs.sort(key=lambda d: d.get("complexity", 1))
    elif mood == "creative":
        docs.sort(key=lambda d: d.get("energy", 1))
    else:
        docs.sort(key=lambda d: d.get("due_date", ""))

    return [_mongo_to_task(d) for d in docs]


# ---------- single-task operations ----------

def get_task_by_id(task_id: str):
    doc = current_app.tasks.find_one({"_id": ObjectId(task_id)})
    if not doc:
        return None
    return _mongo_to_task(doc)


def insert_task(task_data: dict):
    """Insert a new task. task_data is a plain dict with fields."""
    result = current_app.tasks.insert_one(task_data)
    return str(result.inserted_id)


def update_task(task_id: str, updates: dict) -> bool:
    result = current_app.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": updates},
    )
    return result.modified_count > 0


def delete_task(task_id: str) -> bool:
    result = current_app.tasks.delete_one({"_id": ObjectId(task_id)})
    return result.deleted_count > 0


def toggle_task_complete(task_id: str) -> bool:
    """Flip completed True/False and return the new value."""
    doc = current_app.tasks.find_one({"_id": ObjectId(task_id)})
    if not doc:
        return False

    new_value = not doc.get("completed", False)

    current_app.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"completed": new_value}},
    )
    return new_value
