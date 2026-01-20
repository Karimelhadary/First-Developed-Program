
# Import annotations for type hints from future (for Python 3.7+ compatibility)
from __future__ import annotations

# Import datetime class to handle date and time operations
from datetime import datetime
# Import ObjectId for MongoDB document IDs
from bson import ObjectId
# Import InvalidId exception for handling invalid ObjectId strings
from bson.errors import InvalidId
# Import current_app from Flask to access the application context and database
from flask import current_app

# Define a helper function to safely convert a string to ObjectId, returning None if invalid
def _safe_object_id(oid: str):
    # Try to create an ObjectId from the string
    try:
        return ObjectId(oid)
    # If the string is invalid or not a string, catch the exceptions and return None
    except (InvalidId, TypeError):
        return None

# Define a helper function to log audit actions to the database
def _audit(user_id: str, action: str, payload: dict):
    # Try to insert an audit log entry
    try:
        # Insert a document into the audit_logs collection with user_id, action, timestamp, and payload
        current_app.audit_logs.insert_one(
            {"user_id": user_id, "action": action, "created_at": datetime.utcnow(), "payload": payload}
        )
    # If there's any exception (e.g., database error), silently pass (fail gracefully)
    except Exception:
        pass

# Define a function to list all projects for a user
def list_projects(user_id: str):
    # Find all projects for the user, sorted by name ascending
    docs = list(current_app.projects.find({"user_id": user_id}).sort("name", 1))
    # Return a list of dictionaries with id and name for each project
    return [{"id": str(d["_id"]), "name": d.get("name", "")} for d in docs]

# Define a function to get a specific project by ID for a user
def get_project(user_id: str, project_id: str):
    # Convert the project_id string to ObjectId safely
    oid = _safe_object_id(project_id)
    # If conversion failed, return None
    if not oid:
        return None
    # Find the project document matching the ID and user
    doc = current_app.projects.find_one({"_id": oid, "user_id": user_id})
    # If found, return a dict with id and name; else None
    return {"id": str(doc["_id"]), "name": doc.get("name", "")} if doc else None

# Define a function to create a new project
def create_project(user_id: str, name: str) -> str:
    # Strip whitespace from the name and default to empty string if None
    name = (name or "").strip()
    # Insert a new project document into the database
    result = current_app.projects.insert_one({"user_id": user_id, "name": name, "created_at": datetime.utcnow()})
    # Log the creation action in audit logs
    _audit(user_id, "CREATE_PROJECT", {"project_id": str(result.inserted_id)})
    # Return the string representation of the new project's ID
    return str(result.inserted_id)

# Define a function to update an existing project
def update_project(user_id: str, project_id: str, name: str) -> bool:
    # Convert project_id to ObjectId safely
    oid = _safe_object_id(project_id)
    # If invalid, return False
    if not oid:
        return False
    # Update the project document with the new name
    result = current_app.projects.update_one({"_id": oid, "user_id": user_id}, {"$set": {"name": (name or "").strip()}})
    # If at least one document was modified, log the update and return True
    if result.modified_count > 0:
        _audit(user_id, "UPDATE_PROJECT", {"project_id": project_id})
        return True
    # Otherwise, return False (no update happened)
    return False

# Define a function to delete a project
def delete_project(user_id: str, project_id: str) -> bool:
    # Convert project_id to ObjectId safely
    oid = _safe_object_id(project_id)
    # If invalid, return False
    if not oid:
        return False

    # Remove the project_id from all tasks associated with this project
    current_app.tasks.update_many({"user_id": user_id, "project_id": project_id}, {"$set": {"project_id": None}})
    # Delete the project document
    result = current_app.projects.delete_one({"_id": oid, "user_id": user_id})

    # If a document was deleted, log the deletion and return True
    if result.deleted_count > 0:
        _audit(user_id, "DELETE_PROJECT", {"project_id": project_id})
        return True
    # Otherwise, return False
    return False
