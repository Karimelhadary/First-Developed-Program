
# Import annotations for type hints
from __future__ import annotations

# Import datetime for handling dates and times
from datetime import datetime
# Import ObjectId for MongoDB document IDs
from bson import ObjectId
# Import InvalidId exception for handling invalid ObjectId strings
from bson.errors import InvalidId
# Import current_app to access the Flask application context and database
from flask import current_app




# Define a helper function to safely convert a string to ObjectId, returning None if invalid
def _safe_object_id(oid: str):
    # Try to create an ObjectId from the string
    try:
        return ObjectId(oid)
    # If the string is invalid or not a string, catch exceptions and return None
    except (InvalidId, TypeError):
        return None


# Define a helper function to convert a MongoDB document to a task dictionary
def _mongo_to_task(doc):
    # Return a dictionary with task fields extracted from the document
    return {
        "id": str(doc["_id"]),  # Convert ObjectId to string
        "user_id": doc.get("user_id"),  # Get user_id field
        "project_id": doc.get("project_id"),  # Get project_id field
        "tags": doc.get("tags", []),  # Get tags list, default empty
        "title": doc.get("title", ""),  # Get title, default empty string
        "description": doc.get("description", ""),  # Get description, default empty
        "due_date": doc.get("due_date", ""),  # Get due_date, default empty
        "importance": doc.get("importance", "Low"),  # Get importance, default Low
        "complexity": doc.get("complexity", 1),  # Get complexity, default 1
        "energy": doc.get("energy", 1),  # Get energy, default 1
        "completed": doc.get("completed", False),  # Get completed status, default False
    }


# Define a helper function to log audit actions
def _audit(user_id: str, action: str, payload: dict):
    # Try to insert an audit log entry into the database
    try:
        # Insert a document into audit_logs collection with user_id, action, timestamp, and payload
        current_app.audit_logs.insert_one(
            {"user_id": user_id, "action": action, "created_at": datetime.utcnow(), "payload": payload}
        )
    # If there's an exception, pass silently
    except Exception:
        pass


importance_rank = {"Low": 1, "Medium": 2, "High": 3}


# Define a function to get all tasks for a user, sorted by a parameter, optionally filtered by project
def get_all_tasks_sorted(user_id: str, sort_param: str, project_id: str | None = None):
    # Start with a query to find tasks for the user
    query = {"user_id": user_id}
    # If a project_id is provided, add it to the query
    if project_id:
        # If project_id is "__none__", filter for tasks with no project
        if project_id == "__none__":
            query["project_id"] = None
        else:
            # Otherwise, filter for tasks in that project
            query["project_id"] = project_id

    # Find all matching documents in the tasks collection
    docs = list(current_app.tasks.find(query))

    # Sort the documents based on the sort_param
    if sort_param == "importance":
        # Sort by importance rank descending
        docs.sort(key=lambda d: importance_rank.get(d.get("importance", "Low"), 0), reverse=True)
    elif sort_param == "complexity":
        # Sort by complexity descending
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    else:
        # Default sort by due_date ascending
        docs.sort(key=lambda d: d.get("due_date", ""))

    # Convert each document to a task dict and return the list
    return [_mongo_to_task(d) for d in docs]


# Define a function to get tasks for dashboard based on mood
def get_tasks_for_dashboard(user_id: str, mood: str):
    # Find all tasks for the user
    docs = list(current_app.tasks.find({"user_id": user_id}))

    # Sort tasks based on mood
    if mood == "energetic":
        # Sort by complexity descending for high-energy tasks
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    elif mood == "focused":
        # Sort by importance then complexity descending
        docs.sort(
            key=lambda d: (importance_rank.get(d.get("importance", "Low"), 0), d.get("complexity", 1)),
            reverse=True,
        )
    elif mood == "calm":
        # Sort by complexity ascending for easier tasks
        docs.sort(key=lambda d: d.get("complexity", 1))
    elif mood == "creative":
        # Sort by energy ascending for creative tasks
        docs.sort(key=lambda d: d.get("energy", 1))
    else:
        # Default sort by due_date
        docs.sort(key=lambda d: d.get("due_date", ""))

    # Convert documents to task dicts and return
    return [_mongo_to_task(d) for d in docs]


# Define a function to get a single task by ID for a user
def get_task_by_id(user_id: str, task_id: str):
    # Convert task_id to ObjectId safely
    oid = _safe_object_id(task_id)
    # If invalid, return None
    if not oid:
        return None
    # Find the task document
    doc = current_app.tasks.find_one({"_id": oid, "user_id": user_id})
    # Return task dict if found, else None
    return _mongo_to_task(doc) if doc else None


# Define a function to insert a new task
def insert_task(user_id: str, task_data: dict):
    # Add user_id to the task data
    task_data = {**task_data, "user_id": user_id}
    # Insert the task into the database
    result = current_app.tasks.insert_one(task_data)
    # Log the creation audit
    _audit(user_id, "CREATE_TASK", {"task_id": str(result.inserted_id)})
    # Return the new task's ID
    return str(result.inserted_id)



# -------------------------------
# FUNCTION: update_task
#“This function safely updates a task in the database, ensures it belongs to the user, 
# logs the update, and returns whether the update was successful.”
# -------------------------------
def update_task(user_id: str, task_id: str, updates: dict) -> bool:
    # Convert task_id to ObjectId safely
    oid = _safe_object_id(task_id)
    # If invalid, return False
    if not oid:
        return False
    # Update the task document with the provided updates
    result = current_app.tasks.update_one({"_id": oid, "user_id": user_id}, {"$set": updates})
    # If modified, log audit and return True
    if result.modified_count > 0:
        _audit(user_id, "UPDATE_TASK", {"task_id": task_id, "updates": list(updates.keys())})
        return True
    # Otherwise, return False
    return False

#You convert string → Mongo ObjectId when:
#you want to search / update / delete something in MongoDB
#You convert Mongo ObjectId → string when:
#you want to send data to templates, JSON, or URLs

# -------------------------------
# FUNCTION: delete_task
# What happens here: inputs -> logic -> output/return
# -------------------------------
def delete_task(user_id: str, task_id: str) -> bool:
    # Convert task_id to ObjectId safely
    oid = _safe_object_id(task_id)
    # If invalid, return False
    if not oid:
        return False
    # Delete the task document
    result = current_app.tasks.delete_one({"_id": oid, "user_id": user_id})
    # If deleted, log audit and return True
    if result.deleted_count > 0:
        _audit(user_id, "DELETE_TASK", {"task_id": task_id})
        return True
    # Otherwise, return False
    return False


# Function: toggle_task_complete (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: toggle_task_complete
# What happens here: inputs -> logic -> output/return
# -------------------------------
def toggle_task_complete(user_id: str, task_id: str):
    # Convert task_id to ObjectId safely
    oid = _safe_object_id(task_id)
    # If invalid, return False
    if not oid:
        return False

    # Find the task document
    doc = current_app.tasks.find_one({"_id": oid, "user_id": user_id})
    # If not found, return False
    if not doc:
        return False

    # Flip the completed status
    new_value = not doc.get("completed", False)
    # Update the task with the new completed value
    current_app.tasks.update_one({"_id": oid, "user_id": user_id}, {"$set": {"completed": new_value}})
    # Log the toggle audit
    _audit(user_id, "TOGGLE_TASK", {"task_id": task_id, "completed": new_value})
    # Return the new value
    return new_value
