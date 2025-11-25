from flask import Blueprint, render_template, current_app

insights_bp = Blueprint("insights_bp", __name__)

@insights_bp.route("/insights")
def insights():
    total = current_app.tasks.count_documents({})
    completed = current_app.tasks.count_documents({"completed": True})
    remaining = max(total - completed, 0)

    # for now this is just a placeholder string,
    # you could compute real focus time later
    focus_time = "1h 25m"

    return render_template(
        "insights.html",
        total_tasks=total,
        completed_tasks=completed,
        remaining_tasks=remaining,
        focus_time=focus_time,
    )
