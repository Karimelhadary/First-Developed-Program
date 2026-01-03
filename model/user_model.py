from flask import current_app
from utils.security import hash_password, verify_password


def create_user(name: str, email: str, password: str):
    """
    Insert a new user with salted+peppered hash.
    """
    email = email.lower().strip()

    hashed = hash_password(password)

    user = {
        "name": name.strip() or "User",
        "email": email,
        "password_hash": hashed["hash"],
        "salt": hashed["salt"],
    }

    result = current_app.users.insert_one(user)
    user_id = str(result.inserted_id)

    # Create default settings for this user (pomodoro defaults)
    current_app.settings.update_one(
        {"user_id": user_id},
        {
            "$setOnInsert": {
                "user_id": user_id,
                "focus_minutes": 25,
                "break_minutes": 5,
                "long_break_minutes": 15,
                "sessions_before_long_break": 4,
            }
        },
        upsert=True,
    )

    # Create a "Personal" project so tasks can be grouped immediately
    current_app.projects.update_one(
        {"user_id": user_id, "name": "Personal"},
        {
            "$setOnInsert": {
                "user_id": user_id,
                "name": "Personal",
                "created_at": None,
            }
        },
        upsert=True,
    )

    return user_id


def find_user_by_email(email: str):
    email = email.lower().strip()
    return current_app.users.find_one({"email": email})


def verify_user(email: str, password: str) -> bool:
    """
    Verify user credentials.

    Supports:
    - NEW users: with `salt` + `password_hash` (hashed & peppered)
    - OLD users (before security update): with plain `password` field
      (so the app doesn't crash with KeyError)
    """
    user = find_user_by_email(email)
    if not user:
        return False

    # --- New style: hashed password with salt+pepper ---
    if "salt" in user and "password_hash" in user:
        return verify_password(
            password,
            salt_hex=user["salt"],
            stored_hash=user["password_hash"],
        )

    # --- Legacy style: plain-text password (old accounts) ---
    # This is just here so your project doesn't crash on old data.
    # New accounts created via /register will NOT use this anymore.
    if "password" in user:
        return user["password"] == password

    # If neither format is present, fail safely
    return False
