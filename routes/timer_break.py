"""Focus timer + break pages.

Fixes the original logic issues:
... (full file)
"""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, render_template, jsonify, request, session, current_app

from utils.auth import login_required

timer_break_bp = Blueprint("timer_break_bp", __name__)


@timer_break_bp.route("/timer")
@login_required
def timer():
    """Timer UI page. The actual countdown is handled by static/timer.js."""
    return render_template("timer.html")


@timer_break_bp.route("/break")
@login_required
def break_page():
    """Break UI page (also uses JS for countdown)."""
    return render_template("break.html")


@timer_break_bp.route("/api/focus-sessions", methods=["POST"])
@login_required
def api_log_focus_session():
    """Log a completed focus session.

    Expected JSON:
    {
      "minutes": 25,
      "mode": "focus",
      "task_id": "..." (optional)
    }
    """
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}
    minutes = int(data.get("minutes", 25))
    mode = data.get("mode", "focus")
    task_id = data.get("task_id")

    current_app.focus_sessions.insert_one(
        {
            "user_id": user_id,
            "minutes": minutes,
            "mode": mode,
            "task_id": task_id,
            "created_at": datetime.utcnow(),
        }
    )

    return jsonify({"ok": True})


@timer_break_bp.route("/api/break-sessions", methods=["POST"])
@login_required
def api_log_break_session():
    """Log a completed break session."""
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}
    minutes = int(data.get("minutes", 5))
    mode = data.get("mode", "break")

    current_app.break_sessions.insert_one(
        {
            "user_id": user_id,
            "minutes": minutes,
            "mode": mode,
            "created_at": datetime.utcnow(),
        }
    )
    return jsonify({"ok": True})


@timer_break_bp.route("/api/focus-sessions", methods=["GET"])
@login_required
def api_list_focus_sessions():
    """Return last 10 focus sessions for the current user."""
    user_id = session.get("user_id")
    docs = list(
        current_app.focus_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(10)
    )
    out = []
    for d in docs:
        out.append(
            {
                "minutes": int(d.get("minutes", 0)),
                "mode": d.get("mode", "focus"),
                "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
            }
        )
    return jsonify(out)
