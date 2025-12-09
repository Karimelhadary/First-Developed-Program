from flask import current_app
from utils.security import hash_password, verify_password


def create_user(email: str, password: str):
    """
    Insert a new user with salted+peppered hash.
    """
    email = email.lower().strip()

    hashed = hash_password(password)

    user = {
        "email": email,
        "password_hash": hashed["hash"],
        "salt": hashed["salt"],
    }

    result = current_app.users.insert_one(user)
    return str(result.inserted_id)


def find_user_by_email(email: str):
    email = email.lower().strip()
    return current_app.users.find_one({"email": email})


def verify_user(email: str, password: str) -> bool:
    user = find_user_by_email(email)
    if not user:
        return False

    return verify_password(
        password,
        salt_hex=user["salt"],
        stored_hash=user["password_hash"],
    )
