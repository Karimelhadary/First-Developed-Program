from __future__ import annotations

from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, current_app

from utils.auth import login_required
from model.task_model import get_all_tasks_sorted

timer_break_bp = Blueprint("timer_break_bp", __name__)

DEFAULT_SETTINGS = {
    "focus_minutes": 25,
    "break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_before_long_break": 4,
    "theme": "light",
}


def _get_settings(user_id: str) -> dict:
    doc = current_app.settings.find_one({"user_id": user_id}) or {}
    out = dict(DEFAULT_SETTINGS)
    for k in DEFAULT_SETTINGS:
        if doc.get(k) is not None:
            out[k] = doc.get(k)
    return out


def _serialize_sessions(docs):
    out = []
    for s in docs:
        s = dict(s)
        s["_id"] = str(s.get("_id"))
        if isinstance(s.get("created_at"), datetime):
            s["created_at"] = s["created_at"].isoformat()
        out.append(s)
    return out


@timer_break_bp.route("/timer")
@login_required
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


@timer_break_bp.route("/break")
@login_required
def break_page():
    user_id = session["user_id"]
    settings = _get_settings(user_id)

    mode = request.args.get("mode", "break")
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


@timer_break_bp.route("/api/focus-sessions", methods=["GET"])
@login_required
def get_focus_sessions():
    user_id = session["user_id"]
    limit = request.args.get("limit", type=int)
    limit = 10 if not limit or limit <= 0 or limit > 100 else limit

    sessions = list(
        current_app.focus_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    )
    return jsonify(_serialize_sessions(sessions))


@timer_break_bp.route("/api/focus-sessions", methods=["POST"])
@login_required
def log_focus_session():
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    minutes = data.get("minutes", DEFAULT_SETTINGS["focus_minutes"])
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        minutes = DEFAULT_SETTINGS["focus_minutes"]
    minutes = max(1, min(180, minutes))

    task_id = data.get("task_id") or None

    current_app.focus_sessions.insert_one(
        {
            "user_id": user_id,
            "minutes": minutes,
            "task_id": task_id,
            "created_at": datetime.utcnow(),
        }
    )
    return jsonify({"ok": True})


@timer_break_bp.route("/api/break-sessions", methods=["GET"])
@login_required
def get_break_sessions():
    user_id = session["user_id"]
    limit = request.args.get("limit", type=int)
    limit = 10 if not limit or limit <= 0 or limit > 100 else limit

    sessions = list(
        current_app.break_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    )
    return jsonify(_serialize_sessions(sessions))


@timer_break_bp.route("/api/break-sessions", methods=["POST"])
@login_required
def log_break_session():
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    minutes = data.get("minutes", DEFAULT_SETTINGS["break_minutes"])
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        minutes = DEFAULT_SETTINGS["break_minutes"]
    minutes = max(1, min(90, minutes))

    mode = data.get("mode")
    if mode not in ("break", "long_break"):
        mode = "break"

    current_app.break_sessions.insert_one(
        {
            "user_id": user_id,
            "minutes": minutes,
            "mode": mode,
            "created_at": datetime.utcnow(),
        }
    )
    return jsonify({"ok": True})
