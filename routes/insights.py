from flask import Blueprint, render_template, current_app

insights_bp = Blueprint("insights_bp", __name__)

@insights_bp.route("/insights")
def insights():

    total = current_app.tasks.count_documents({})
    completed = current_app.tasks.count_documents({"completed": True})

    return render_template(
        "insights.html",
        total_tasks=total,
        completed_tasks=completed
    )
