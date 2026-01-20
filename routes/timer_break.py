
# --- Imports used in this file (what we need from libraries/modules) ---
from __future__ import annotations

from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, current_app

from utils.auth import login_required
from model.task_model import get_all_tasks_sorted



# Blueprint groups related routes into a reusable module
timer_break_bp = Blueprint("timer_break_bp", __name__)

DEFAULT_SETTINGS = {
    "focus_minutes": 25,
    "break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_before_long_break": 4,
    "theme": "light",
}



# -------------------------------
# FUNCTION: _get_settings
# What happens here: inputs -> logic -> output/return
# -------------------------------
def _get_settings(user_id: str) -> dict:
    doc = current_app.settings.find_one({"user_id": user_id}) or {}
    out = dict(DEFAULT_SETTINGS)
    # Control-flow: starts a 'for' block (indentation shows what belongs to it).
    for k in DEFAULT_SETTINGS:
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if doc.get(k) is not None:
            out[k] = doc.get(k)
    return out


# Function: _serialize_sessions (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: _serialize_sessions
# What happens here: inputs -> logic -> output/return
# -------------------------------
def _serialize_sessions(docs):
    out = []
    # Control-flow: starts a 'for' block (indentation shows what belongs to it).
    for s in docs:
        s = dict(s)
        s["_id"] = str(s.get("_id"))
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if isinstance(s.get("created_at"), datetime):
            s["created_at"] = s["created_at"].isoformat()
        out.append(s)
    return out


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@timer_break_bp.route("/timer")
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: timer_page (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: timer_page
# What happens here: inputs -> logic -> output/return
# -------------------------------
def timer_page():
    user_id = session["user_id"]
    settings = _get_settings(user_id)

    tasks = get_all_tasks_sorted(user_id, "due_date")
    open_tasks = [t for t in tasks if not t.get("completed")]

    return render_template(
        "timer.html",
        active="timer",
        settings=settings,
        open_tasks=open_tasks,
    )


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@timer_break_bp.route("/break")
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: break_page (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: break_page
# What happens here: inputs -> logic -> output/return
# -------------------------------
def break_page():
    user_id = session["user_id"]
    settings = _get_settings(user_id)

    mode = request.args.get("mode", "break")
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if mode not in ("break", "long_break"):
        mode = "break"

    minutes = settings["long_break_minutes"] if mode == "long_break" else settings["break_minutes"]
    title = "Long break" if mode == "long_break" else "Short break"

    return render_template(
        "break.html",
        active="timer",
        settings=settings,
        break_mode=mode,
        break_minutes=minutes,
        break_title=title,
    )


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@timer_break_bp.route("/api/focus-sessions", methods=["GET"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: get_focus_sessions (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: get_focus_sessions
# What happens here: inputs -> logic -> output/return
# -------------------------------
def get_focus_sessions():
    user_id = session["user_id"]
    limit = request.args.get("limit", type=int)
    limit = 10 if not limit or limit <= 0 or limit > 100 else limit

    sessions = list(
        # MongoDB operation: read/write data in a collection
        current_app.focus_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    )
    return jsonify(_serialize_sessions(sessions))


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@timer_break_bp.route("/api/focus-sessions", methods=["POST"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: log_focus_session (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: log_focus_session
# What happens here: inputs -> logic -> output/return
# -------------------------------
def log_focus_session():
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    minutes = data.get("minutes", DEFAULT_SETTINGS["focus_minutes"])
    # Control-flow: starts a 'try:' block (indentation shows what belongs to it).
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        minutes = DEFAULT_SETTINGS["focus_minutes"]
    minutes = max(1, min(180, minutes))

    task_id = data.get("task_id") or None

    # MongoDB operation: read/write data in a collection
    current_app.focus_sessions.insert_one(
        {
            "user_id": user_id,
            "minutes": minutes,
            "task_id": task_id,
            "created_at": datetime.utcnow(),
        }
    )
    return jsonify({"ok": True})


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@timer_break_bp.route("/api/break-sessions", methods=["GET"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: get_break_sessions (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: get_break_sessions
# What happens here: inputs -> logic -> output/return
# -------------------------------
def get_break_sessions():
    user_id = session["user_id"]
    limit = request.args.get("limit", type=int)
    limit = 10 if not limit or limit <= 0 or limit > 100 else limit

    sessions = list(
        # MongoDB operation: read/write data in a collection
        current_app.break_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    )
    return jsonify(_serialize_sessions(sessions))


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@timer_break_bp.route("/api/break-sessions", methods=["POST"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: log_break_session (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: log_break_session
# What happens here: inputs -> logic -> output/return
# -------------------------------
def log_break_session():
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    minutes = data.get("minutes", DEFAULT_SETTINGS["break_minutes"])
    # Control-flow: starts a 'try:' block (indentation shows what belongs to it).
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        minutes = DEFAULT_SETTINGS["break_minutes"]
    minutes = max(1, min(90, minutes))

    mode = data.get("mode")
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if mode not in ("break", "long_break"):
        mode = "break"

    # MongoDB operation: read/write data in a collection
    current_app.break_sessions.insert_one(
        {
            "user_id": user_id,
            "minutes": minutes,
            "mode": mode,
            "created_at": datetime.utcnow(),
        }
    )
    return jsonify({"ok": True})
