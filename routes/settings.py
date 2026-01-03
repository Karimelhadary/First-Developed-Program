"""User settings pages (Pomodoro defaults).

Also provides a small JSON endpoint used by timer.js.
"""

from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app

from utils.auth import login_required

settings_bp = Blueprint("settings_bp", __name__)


def _get_settings(user_id: str) -> dict:
    doc = current_app.settings.find_one({"user_id": user_id}) or {}
    return {
        "focus_minutes": int(doc.get("focus_minutes", 25)),
        "break_minutes": int(doc.get("break_minutes", 5)),
        "long_break_minutes": int(doc.get("long_break_minutes", 15)),
        "sessions_before_long_break": int(doc.get("sessions_before_long_break", 4)),
    }


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    user_id = session.get("user_id")

    if request.method == "POST":
        focus = int(request.form.get("focus_minutes", 25))
        brk = int(request.form.get("break_minutes", 5))
        long_brk = int(request.form.get("long_break_minutes", 15))
        n = int(request.form.get("sessions_before_long_break", 4))

        current_app.settings.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "focus_minutes": focus,
                    "break_minutes": brk,
                    "long_break_minutes": long_brk,
                    "sessions_before_long_break": n,
                }
            },
            upsert=True,
        )
        return redirect(url_for("settings_bp.settings_page"))

    return render_template("settings.html", settings=_get_settings(user_id))


@settings_bp.route("/api/settings")
@login_required
def settings_json():
    user_id = session.get("user_id")
    return jsonify(_get_settings(user_id))
