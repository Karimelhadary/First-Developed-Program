from flask import Blueprint, render_template, current_app

insights_bp = Blueprint("insights_bp", __name__)


@insights_bp.route("/insights")
def insights():
    total = current_app.tasks.count_documents({})
    completed = current_app.tasks.count_documents({"completed": True})
    remaining = max(total - completed, 0)

    focus_sessions = current_app.focus_sessions.count_documents({})
    mood_logs = current_app.moods.count_documents({})

    # Placeholder - could be derived from focus_sessions in the future
    focus_time = "1h 25m"

    return render_template(
        "insights.html",
        total_tasks=total,
        completed_tasks=completed,
        remaining_tasks=remaining,
        focus_time=focus_time,
        focus_sessions=focus_sessions,
        mood_logs=mood_logs,
    )
