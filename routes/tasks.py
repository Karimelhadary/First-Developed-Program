from flask import Blueprint, render_template, request, redirect, url_for, abort
from routes.data import Task, tasks, get_next_id, find_task



tasks_bp = Blueprint("tasks_bp", __name__)

@tasks_bp.route("/tasklist")
@tasks_bp.route("/tasklist.html")
def task_list():
    return render_template("tasklist.html", tasks=tasks)

@tasks_bp.route("/addtask", methods=["GET", "POST"])
@tasks_bp.route("/addtask.html", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description", "")
        due_date = request.form.get("due_date")
        importance = request.form.get("importance", "Low")
        complexity = int(request.form.get("complexity", 1))
        energy = int(request.form.get("energy", 1))

        if not title or not due_date:
            return render_template("addtask.html", error="Title and due date are required.")

        new_task = Task(
            id=get_next_id(),
            title=title,
            description=description,
            due_date=due_date,
            importance=importance,
            complexity=complexity,
            energy=energy,
        )
        tasks.append(new_task)
        return redirect(url_for("dashboard_bp.dashboard"))

    return render_template("addtask.html", editing=False)

@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        abort(404)

    if request.method == "POST":
        task.title = request.form.get("title", task.title)
        task.description = request.form.get("description", task.description)
        task.due_date = request.form.get("due_date", task.due_date)
        task.importance = request.form.get("importance", task.importance)
        task.complexity = int(request.form.get("complexity", task.complexity))
        task.energy = int(request.form.get("energy", task.energy))
        return redirect(url_for("tasks_bp.task_list"))

    return render_template("addtask.html", task=task, editing=True)

@tasks_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        abort(404)

    tasks.remove(task)
    return redirect(url_for("tasks_bp.task_list"))
