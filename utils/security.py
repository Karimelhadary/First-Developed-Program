
# Import os for generating random salts
import os
# Import hashlib for SHA256 hashing
import hashlib
# Import binascii for hex encoding/decoding
import binascii
# Import current_app to access Flask app config for pepper
from flask import current_app

# Define the length of the salt in bytes
SALT_LEN = 16

# Function to hash a password with salt and pepper
def hash_password(password: str) -> dict:
    # Docstring: Hash password using SHA256 + salt + pepper. Returns dict with salt and hash
    """
    Hash password using SHA256 + salt + pepper.
    Returns dict: {"salt": ..., "hash": ...}
    """

    # Generate a random salt of SALT_LEN bytes
    salt = os.urandom(SALT_LEN)

    # Get the pepper from app config, default to empty string
    pepper = current_app.config.get("PEPPER", "")

    # Encode password to bytes
    pwd = password.encode("utf-8")
    # Combine salt + password + pepper
    combined = salt + pwd + pepper.encode("utf-8")

    # Hash the combined bytes with SHA256
    hashed = hashlib.sha256(combined).digest()

    # Return dict with hex-encoded salt and hash
    return {
        "salt": binascii.hexlify(salt).decode(),
        "hash": binascii.hexlify(hashed).decode()
    }

# Function to verify a password against stored salt and hash
def verify_password(password: str, salt_hex: str, stored_hash: str) -> bool:
    # Docstring: Check if password matches stored hash
    """
    Check if password matches stored hash.
    """
    # Get the pepper from app config
    pepper = current_app.config.get("PEPPER", "")
    # Decode the hex salt back to bytes
    salt = binascii.unhexlify(salt_hex)

    # Combine salt + password + pepper, same as during hashing
    combined = salt + password.encode("utf-8") + pepper.encode("utf-8")
    # Hash the combined bytes
    check_hash = hashlib.sha256(combined).digest()

    # Compare the computed hash with the stored hash
    return binascii.hexlify(check_hash).decode() == stored_hash
