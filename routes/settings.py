from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app, flash
from utils.auth import login_required

settings_bp = Blueprint("settings_bp", __name__)

DEFAULTS = {
    "focus_minutes": 25,
    "break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_before_long_break": 4,
    "theme": "light",
}


def _get_settings(user_id: str) -> dict:
    doc = current_app.settings.find_one({"user_id": user_id}) or {}
    out = dict(DEFAULTS)
    for k in DEFAULTS:
        if doc.get(k) is not None:
            out[k] = doc.get(k)
    return out


def _save_settings(user_id: str, updates: dict):
    current_app.settings.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, **updates}},
        upsert=True,
    )


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    user_id = session["user_id"]

    if request.method == "POST":
        try:
            focus = int(request.form.get("focus_minutes", DEFAULTS["focus_minutes"]))
            brk = int(request.form.get("break_minutes", DEFAULTS["break_minutes"]))
            longb = int(request.form.get("long_break_minutes", DEFAULTS["long_break_minutes"]))
            cycles = int(
                request.form.get("sessions_before_long_break", DEFAULTS["sessions_before_long_break"])
            )
        except (TypeError, ValueError):
            flash("Please enter valid numbers for timer settings.", "danger")
            return redirect(url_for("settings_bp.settings_page"))

        theme = request.form.get("theme", "light")
        if theme not in ("light", "dark"):
            theme = "light"

        updates = {
            "focus_minutes": max(1, min(180, focus)),
            "break_minutes": max(1, min(60, brk)),
            "long_break_minutes": max(1, min(90, longb)),
            "sessions_before_long_break": max(1, min(12, cycles)),
            "theme": theme,
        }
        _save_settings(user_id, updates)
        flash("Settings saved.", "success")
        return redirect(url_for("settings_bp.settings_page"))

    settings = _get_settings(user_id)
    return render_template("settings.html", active="settings", settings=settings)


@settings_bp.route("/api/settings", methods=["GET"])
@login_required
def api_get_settings():
    return jsonify(_get_settings(session["user_id"]))


@settings_bp.route("/api/settings", methods=["POST"])
@login_required
def api_settings():
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    updates = {}

    if "theme" in data:
        theme = data.get("theme")
        if theme not in ("light", "dark"):
            return jsonify({"ok": False, "error": "invalid_theme"}), 400
        updates["theme"] = theme

    for key, (mn, mx) in {
        "focus_minutes": (1, 180),
        "break_minutes": (1, 60),
        "long_break_minutes": (1, 90),
        "sessions_before_long_break": (1, 12),
    }.items():
        if key in data:
            try:
                val = int(data.get(key))
            except (TypeError, ValueError):
                return jsonify({"ok": False, "error": f"invalid_{key}"}), 400
            updates[key] = max(mn, min(mx, val))

    if not updates:
        return jsonify({"ok": False, "error": "no_updates"}), 400

    _save_settings(user_id, updates)
    return jsonify({"ok": True})
