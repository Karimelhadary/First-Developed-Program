
# This is the tag model module
# Tags are reusable labels like "Study", "Work", etc.
# They improve UI filtering and help with multiple collections requirement

# Import annotations for type hints
from __future__ import annotations

# Import datetime for timestamps
from datetime import datetime
# Import current_app to access Flask app and database
from flask import current_app


# Define a function to ensure that tags exist for a user, creating them if they don't
def ensure_tags_exist(user_id: str, tag_names: list[str]):
    # Docstring: Create tags if they don't exist. This operation is idempotent (can be run multiple times safely)
    """Create tags if they don't exist. Idempotent."""
    # Loop through each tag name in the list
    for name in tag_names:
        # Strip whitespace from the name
        name = name.strip()
        # If the name is empty after stripping, skip it
        if not name:
            continue
        # Use update_one with upsert=True to create the tag if it doesn't exist
        # Look for a tag with this user_id and name
        # If it exists, do nothing; if not, create it with setOnInsert
        current_app.tags.update_one(
            {"user_id": user_id, "name": name},
            {"$setOnInsert": {"user_id": user_id, "name": name, "created_at": datetime.utcnow()}},
            upsert=True,
        )


# Define a function to list all tags for a user
def list_tags(user_id: str):
    # This function returns the user's tags sorted alphabetically as a simple list of names
    # From the tags collection, get all documents where user_id matches, sorted by name ascending
    docs = list(current_app.tags.find({"user_id": user_id}).sort("name", 1))
    # From each document, extract the name field and return a list of strings
    return [d.get("name", "") for d in docs]
