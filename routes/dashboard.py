from flask import Blueprint, render_template, request
from routes.data import tasks


dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/dashboard")
@dashboard_bp.route("/dashboard.html")
def dashboard():
    mood = request.args.get("mood", "focused")
    return render_template("/templates/dashboard.html", tasks=tasks, mood=mood)
