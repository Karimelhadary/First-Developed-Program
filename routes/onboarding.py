
# Unused import (likely a mistake, 'If' is not used in this file)
from ast import If
# Import Flask components: Blueprint for routes, render_template for HTML, request for form data, redirect for redirects, url_for for URLs, current_app for app context, session for user data
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
# Import datetime for timestamping mood logs
from datetime import datetime
# Import login_required to protect the route
from utils.auth import login_required


# Create Blueprint for onboarding routes
onboarding_bp = Blueprint("onboarding_bp", __name__)


# Route for onboarding page, handles GET (show form) and POST (process mood selection)
@onboarding_bp.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding():
    # Check if request is POST (form submission)
    if request.method == "POST":
        # Get mood from form, default to "focused" if missing
        mood = request.form.get("mood", "focused")

        # Insert mood log into MongoDB moods collection
        current_app.moods.insert_one(
            {
                "user_id": session.get("user_id"),  # Associate with current user
                "mood": mood,  # The selected mood
                "created_at": datetime.utcnow(),  # Timestamp in UTC
            }
        )

        # Store mood in session for later use (e.g., on dashboard)
        session["current_mood"] = mood

        # Redirect to dashboard after saving
        return redirect(url_for("dashboard_bp.dashboard"))

    # For GET request, render the onboarding form
    return render_template("onboarding.html")
