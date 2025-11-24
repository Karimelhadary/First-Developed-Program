from flask import Blueprint, render_template
from routes.data import tasks

insights_bp = Blueprint("insights_bp", __name__)

@insights_bp.route("/insights")
@insights_bp.route("/insights.html")
def insights():
    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    focus_time = "1h 25m"  # placeholder

    return render_template(
        "insights.html",
        total_tasks=total,
        completed_tasks=completed,
        focus_time=focus_time,
    )
