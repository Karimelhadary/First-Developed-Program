from flask import Blueprint, render_template, request, redirect, url_for, abort, session

from utils.auth import login_required
from model.project_model import list_projects
from model.tag_model import list_tags, ensure_tags_exist
from model.task_model import (
    get_all_tasks_sorted,
    get_task_by_id,
    insert_task,
    update_task,
    delete_task,
    toggle_task_complete,
)

tasks_bp = Blueprint("tasks_bp", __name__)


@tasks_bp.route("/tasklist")
@login_required
def task_list():
    sort_param = request.args.get("sort", "due_date")
    project_id = request.args.get("project") or ""
    user_id = session.get("user_id")

    projects = list_projects(user_id)
    project_name = {p["id"]: p["name"] for p in projects}

    # filtered tasks
    tasks = get_all_tasks_sorted(user_id, sort_param, project_id if project_id else None)

    # enrich for UI
    for t in tasks:
        pid = t.get("project_id")
        t["project_name"] = project_name.get(pid, "No project") if pid else "No project"

    return render_template(
        "tasklist.html",
        tasks=tasks,
        sort=sort_param,
        projects=projects,
        project_id=project_id,
    )


@tasks_bp.route("/addtask", methods=["GET", "POST"])
@login_required
def add_task():
    user_id = session.get("user_id")

    # Ensure default tags exist (useful for demo + rubric)
    ensure_tags_exist(user_id, ["Study", "Work", "Health", "Personal"])

    if request.method == "POST":
        tags_raw = request.form.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        task_data = {
            "project_id": request.form.get("project_id") or None,
            "tags": tags,
            "title": request.form["title"],
            "description": request.form["description"],
            "due_date": request.form["due_date"],
            "importance": request.form["importance"],
            "complexity": int(request.form["complexity"]),
            "energy": int(request.form["energy"]),
            "completed": False,
        }
        insert_task(user_id, task_data)
        return redirect(url_for("dashboard_bp.dashboard"))

    projects = list_projects(user_id)
    tags = list_tags(user_id)
    return render_template("addtask.html", editing=False, projects=projects, tags=tags)


@tasks_bp.route("/tasks/<task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    user_id = session.get("user_id")
    task = get_task_by_id(user_id, task_id)
    if not task:
        abort(404)

    if request.method == "POST":
        tags_raw = request.form.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        updates = {
            "project_id": request.form.get("project_id") or None,
            "tags": tags,
            "title": request.form["title"],
            "description": request.form["description"],
            "due_date": request.form["due_date"],
            "importance": request.form["importance"],
            "complexity": int(request.form["complexity"]),
            "energy": int(request.form["energy"]),
        }
        update_task(user_id, task_id, updates)
        return redirect(url_for("tasks_bp.task_list"))

    projects = list_projects(user_id)
    tags = list_tags(user_id)
    return render_template("addtask.html", task=task, editing=True, projects=projects, tags=tags)


@tasks_bp.route("/tasks/<task_id>/delete", methods=["POST"])
@login_required
def delete_task_route(task_id):
    user_id = session.get("user_id")
    delete_task(user_id, task_id)
    # keep filters if present
    sort_param = request.args.get("sort", "due_date")
    project_id = request.args.get("project", "")
    return redirect(url_for("tasks_bp.task_list", sort=sort_param, project=project_id))


@tasks_bp.route("/tasks/<task_id>/toggle_complete", methods=["POST"])
@login_required
def toggle_complete(task_id):
    user_id = session.get("user_id")
    toggle_task_complete(user_id, task_id)

    sort_param = request.args.get("sort", "due_date")
    project_id = request.args.get("project", "")
    return redirect(url_for("tasks_bp.task_list", sort=sort_param, project=project_id))
