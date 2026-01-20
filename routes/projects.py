# Enable future annotations for better type hinting
from __future__ import annotations

# Import defaultdict for default dictionaries
from collections import defaultdict

# Import Flask components: Blueprint for routes, render_template for HTML, request for form data, redirect for redirects, url_for for URLs, session for user data, abort for 404 errors, current_app for app context
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, current_app

# Import login_required decorator
from utils.auth import login_required
# Import project model functions for CRUD operations
from model.project_model import list_projects, get_project, create_project, update_project, delete_project



# Create Blueprint for project-related routes
projects_bp = Blueprint("projects_bp", __name__)


# Helper function to get a MongoDB collection by name, supporting different app configurations
def _col(name: str):
    # Check if app has a 'db' attribute (alternative MongoDB setup)
    if hasattr(current_app, "db"):
        # Access collection via current_app.db[name]
        return current_app.db[name]
    # Otherwise, access as attribute of current_app (e.g., current_app.tasks)
    return getattr(current_app, name)


# Route to list all projects for the user
@projects_bp.route("/projects")
@login_required
def projects_list():
    # Get user ID from session
    user_id = session.get("user_id")
    # Fetch user's projects
    projects = list_projects(user_id)

    # Get database collections
    tasks_col = _col("tasks")
    focus_col = _col("focus_sessions")

    # Fetch all focus sessions for the user
    focus_docs = list(focus_col.find({"user_id": user_id}))
    # Create defaultdict to accumulate focus minutes per task
    task_focus = defaultdict(int)
    # Loop through focus sessions and sum minutes per task
    for s in focus_docs:
        tid = s.get("task_id")
        if tid:
            task_focus[tid] += int(s.get("minutes", 0) or 0)

    # Enrich projects with statistics
    enriched = []
    for p in projects:
        pid = p["id"]
        # Get tasks for this project
        p_tasks = list(tasks_col.find({"user_id": user_id, "project_id": pid}))
        total = len(p_tasks)
        # Count completed tasks
        done = sum(1 for t in p_tasks if t.get("completed") is True)
        # Sum focus minutes for tasks in this project
        focus_minutes = sum(task_focus.get(str(t["_id"]), 0) for t in p_tasks)
        # Append enriched project data
        enriched.append(
            {
                **p,  # Spread original project data
                "tasks_total": total,
                "tasks_done": done,
                "focus_minutes": focus_minutes,
            }
        )

    # Sort projects by focus minutes descending
    enriched.sort(key=lambda x: x["focus_minutes"], reverse=True)
    # Render projects list template
    return render_template("projects.html", projects=enriched)


# Route to show details of a specific project
@projects_bp.route("/projects/<project_id>")
@login_required
def project_detail(project_id: str):
    # Get user ID
    user_id = session.get("user_id")
    # Fetch project by ID
    project = get_project(user_id, project_id)
    # If project not found, return 404
    if not project:
        abort(404)

    # Get collections
    tasks_col = _col("tasks")
    focus_col = _col("focus_sessions")

    # Fetch tasks for this project
    tasks = list(tasks_col.find({"user_id": user_id, "project_id": project_id}))

    # Fetch focus sessions and aggregate per task
    focus_docs = list(focus_col.find({"user_id": user_id}))
    task_focus = defaultdict(int)
    task_sessions = defaultdict(int)

    # Loop through focus sessions
    for s in focus_docs:
        tid = s.get("task_id")
        if tid:
            # Accumulate minutes and session count
            task_focus[tid] += int(s.get("minutes", 0) or 0)
            task_sessions[tid] += 1

    # Prepare tasks for view
    view_tasks = []
    for t in tasks:
        tid = str(t["_id"])
        view_tasks.append(
            {
                "id": tid,
                "title": t.get("title", ""),
                "completed": bool(t.get("completed")),
                "due_date": t.get("due_date", ""),
                "importance": t.get("importance", "Low"),
                "complexity": t.get("complexity", 1),
                "focus_minutes": task_focus.get(tid, 0),
                "focus_sessions": task_sessions.get(tid, 0),
            }
        )

    # Sort tasks: completed first, then by due date
    view_tasks.sort(key=lambda x: (x["completed"], x["due_date"]))

    # Calculate project stats
    total = len(view_tasks)
    done = sum(1 for t in view_tasks if t["completed"])
    focus_total = sum(t["focus_minutes"] for t in view_tasks)

    # Render project detail template
    return render_template(
        "project_detail.html",
        project=project,
        tasks=view_tasks,
        stats={
            "total": total,
            "done": done,
            "focus_minutes": focus_total,
        },
    )


# Route to create a new project
@projects_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def projects_new():
    # Handle POST request (form submission)
    if request.method == "POST":
        user_id = session.get("user_id")
        name = request.form.get("name", "").strip()
        # If name provided, create project
        if name:
            create_project(user_id, name)
        # Redirect to projects list
        return redirect(url_for("projects_bp.projects_list"))

    # Render new project form
    return render_template("project_form.html", editing=False)


# Route to edit an existing project
@projects_bp.route("/projects/<project_id>/edit", methods=["GET", "POST"])
@login_required
def projects_edit(project_id: str):
    user_id = session.get("user_id")
    # Fetch project
    project = get_project(user_id, project_id)
    if not project:
        abort(404)

    # Handle POST
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            update_project(user_id, project_id, name)
        return redirect(url_for("projects_bp.projects_list"))

    # Render edit form
    return render_template("project_form.html", editing=True, project=project)


# Route to delete a project
@projects_bp.route("/projects/<project_id>/delete", methods=["POST"])
@login_required
def projects_delete(project_id: str):
    user_id = session.get("user_id")
    # Delete project
    delete_project(user_id, project_id)
    # Redirect to projects list
    return redirect(url_for("projects_bp.projects_list"))
