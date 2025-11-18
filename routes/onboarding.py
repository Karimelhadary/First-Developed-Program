from flask import Blueprint, render_template, request, redirect, url_for

onboarding_bp = Blueprint("onboarding_bp", __name__)

@onboarding_bp.route("/onboarding", methods=["GET", "POST"])
@onboarding_bp.route("/onboarding.html", methods=["GET", "POST"])
def onboarding():
    if request.method == "POST":
        mood = request.form.get("mood", "focused")
        return redirect(url_for("dashboard_bp.dashboard", mood=mood))
    
    selected_mood = request.args.get("mood", "focused")
    return render_template("/templates/onboarding.html", selected_mood=selected_mood)
