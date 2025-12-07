from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from datetime import datetime

onboarding_bp = Blueprint("onboarding_bp", __name__)


@onboarding_bp.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    if request.method == "POST":
        mood = request.form.get("mood", "focused")

        # Save mood into MongoDB
        current_app.moods.insert_one(
            {
                "user_id": session.get("user_id"),   # may be None if not logged in
                "mood": mood,
                "created_at": datetime.utcnow(),
            }
        )

        # Also store in session so we can reuse it on dashboard if we want
        session["current_mood"] = mood

        return redirect(url_for("dashboard_bp.dashboard"))

    # GET request -> show the form
    return render_template("onboarding.html")
