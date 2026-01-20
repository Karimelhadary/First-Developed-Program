

"""Tag model.

Tags are reusable labels (Study, Work, etc.). They improve UI filtering and
help satisfy the multiple-collections requirement with a real use case.
"""

from __future__ import annotations

from datetime import datetime
from flask import current_app


# Function: ensure_tags_exist (reads input, applies logic, returns response/value)
def ensure_tags_exist(user_id: str, tag_names: list[str]):
    """Create tags if they don't exist. Idempotent."""
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
# MongoDB operation: read/write data in a collection
        current_app.tags.update_one(
            {"user_id": user_id, "name": name},
            {"$setOnInsert": {"user_id": user_id, "name": name, "created_at": datetime.utcnow()}},
            upsert=True,
        )


# Function: list_tags (reads input, applies logic, returns response/value)
def list_tags(user_id: str):
# MongoDB operation: read/write data in a collection
    docs = list(current_app.tags.find({"user_id": user_id}).sort("name", 1))
    return [d.get("name", "") for d in docs]
