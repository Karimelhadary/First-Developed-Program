
# This module contains authentication helpers
# The project uses a simple session-based login system
# The logged-in user's id is stored in session["user_id"]

# Enable future annotations for type hints
from __future__ import annotations

# Import wraps from functools to preserve function metadata in decorators
from functools import wraps
# Import Callable and Any for type hints
from typing import Callable, Any

# Import session for storing user data, redirect for redirects, url_for for URLs, request for current request
from flask import session, redirect, url_for, request

# Define a decorator function that requires login
def login_required(view_func: Callable[..., Any]):
    # Docstring: Redirect to /login if the user is not logged in
    """Redirect to /login if the user is not logged in."""

    # Use wraps to preserve the original function's metadata
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Check if user_id is in session; if not, redirect to login
        if not session.get("user_id"):
            # Save the current path as next URL for post-login redirect
            next_url = request.path
            # Redirect to login page with next parameter
            return redirect(url_for("login_bp.login", next=next_url))
        # If logged in, call the original view function
        return view_func(*args, **kwargs)

    # Return the wrapper function
    return wrapper
