

# Enable future annotations for type hinting
from __future__ import annotations

# Import Flask components: Blueprint for routes, render_template for HTML, request for form/JSON data, redirect for redirects, url_for for URLs, session for user data, jsonify for JSON responses, current_app for app context, flash for messages
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app, flash
# Import login_required decorator
from utils.auth import login_required



# Create Blueprint for settings routes
settings_bp = Blueprint("settings_bp", __name__)

# Define default settings values
DEFAULTS = {
    "focus_minutes": 25,
    "break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_before_long_break": 4,
    "theme": "light",
}



# Function to retrieve user settings, merging with defaults
def _get_settings(user_id: str) -> dict:
    # Fetch settings document from database, or empty dict if none
    doc = current_app.settings.find_one({"user_id": user_id}) or {}
    # Start with defaults
    out = dict(DEFAULTS)
    # Override defaults with user-specific values if present
    for k in DEFAULTS:
        if doc.get(k) is not None:
            out[k] = doc.get(k)
    return out


# Function to save settings updates to database
def _save_settings(user_id: str, updates: dict):
    # Update settings document, creating if it doesn't exist
    current_app.settings.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, **updates}},
        upsert=True,
    )


# Route for settings page, handles GET (show form) and POST (save settings)
@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    # Get user ID from session
    user_id = session["user_id"]

    # Handle POST request (form submission)
    if request.method == "POST":
        # Parse and validate timer settings from form
        try:
            focus = int(request.form.get("focus_minutes", DEFAULTS["focus_minutes"]))
            brk = int(request.form.get("break_minutes", DEFAULTS["break_minutes"]))
            longb = int(request.form.get("long_break_minutes", DEFAULTS["long_break_minutes"]))
            cycles = int(
                request.form.get("sessions_before_long_break", DEFAULTS["sessions_before_long_break"])
            )
        except (TypeError, ValueError):
            # Flash error message for invalid input
            flash("Please enter valid numbers for timer settings.", "danger")
            return redirect(url_for("settings_bp.settings_page"))

        # Get theme from form, default to light
        theme = request.form.get("theme", "light")
        if theme not in ("light", "dark"):
            theme = "light"

        # Prepare updates with clamped values
        updates = {
            "focus_minutes": max(1, min(180, focus)),
            "break_minutes": max(1, min(60, brk)),
            "long_break_minutes": max(1, min(90, longb)),
            "sessions_before_long_break": max(1, min(12, cycles)),
            "theme": theme,
        }
        # Save updates
        _save_settings(user_id, updates)
        # Flash success message
        flash("Settings saved.", "success")
        return redirect(url_for("settings_bp.settings_page"))

    # For GET, retrieve settings and render template
    settings = _get_settings(user_id)
    return render_template("settings.html", active="settings", settings=settings)


# API route to get settings as JSON
@settings_bp.route("/api/settings", methods=["GET"])
@login_required
def api_get_settings():
    # Return settings as JSON
    return jsonify(_get_settings(session["user_id"]))


# API route to update settings via JSON POST
@settings_bp.route("/api/settings", methods=["POST"])
@login_required
def api_settings():
    # Get user ID
    user_id = session["user_id"]
    # Parse JSON data from request
    data = request.get_json(silent=True) or {}

    # Prepare updates dictionary
    updates = {}

    # Handle theme update
    if "theme" in data:
        theme = data.get("theme")
        if theme not in ("light", "dark"):
            return jsonify({"ok": False, "error": "invalid_theme"}), 400
        updates["theme"] = theme

    # Handle timer settings with validation and clamping
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

    # If no updates, return error
    if not updates:
        return jsonify({"ok": False, "error": "no_updates"}), 400

    # Save updates
    _save_settings(user_id, updates)
    # Return success
    return jsonify({"ok": True})
