from flask import Blueprint, render_template, request, redirect, url_for, abort
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
def task_list():
    """Show all tasks, with optional sorting."""
    sort_param = request.args.get("sort", "due_date")
    tasks = get_all_tasks_sorted(sort_param)
    return render_template("tasklist.html", tasks=tasks, sort=sort_param)


@tasks_bp.route("/addtask", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        task_data = {
            "title": request.form["title"],
            "description": request.form["description"],
            "due_date": request.form["due_date"],
            "importance": request.form["importance"],
            "complexity": int(request.form["complexity"]),
            "energy": int(request.form["energy"]),
            "completed": False,
        }
        insert_task(task_data)
        return redirect(url_for("dashboard_bp.dashboard"))

    return render_template("addtask.html", editing=False)


@tasks_bp.route("/tasks/<task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = get_task_by_id(task_id)
    if not task:
        abort(404)

    if request.method == "POST":
        updates = {
            "title": request.form["title"],
            "description": request.form["description"],
            "due_date": request.form["due_date"],
            "importance": request.form["importance"],
            "complexity": int(request.form["complexity"]),
            "energy": int(request.form["energy"]),
        }
        update_task(task_id, updates)
        return redirect(url_for("tasks_bp.task_list"))

    return render_template("addtask.html", task=task, editing=True)


@tasks_bp.route("/tasks/<task_id>/delete", methods=["POST"])
def delete_task_route(task_id):
    delete_task(task_id)
    return redirect(url_for("tasks_bp.task_list"))


@tasks_bp.route("/tasks/<task_id>/toggle_complete", methods=["POST"])
def toggle_complete(task_id):
    """Toggle the 'completed' status of a task."""
    toggle_task_complete(task_id)

    sort_param = request.args.get("sort")
    if sort_param:
        return redirect(url_for("tasks_bp.task_list", sort=sort_param))
    return redirect(url_for("tasks_bp.task_list"))
