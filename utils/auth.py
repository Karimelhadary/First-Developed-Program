
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
#This code makes sure that only logged-in users can open certain pages.
#If you’re not logged in → it sends you to the login page.
# -------------------------------
def login_required(view_func: Callable[..., Any]):
    """Redirect to /login if the user is not logged in."""

    # Decorator:A decorator = something you put on top of a route to add extra behavior.
    @wraps(view_func)
# Function: wrapper (reads input, applies logic, returns response/value)

    # -------------------------------
    # FUNCTION: wrapper
    # What happens here:This function blocks access to a page if the user is not logged in and redirects them to the login page.
    # -------------------------------
    def wrapper(*args, **kwargs):
        #This function accepts any arguments because it can wrap any page function.
        if not session.get("user_id"):
            # remember where user wanted to go, Save the URL the user tried to open.
            next_url = request.path
            return redirect(url_for("login_bp.login", next=next_url))
        return view_func(*args, **kwargs)
        #Everything is fine — run the real page function

    return wrapper
