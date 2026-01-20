
# --- Imports used in this file (what we need from libraries/modules) ---
from __future__ import annotations

from collections import defaultdict

from flask import Blueprint, render_template, request, redirect, url_for, session, abort, current_app

from utils.auth import login_required
from model.project_model import list_projects, get_project, create_project, update_project, delete_project



# Blueprint groups related routes into a reusable module
projects_bp = Blueprint("projects_bp", __name__)


# Function: _col (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: _col
# What happens here: inputs -> logic -> output/return
# -------------------------------
def _col(name: str):
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if hasattr(current_app, "db"):
        # MongoDB operation: read/write data in a collection
        return current_app.db[name]
    return getattr(current_app, name)


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@projects_bp.route("/projects")
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: projects_list (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: projects_list
# What happens here: inputs -> logic -> output/return
# -------------------------------
def projects_list():
    user_id = session.get("user_id")
    projects = list_projects(user_id)

    tasks_col = _col("tasks")
    focus_col = _col("focus_sessions")

    # focus per task id (for fast project rollups)
    # MongoDB operation: read/write data in a collection
    focus_docs = list(focus_col.find({"user_id": user_id}))
    task_focus = defaultdict(int)
    # Control-flow: starts a 'for' block (indentation shows what belongs to it).
    for s in focus_docs:
        tid = s.get("task_id")
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if tid:
            task_focus[tid] += int(s.get("minutes", 0) or 0)

    enriched = []
    # Control-flow: starts a 'for' block (indentation shows what belongs to it).
    for p in projects:
        pid = p["id"]
        # MongoDB operation: read/write data in a collection
        p_tasks = list(tasks_col.find({"user_id": user_id, "project_id": pid}))
        total = len(p_tasks)
        done = sum(1 for t in p_tasks if t.get("completed") is True)
        # sum focus minutes for tasks in this project
        focus_minutes = sum(task_focus.get(str(t["_id"]), 0) for t in p_tasks)
        enriched.append(
            {
                **p,
                "tasks_total": total,
                "tasks_done": done,
                "focus_minutes": focus_minutes,
            }
        )

    enriched.sort(key=lambda x: x["focus_minutes"], reverse=True)
    return render_template("projects.html", projects=enriched)


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@projects_bp.route("/projects/<project_id>")
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: project_detail (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: project_detail
# What happens here: inputs -> logic -> output/return
# -------------------------------
def project_detail(project_id: str):
    user_id = session.get("user_id")
    project = get_project(user_id, project_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not project:
        abort(404)

    tasks_col = _col("tasks")
    focus_col = _col("focus_sessions")

    # MongoDB operation: read/write data in a collection
    tasks = list(tasks_col.find({"user_id": user_id, "project_id": project_id}))

    # map focus minutes per task
    # MongoDB operation: read/write data in a collection
    focus_docs = list(focus_col.find({"user_id": user_id}))
    task_focus = defaultdict(int)
    task_sessions = defaultdict(int)

    # Control-flow: starts a 'for' block (indentation shows what belongs to it).
    for s in focus_docs:
        tid = s.get("task_id")
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if tid:
            task_focus[tid] += int(s.get("minutes", 0) or 0)
            task_sessions[tid] += 1

    view_tasks = []
    # Control-flow: starts a 'for' block (indentation shows what belongs to it).
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

    view_tasks.sort(key=lambda x: (x["completed"], x["due_date"]))

    total = len(view_tasks)
    done = sum(1 for t in view_tasks if t["completed"])
    focus_total = sum(t["focus_minutes"] for t in view_tasks)

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


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@projects_bp.route("/projects/new", methods=["GET", "POST"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: projects_new (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: projects_new
# What happens here: inputs -> logic -> output/return
# -------------------------------
def projects_new():
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if request.method == "POST":
        user_id = session.get("user_id")
        name = request.form.get("name", "").strip()
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if name:
            create_project(user_id, name)
        return redirect(url_for("projects_bp.projects_list"))

    return render_template("project_form.html", editing=False)


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@projects_bp.route("/projects/<project_id>/edit", methods=["GET", "POST"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: projects_edit (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: projects_edit
# What happens here: inputs -> logic -> output/return
# -------------------------------
def projects_edit(project_id: str):
    user_id = session.get("user_id")
    project = get_project(user_id, project_id)
    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if not project:
        abort(404)

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if name:
            update_project(user_id, project_id, name)
        return redirect(url_for("projects_bp.projects_list"))

    return render_template("project_form.html", editing=True, project=project)


# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@projects_bp.route("/projects/<project_id>/delete", methods=["POST"])
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_required
# Function: projects_delete (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: projects_delete
# What happens here: inputs -> logic -> output/return
# -------------------------------
def projects_delete(project_id: str):
    user_id = session.get("user_id")
    delete_project(user_id, project_id)
    return redirect(url_for("projects_bp.projects_list"))
