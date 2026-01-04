from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from datetime import datetime
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
    doc = current_app.db["settings"].find_one({"user_id": user_id}) or {}
    settings = {**DEFAULT_SETTINGS, **{k: doc.get(k) for k in DEFAULT_SETTINGS.keys() if doc.get(k) is not None}}
    return settings

@timer_break_bp.route("/timer")
def timer_page():
    if "user_id" not in session:
        return redirect(url_for("login_bp.login"))

    user_id = session["user_id"]
    settings = _get_settings(user_id)

    # open tasks for dropdown
    tasks = get_all_tasks_sorted(user_id, "due_date")
    open_tasks = [t for t in tasks if not t.get("completed")]

    return render_template("timer.html", active="timer", settings=settings, open_tasks=open_tasks)

@timer_break_bp.route("/break")
def break_page():
    if "user_id" not in session:
        return redirect(url_for("login_bp.login"))
    return render_template("break.html", active="timer")

@timer_break_bp.route("/api/focus-sessions", methods=["GET"])
def get_focus_sessions():
    if "user_id" not in session:
        return jsonify({"error": "not_logged_in"}), 401
    user_id = session["user_id"]
    sessions = list(current_app.db["focus_sessions"].find({"user_id": user_id}).sort("created_at", -1))
    for s in sessions:
        s["_id"] = str(s["_id"])
        if "created_at" in s and isinstance(s["created_at"], datetime):
            s["created_at"] = s["created_at"].isoformat()
    return jsonify(sessions)

@timer_break_bp.route("/api/focus-sessions", methods=["POST"])
def log_focus_session():
    if "user_id" not in session:
        return jsonify({"error": "not_logged_in"}), 401

    data = request.get_json(silent=True) or {}
    minutes = int(data.get("minutes", DEFAULT_SETTINGS["focus_minutes"]))
    task_id = data.get("task_id") or None

    doc = {
        "user_id": session["user_id"],
        "minutes": minutes,
        "task_id": task_id,
        "created_at": datetime.utcnow(),
    }
    current_app.db["focus_sessions"].insert_one(doc)
    return jsonify({"ok": True})

@timer_break_bp.route("/api/break-sessions", methods=["GET"])
def get_break_sessions():
    if "user_id" not in session:
        return jsonify({"error": "not_logged_in"}), 401
    user_id = session["user_id"]
    sessions = list(current_app.db["break_sessions"].find({"user_id": user_id}).sort("created_at", -1))
    for s in sessions:
        s["_id"] = str(s["_id"])
        if "created_at" in s and isinstance(s["created_at"], datetime):
            s["created_at"] = s["created_at"].isoformat()
    return jsonify(sessions)

@timer_break_bp.route("/api/break-sessions", methods=["POST"])
def log_break_session():
    if "user_id" not in session:
        return jsonify({"error": "not_logged_in"}), 401

    data = request.get_json(silent=True) or {}
    minutes = int(data.get("minutes", DEFAULT_SETTINGS["break_minutes"]))

    doc = {
        "user_id": session["user_id"],
        "minutes": minutes,
        "created_at": datetime.utcnow(),
    }
    current_app.db["break_sessions"].insert_one(doc)
    return jsonify({"ok": True})
