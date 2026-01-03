from flask import Blueprint, render_template, session
from model.task_model import get_tasks_for_dashboard
from utils.auth import login_required

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Mood set in onboarding (defaults to "focused")
    mood = session.get("current_mood", "focused")

    tasks = get_tasks_for_dashboard(user_id=session.get("user_id"), mood=mood)

    mood_labels = {
        "energetic": "⚡ Energetic",
        "focused": "🎯 Focused",
        "calm": "😊 Calm",
        "creative": "✨ Creative",
    }
    mood_label = mood_labels.get(mood, "🎯 Focused")

    return render_template(
        "dashboard.html",
        tasks=tasks,
        mood_label=mood_label,
        user_name=session.get("user_name", "User"),
    )
