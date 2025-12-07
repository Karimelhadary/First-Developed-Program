from flask import Blueprint, render_template, session
from model.task_model import get_tasks_for_dashboard

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    # Mood set in onboarding (defaults to "focused")
    mood = session.get("current_mood", "focused")

    tasks = get_tasks_for_dashboard(mood)

    mood_labels = {
        "energetic": "⚡ Energetic",
        "focused": "🎯 Focused",
        "calm": "😊 Calm",
        "creative": "✨ Creative",
    }
    mood_label = mood_labels.get(mood, "🎯 Focused")

    return render_template("dashboard.html", tasks=tasks, mood_label=mood_label)
