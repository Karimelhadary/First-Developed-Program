# Enable future annotations for better type hinting
from __future__ import annotations

# Import defaultdict for default dictionary values, datetime and timedelta for date handling
from collections import defaultdict
from datetime import datetime, timedelta

# Import Flask components: Blueprint for routes, render_template for HTML, session for user data, jsonify for JSON responses, current_app for app context
from flask import Blueprint, render_template, session, jsonify, current_app
# Import login_required decorator to protect routes
from utils.auth import login_required


# Create Blueprint for insights-related routes
insights_bp = Blueprint("insights_bp", __name__)


# Helper function to get a collection from the database, supporting different access styles
def _col(name: str):
    # Check if current_app has a 'db' attribute (alternative database access)
    if hasattr(current_app, "db"):
        # Access collection via current_app.db[name]
        return current_app.db[name]
    # Otherwise, access as an attribute of current_app (e.g., current_app.tasks)
    return getattr(current_app, name)


# Helper function to safely convert a value to int, returning default if conversion fails
def _safe_int(x, default=0):
    # Attempt to convert x to int
    try:
        return int(x)
    except Exception:
        # Return default value if conversion fails
        return default



# Function to generate insights data payload for a user
def _insights_payload(user_id: str) -> dict:
    # Get database collections for tasks, focus sessions, break sessions, moods, and projects
    tasks_col = _col("tasks")
    focus_col = _col("focus_sessions")
    break_col = _col("break_sessions")
    moods_col = _col("moods")
    projects_col = _col("projects")

    # Calculate task summary: total tasks, completed, remaining, and progress percentage
    total = tasks_col.count_documents({"user_id": user_id})
    completed = tasks_col.count_documents({"user_id": user_id, "completed": True})
    remaining = max(total - completed, 0)
    progress_pct = int(round((completed / total) * 100)) if total > 0 else 0

    # Retrieve focus and break session documents for the user
    focus_docs = list(focus_col.find({"user_id": user_id}))
    break_docs = list(break_col.find({"user_id": user_id}))

    # Sum up total focus and break minutes from sessions
    focus_minutes = sum(_safe_int(d.get("minutes", 0)) for d in focus_docs)
    break_minutes = sum(_safe_int(d.get("minutes", 0)) for d in break_docs)

    # Count mood logs for the user
    mood_logs_count = moods_col.count_documents({"user_id": user_id})

    # Prepare data for last 7 days chart: get dates from 6 days ago to today
    today = datetime.utcnow().date()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    labels = [d.strftime("%a") for d in days]  # Abbreviated day names like 'Mon', 'Tue'

    # Nested function to sum minutes by day for a list of documents
    def sum_by_day(docs):
        # Initialize dictionary with 0 for each day
        per = {d: 0 for d in days}
        # Loop through each document
        for doc in docs:
            # Get created_at datetime
            dt = doc.get("created_at")
            if not dt:
                continue
            # Extract date part
            try:
                day = dt.date()
            except Exception:
                continue
            # If day is in our range, add minutes
            if day in per:
                per[day] += _safe_int(doc.get("minutes", 0))
        # Return list of sums in day order
        return [per[d] for d in days]

    # Get focus and break minutes series for the chart
    focus_series = sum_by_day(focus_docs)
    break_series = sum_by_day(break_docs)

    # Initialize dictionaries for task-based focus aggregation
    task_minutes = defaultdict(int)
    task_sessions = defaultdict(int)
    unlinked_minutes = 0
    unlinked_sessions = 0

    # Loop through focus sessions to aggregate by task
    for s in focus_docs:
        mins = _safe_int(s.get("minutes", 0))
        tid = s.get("task_id")
        if tid:
            # Linked to a task: add to task totals
            task_minutes[tid] += mins
            task_sessions[tid] += 1
        else:
            # Unlinked: add to unlinked totals
            unlinked_minutes += mins
            unlinked_sessions += 1

    # Get task IDs that have focus sessions
    task_ids = list(task_minutes.keys())
    # Query tasks collection for these IDs (assuming ObjectId format)
    task_docs = list(tasks_col.find({"user_id": user_id, "_id": {"$in": [__import__("bson").ObjectId(t) for t in task_ids if _looks_like_objectid(t)]}})) if task_ids else []
    # Note: Additional query for string IDs if needed, but currently no-op

    # Create mapping of task ID strings to task documents
    tasks_by_id = {str(d["_id"]): d for d in task_docs}

    # Get all projects for the user and create ID to name mapping
    projects = list(projects_col.find({"user_id": user_id}))
    project_name = {str(p["_id"]): p.get("name", "Untitled") for p in projects}

    # Build list of top tasks by focus minutes (top 8)
    top_tasks = []
    for tid, mins in sorted(task_minutes.items(), key=lambda x: x[1], reverse=True)[:8]:
        doc = tasks_by_id.get(tid)
        title = doc.get("title") if doc else "Deleted task"
        pid = (doc.get("project_id") if doc else None) or None
        top_tasks.append(
            {
                "task_id": tid,
                "title": title,
                "minutes": mins,
                "sessions": task_sessions.get(tid, 0),
                "project": project_name.get(pid, "No project") if pid else "No project",
            }
        )

    # Build project statistics
    project_stats = []
    for p in projects:
        pid = str(p["_id"])
        # Get tasks for this project
        p_tasks = list(tasks_col.find({"user_id": user_id, "project_id": pid}))
        p_total = len(p_tasks)
        p_done = sum(1 for t in p_tasks if t.get("completed") is True)

        # Sum focus minutes for tasks in this project
        p_task_ids = {str(t["_id"]) for t in p_tasks}
        p_focus_minutes = sum(task_minutes.get(tid, 0) for tid in p_task_ids)

        project_stats.append(
            {
                "project_id": pid,
                "name": p.get("name", "Untitled"),
                "tasks_total": p_total,
                "tasks_done": p_done,
                "focus_minutes": p_focus_minutes,
            }
        )

    # Sort projects by focus minutes descending
    project_stats.sort(key=lambda x: x["focus_minutes"], reverse=True)

    # Return the complete insights payload
    return {
        "tasks": {
            "total": total,
            "completed": completed,
            "remaining": remaining,
            "progress_pct": progress_pct,
        },
        "timer": {
            "focus_minutes": focus_minutes,
            "focus_sessions": len(focus_docs),
            "break_minutes": break_minutes,
            "break_sessions": len(break_docs),
            "unlinked_focus_minutes": unlinked_minutes,
            "unlinked_focus_sessions": unlinked_sessions,
        },
        "mood": {"logs": mood_logs_count},
        "charts": {
            "labels": labels,
            "focus_minutes": focus_series,
            "break_minutes": break_series,
        },
        "top_tasks": top_tasks,
        "projects": project_stats[:8],  # Top 8 projects
    }



# Helper function to check if a string looks like a MongoDB ObjectId (24-character hex)
def _looks_like_objectid(s: str) -> bool:
    # Check length and type
    if not isinstance(s, str) or len(s) != 24:
        return False
    # Try to parse as hex
    try:
        int(s, 16)
        return True
    except Exception:
        return False


# Route for insights page
@insights_bp.route("/insights")
@login_required
def insights():
    # Render the insights HTML template
    return render_template("insights.html")


# API route for insights data
@insights_bp.route("/api/insights")
@login_required
def insights_api():
    # Get user ID from session
    user_id = session.get("user_id")
    # Return JSON response with insights payload
    return jsonify(_insights_payload(user_id))
