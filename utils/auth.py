
"""Authentication helpers.

This project uses a simple session-based login system.
We store the logged-in user's id in session["user_id"].
"""

# --- Imports used in this file (what we need from libraries/modules) ---
from __future__ import annotations

from functools import wraps
from typing import Callable, Any

from flask import session, redirect, url_for, request


# Function: login_required (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: login_required
# What happens here: inputs -> logic -> output/return
# -------------------------------
def login_required(view_func: Callable[..., Any]):
    """Redirect to /login if the user is not logged in."""

    # Decorator: modifies the function below (commonly registers a route in Flask)
    @wraps(view_func)
# Function: wrapper (reads input, applies logic, returns response/value)

    # -------------------------------
    # FUNCTION: wrapper
    # What happens here: inputs -> logic -> output/return
    # -------------------------------
    def wrapper(*args, **kwargs):
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if not session.get("user_id"):
            # remember where user wanted to go
            next_url = request.path
            return redirect(url_for("login_bp.login", next=next_url))
        return view_func(*args, **kwargs)

    return wrapper
