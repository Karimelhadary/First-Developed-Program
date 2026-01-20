# Enable future annotations for improved type hinting support in Python
from __future__ import annotations

# Import datetime and date classes from datetime module for date parsing and comparisons
from datetime import datetime, date
# Import defaultdict from collections for dictionaries that provide default values for missing keys
from collections import defaultdict

# Import Blueprint for creating modular route groups, render_template for rendering HTML, session for storing user data, current_app for accessing the Flask app context
from flask import Blueprint, render_template, session, current_app

# Import get_tasks_for_dashboard function from task_model to retrieve tasks filtered by user and mood
from model.task_model import get_tasks_for_dashboard
# Import list_projects function from project_model to get all projects for a user
from model.project_model import list_projects
# Import tasks module from routes (though not directly used in this file, possibly for side effects or future use)
from routes import tasks
# Import login_required decorator from utils.auth to ensure user is authenticated before accessing routes
from utils.auth import login_required



# Create a Blueprint named 'dashboard_bp' with the current module name for organizing dashboard-related routes
dashboard_bp = Blueprint("dashboard_bp", __name__)


# Define helper function _parse_due to convert a due date string to a date object or None if invalid
def _parse_due(due_str: str):
    # Check if due_str is empty or None; if so, return None
    if not due_str:
        return None
    # Attempt to parse the string in YYYY-MM-DD format to a date object
    try:
        return datetime.strptime(due_str, "%Y-%m-%d").date()
    except Exception:
        # If parsing fails (e.g., invalid format), return None
        return None


# Define helper function _due_status to determine the status of a due date relative to today
def _due_status(d: date | None, today: date):
    # If no due date, return "none" status and None for days left
    if not d:
        return "none", None
    # Calculate days difference: positive if future, negative if past
    delta = (d - today).days
    # If overdue (negative days), return "overdue" and the negative delta
    if delta < 0:
        return "overdue", delta
    # If due today (zero days), return "today" and 0
    if delta == 0:
        return "today", 0
    # If due in 1-3 days, return "soon" and the delta
    if 1 <= delta <= 3:
        return "soon", delta
    # Otherwise, due later, return "later" and the delta
    return "later", delta


# Define helper function _importance_class to map importance strings to CSS class codes
def _importance_class(importance: str):
    # Map "High" to "high" class
    if importance == "High":
        return "high"
    # Map "Medium" to "med" class
    if importance == "Medium":
        return "med"
    # Default to "low" for "Low" or any other value
    return "low"


# Route decorator: register the dashboard function to handle GET requests to "/dashboard"
@dashboard_bp.route("/dashboard")
# Apply login_required decorator to ensure only authenticated users can access this route
@login_required
def dashboard():
    # Retrieve the user_id from the session
    user_id = session.get("user_id")

    # Get the current mood from session, defaulting to "focused" if not set
    mood = session.get("current_mood", "focused")

    # Define mood labels with emojis for display
    mood_labels = {
        "energetic": "⚡ Energetic",
        "focused": "🎯 Focused",
        "calm": "😊 Calm",
        "creative": "✨ Creative",
    }
    # Get the label for the current mood, defaulting to "🎯 Focused"
    mood_label = mood_labels.get(mood, "🎯 Focused")

    # Fetch tasks for the dashboard, filtered by user_id and mood
    tasks = get_tasks_for_dashboard(user_id=user_id, mood=mood)

    # Get list of projects for the user
    projects = list_projects(user_id)
    # Create a dictionary mapping project IDs to project names for quick lookup
    project_name = {p["id"]: p["name"] for p in projects}

    # Retrieve all focus sessions for the user from the database
    focus_docs = list(current_app.focus_sessions.find({"user_id": user_id}))
    # Initialize defaultdicts to accumulate focus minutes and session counts per task
    focus_minutes_by_task = defaultdict(int)
    focus_sessions_by_task = defaultdict(int)
    # Loop through each focus session document
    for s in focus_docs:
        # Get the task_id from the session
        tid = s.get("task_id")
        # If task_id exists, accumulate minutes and increment session count
        if tid:
            focus_minutes_by_task[tid] += int(s.get("minutes", 0) or 0)
            focus_sessions_by_task[tid] += 1

    # Get today's date in UTC
    today = datetime.utcnow().date()

    # Initialize list to hold enriched task data
    enriched = []
    # Loop through each task to add computed fields
    for t in tasks:
        # Parse the due date string to a date object
        due = _parse_due(t.get("due_date", ""))
        # Determine due status and days left
        status, days_left = _due_status(due, today)

        # Get task ID
        tid = t.get("id")
        # Get accumulated focus minutes for this task
        focus_min = focus_minutes_by_task.get(tid, 0)
        # Get accumulated focus sessions for this task
        focus_cnt = focus_sessions_by_task.get(tid, 0)

        # Get project ID and map to project name
        pid = t.get("project_id")
        p_name = project_name.get(pid, "No project") if pid else "No project"

        # Get importance and map to CSS class
        importance = t.get("importance", "Low")
        imp_code = _importance_class(importance)

        # Append enriched task dictionary with additional fields
        enriched.append(
            {
                **t,  # Spread original task fields
                "project_name": p_name,
                "due_status": status,
                "days_left": days_left,
                "focus_minutes": focus_min,
                "focus_sessions": focus_cnt,
                "importance_code": imp_code,
            }
        )

    # Filter tasks into open (not completed) and done (completed)
    open_tasks = [t for t in enriched if not t.get("completed")]
    done_tasks = [t for t in enriched if t.get("completed")]

    # Further filter open tasks by due status
    overdue = [t for t in open_tasks if t["due_status"] == "overdue"]
    due_today = [t for t in open_tasks if t["due_status"] == "today"]
    due_soon = [t for t in open_tasks if t["due_status"] == "soon"]

    # Sort open tasks for suggested focus plan: prioritize by due status, importance, then due date
    suggested = sorted(
        open_tasks,
        key=lambda x: (
            0 if x["due_status"] in ("overdue", "today", "soon") else 1,  # Urgent first
            0 if x.get("importance") == "High" else 1,  # High importance first
            x.get("due_date", "9999-12-31"),  # Earlier due dates first
        ),
    )[:6]  # Take top 6

    # Identify quick wins: urgent tasks with low complexity (<=2)
    quick_wins = sorted(
        [t for t in open_tasks if t["due_status"] in ("overdue", "today", "soon") and int(t.get("complexity", 1)) <= 2],
        key=lambda x: (0 if x["due_status"] == "overdue" else 1, x.get("due_date", "9999-12-31")),
    )[:4]

    # Identify big rocks: tasks with highest complexity, prioritizing urgent ones
    big_rocks = sorted(
        [t for t in open_tasks],
        key=lambda x: (int(x.get("complexity", 1)), 0 if x["due_status"] in ("overdue", "today", "soon") else 1),
        reverse=True,  # Highest complexity first
    )[:4]

    # Identify neglected urgent tasks: no focus minutes and due soon/today/overdue
    neglected_urgent = sorted(
        [t for t in open_tasks if (t.get("focus_minutes", 0) == 0) and t["due_status"] in ("overdue", "today", "soon")],
        key=lambda x: (0 if x["due_status"] == "overdue" else 1, x.get("due_date", "9999-12-31")),
    )[:4]

    # Get high priority tasks: importance "High"
    high_priority = [t for t in open_tasks if t.get("importance") == "High"][:5]
    # Get neglected tasks: no focus minutes
    neglected = [t for t in open_tasks if (t.get("focus_minutes", 0) == 0)][:5]

    # Calculate KPIs: counts for open, done, overdue, and due soon
    kpis = {
        "open": len(open_tasks),
        "done": len(done_tasks),
        "overdue": len(overdue),
        "due_soon": len(due_today) + len(due_soon),
    }

    # Render the dashboard template with all computed data
    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "User"),
        mood_label=mood_label,
        kpis=kpis,
        suggested=suggested,
        overdue=overdue[:5],  # Limit to 5 for display
        due_today=due_today[:5],
        due_soon=due_soon[:5],
        high_priority=high_priority,
        neglected=neglected,
        quick_wins=quick_wins,
        big_rocks=big_rocks,
        neglected_urgent=neglected_urgent,
    )
