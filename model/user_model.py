# Import current_app from Flask to access the application context, which provides access to database collections like users, settings, and projects
from flask import current_app
# Import hash_password and verify_password functions from the utils.security module for secure password hashing and verification
from utils.security import hash_password, verify_password




# Function definition for create_user: takes name, email, and password as strings, creates a new user in the database
def create_user(name: str, email: str, password: str):
    """
    Insert a new user with salted+peppered hash.
    """
    # Normalize the email by converting to lowercase and stripping whitespace to ensure consistency
    email = email.lower().strip()

    # Hash the password using the security utility, which returns a dictionary with 'hash' and 'salt'
    hashed = hash_password(password)

    # Create a user dictionary with the processed name, email, hashed password, and salt
    user = {
        "name": name.strip() or "User",  # Strip name and default to "User" if empty
        "email": email,  # Use the normalized email
        "password_hash": hashed["hash"],  # Store the hashed password
        "salt": hashed["salt"],  # Store the salt used for hashing
    }

    # Insert the user document into the MongoDB 'users' collection and get the result
    result = current_app.users.insert_one(user)
    # Convert the inserted ObjectId to string for the user ID
    user_id = str(result.inserted_id)

    # Insert default Pomodoro settings for the new user into the 'settings' collection
    # Uses update_one with upsert=True to insert only if no document exists for this user_id
    current_app.settings.update_one(
        {"user_id": user_id},  # Filter by user_id
        {
            "$setOnInsert": {  # Only set these fields on insert (not update)
                "user_id": user_id,  # Reference to the user
                "focus_minutes": 25,  # Default focus time in minutes
                "break_minutes": 5,  # Default short break time
                "long_break_minutes": 15,  # Default long break time
                "sessions_before_long_break": 4,  # Sessions before a long break
            }
        },
        upsert=True,  # Insert if no matching document found
    )

    # Create a default "Personal" project for the user to group tasks
    # Uses update_one with upsert=True to avoid duplicates
    current_app.projects.update_one(
        {"user_id": user_id, "name": "Personal"},  # Filter by user_id and name
        {
            "$setOnInsert": {  # Only set on insert
                "user_id": user_id,  # User reference
                "name": "Personal",  # Project name
                "created_at": None,  # Placeholder for creation time (could be datetime.now())
            }
        },
        upsert=True,  # Insert if not exists
    )

    # Return the string representation of the new user's ID
    return user_id


# Function definition for find_user_by_email: takes email as string, returns user document or None
def find_user_by_email(email: str):
    # Normalize the email to lowercase and strip whitespace
    email = email.lower().strip()
    # Query the 'users' collection for a document with matching email
    return current_app.users.find_one({"email": email})



# Function definition for verify_user: takes email and password, returns True if credentials are valid, False otherwise
def verify_user(email: str, password: str) -> bool:
    """
    Verify user credentials.

    Supports:
    - NEW users: with `salt` + `password_hash` (hashed & peppered)
    - OLD users (before security update): with plain `password` field
      (so the app doesn't crash with KeyError)
    """
    # Retrieve the user document by email
    user = find_user_by_email(email)
    # If no user found, return False
    if not user:
        return False

    # Check if the user has the new-style hashed password fields
    if "salt" in user and "password_hash" in user:
        # Verify the provided password against the stored hash and salt
        return verify_password(
            password,  # The plain password input
            salt_hex=user["salt"],  # The salt as hex string
            stored_hash=user["password_hash"],  # The stored hash
        )

    # Fallback for legacy users with plain-text passwords (for backward compatibility)
    if "password" in user:
        # Direct comparison of plain text (not secure, but maintains compatibility)
        return user["password"] == password

    # If neither password format is present, return False
    return False
