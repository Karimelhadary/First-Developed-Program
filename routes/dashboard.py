from flask import Blueprint, render_template, current_app, session

dashboard_bp = Blueprint("dashboard_bp", __name__)


def to_task_object(doc):
    """Convert Mongo document → template-friendly dict."""
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "description": doc.get("description", ""),
        "due_date": doc.get("due_date", ""),
        "importance": doc.get("importance", "Low"),
        "complexity": doc.get("complexity", 1),
        "energy": doc.get("energy", 1),
        "completed": doc.get("completed", False),
    }


@dashboard_bp.route("/dashboard")
def dashboard():
    # Get mood from session (set in onboarding), default to "focused"
    mood = session.get("current_mood", "focused")

    docs = list(current_app.tasks.find())

    importance_rank = {"Low": 1, "Medium": 2, "High": 3}

    # Mood-based sorting logic
    if mood == "energetic":
        # Big challenging tasks first
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    elif mood == "focused":
        # High importance + complex tasks first
        docs.sort(
            key=lambda d: (
                importance_rank.get(d.get("importance", "Low"), 0),
                d.get("complexity", 1),
            ),
            reverse=True,
        )
    elif mood == "calm":
        # Easier tasks first
        docs.sort(key=lambda d: d.get("complexity", 1))
    elif mood == "creative":
        # Lower "energy" tasks first (you could change this to something else later)
        docs.sort(key=lambda d: d.get("energy", 1))
    else:
        # Fallback: due date ascending
        docs.sort(key=lambda d: d.get("due_date", ""))

    tasks = [to_task_object(doc) for doc in docs]

    mood_labels = {
        "energetic": "⚡ Energetic",
        "focused": "🎯 Focused",
        "calm": "😊 Calm",
        "creative": "✨ Creative",
    }
    mood_label = mood_labels.get(mood, "🎯 Focused")

    return render_template("dashboard.html", tasks=tasks, mood_label=mood_label)
