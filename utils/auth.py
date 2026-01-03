"""Authentication helpers.

This project uses a simple session-based login system.
We store the logged-in user's id in session["user_id"].
"""

from __future__ import annotations

from functools import wraps
from typing import Callable, Any

from flask import session, redirect, url_for, request


def login_required(view_func: Callable[..., Any]):
    """Redirect to /login if the user is not logged in."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            # remember where user wanted to go
            next_url = request.path
            return redirect(url_for("login_bp.login", next=next_url))
        return view_func(*args, **kwargs)

    return wrapper
