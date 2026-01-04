from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app, flash

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
    current_app.settings.update_one({"user_id": user_id}, {"$set": {"user_id": user_id, **updates}}, upsert=True)

@settings_bp.route("/settings", methods=["GET", "POST"])
def settings_page():
    if "user_id" not in session:
        return redirect(url_for("login_bp.login"))
    user_id = session["user_id"]

    if request.method == "POST":
        try:
            focus = int(request.form.get("focus_minutes", DEFAULTS["focus_minutes"]))
            brk = int(request.form.get("break_minutes", DEFAULTS["break_minutes"]))
            longb = int(request.form.get("long_break_minutes", DEFAULTS["long_break_minutes"]))
            cycles = int(request.form.get("sessions_before_long_break", DEFAULTS["sessions_before_long_break"]))
        except ValueError:
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

@settings_bp.route("/api/settings", methods=["POST"])
def api_settings():
    if "user_id" not in session:
        return jsonify({"error": "not_logged_in"}), 401
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}
    theme = data.get("theme")
    if theme not in ("light", "dark"):
        return jsonify({"ok": False, "error": "invalid_theme"}), 400
    _save_settings(user_id, {"theme": theme})
    return jsonify({"ok": True})
