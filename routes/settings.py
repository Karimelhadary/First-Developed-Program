

# --- Imports used in this file (what we need from libraries/modules) ---
from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app, flash
from utils.auth import login_required



# Blueprint groups related routes into a reusable module
settings_bp = Blueprint("settings_bp", __name__)

DEFAULTS = {
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
    out = dict(DEFAULTS)
    # Control-flow: starts a 'for' block (indentation shows what belongs to it).
    for k in DEFAULTS:
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if doc.get(k) is not None:
            out[k] = doc.get(k)
    return out


# Function: _save_settings (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: _save_settings
# What happens here: inputs -> logic -> output/return
# -------------------------------
def _save_settings(user_id: str, updates: dict):
    # MongoDB operation: read/write data in a collection
    current_app.settings.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, **updates}},
        upsert=True,
    )


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@settings_bp.route("/settings", methods=["GET", "POST"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: settings_page (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: settings_page
# What happens here: inputs -> logic -> output/return
# -------------------------------
def settings_page():
    user_id = session["user_id"]

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if request.method == "POST":
        # Control-flow: starts a 'try:' block (indentation shows what belongs to it).
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
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
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


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@settings_bp.route("/api/settings", methods=["GET"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: api_get_settings (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: api_get_settings
# What happens here: inputs -> logic -> output/return
# -------------------------------
def api_get_settings():
    return jsonify(_get_settings(session["user_id"]))


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@settings_bp.route("/api/settings", methods=["POST"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: api_settings (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: api_settings
# What happens here: inputs -> logic -> output/return
# -------------------------------
def api_settings():
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}

    updates = {}

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if "theme" in data:
        theme = data.get("theme")
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if theme not in ("light", "dark"):
            return jsonify({"ok": False, "error": "invalid_theme"}), 400
        updates["theme"] = theme

    for key, (mn, mx) in {
        "focus_minutes": (1, 180),
        "break_minutes": (1, 60),
        "long_break_minutes": (1, 90),
        "sessions_before_long_break": (1, 12),
    }.items():
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if key in data:
            # Control-flow: starts a 'try:' block (indentation shows what belongs to it).
            try:
                val = int(data.get(key))
            except (TypeError, ValueError):
                return jsonify({"ok": False, "error": f"invalid_{key}"}), 400
            updates[key] = max(mn, min(mx, val))

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not updates:
        return jsonify({"ok": False, "error": "no_updates"}), 400

    _save_settings(user_id, updates)
    return jsonify({"ok": True})
