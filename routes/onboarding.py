

# --- Imports used in this file (what we need from libraries/modules) ---
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from datetime import datetime
from utils.auth import login_required


# Blueprint groups related routes into a reusable module
onboarding_bp = Blueprint("onboarding_bp", __name__)


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@onboarding_bp.route("/onboarding", methods=["GET", "POST"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: onboarding (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: onboarding
# What happens here: inputs -> logic -> output/return
# -------------------------------
def onboarding():
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if request.method == "POST":
        mood = request.form.get("mood", "focused")

        # Save mood into MongoDB
        # MongoDB operation: read/write data in a collection
        current_app.moods.insert_one(
            {
                "user_id": session.get("user_id"),
                "mood": mood,
                "created_at": datetime.utcnow(),
            }
        )

        # Also store in session so we can reuse it on dashboard if we want
        session["current_mood"] = mood

        return redirect(url_for("dashboard_bp.dashboard"))

    # GET request -> show the form
    return render_template("onboarding.html")
