from flask import render_template, request, redirect, url_for, abort
from app import app
from data import tasks, get_next_id, find_task
from models import Task

@app.route("/tasklist")
@app.route("/tasklist.html")
def task_list():
    return render_template("tasklist.html", tasks=tasks)

@app.route("/addtask", methods=["GET", "POST"])
@app.route("/addtask.html", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description", "")
        due_date = request.form.get("due_date")
        importance = request.form.get("importance", "Low")
        complexity = int(request.form.get("complexity", 1))
        energy = int(request.form.get("energy", 1))

        if not title or not due_date:
            return render_template("addtask.html", task=None, editing=False, error="Title and due date are required.")

        new_task = Task(get_next_id(), title, description, due_date, importance, complexity, energy)
        tasks.append(new_task)
        return redirect(url_for("dashboard"))

    return render_template("addtask.html", task=None, editing=False)

@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
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
        return redirect(url_for("task_list"))

    return render_template("addtask.html", task=task, editing=True)

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        abort(404)

    tasks.remove(task)
    return redirect(url_for("task_list"))

