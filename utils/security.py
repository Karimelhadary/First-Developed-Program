import os
import hashlib
import binascii
from flask import current_app

# SALT length in bytes
SALT_LEN = 16

def hash_password(password: str) -> dict:
    """
    Hash password using SHA256 + salt + pepper.
    Returns dict: {"salt": ..., "hash": ...}
    """

    # Generate a random salt
    salt = os.urandom(SALT_LEN)

    # Pepper (global secret)
    pepper = current_app.config.get("PEPPER", "")

    # Combine password + salt + pepper
    pwd = password.encode("utf-8")
    combined = salt + pwd + pepper.encode("utf-8")

    hashed = hashlib.sha256(combined).digest()

    return {
        "salt": binascii.hexlify(salt).decode(),
        "hash": binascii.hexlify(hashed).decode()
    }


def verify_password(password: str, salt_hex: str, stored_hash: str) -> bool:
    """
    Check if password matches stored hash.
    """
    pepper = current_app.config.get("PEPPER", "")
    salt = binascii.unhexlify(salt_hex)

    combined = salt + password.encode("utf-8") + pepper.encode("utf-8")
    check_hash = hashlib.sha256(combined).digest()

    return binascii.hexlify(check_hash).decode() == stored_hash
