from flask import Blueprint, render_template, request, redirect, url_for, abort, current_app
from bson import ObjectId

tasks_bp = Blueprint("tasks_bp", __name__)

def to_task_object(doc):
    """Convert Mongo document → template-friendly dict"""
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "description": doc.get("description", ""),
        "due_date": doc.get("due_date", ""),
        "importance": doc.get("importance", "Low"),
        "complexity": doc.get("complexity", 1),
        "energy": doc.get("energy", 1),
        "completed": doc.get("completed", False)
    }

@tasks_bp.route("/tasklist")
def task_list():
    raw = list(current_app.tasks.find())
    tasks = [to_task_object(t) for t in raw]
    return render_template("tasklist.html", tasks=tasks)

@tasks_bp.route("/addtask", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        new_task = {
            "title": request.form["title"],
            "description": request.form["description"],
            "due_date": request.form["due_date"],
            "importance": request.form["importance"],
            "complexity": int(request.form["complexity"]),
            "energy": int(request.form["energy"]),
            "completed": False
        }
        current_app.tasks.insert_one(new_task)
        return redirect(url_for("dashboard_bp.dashboard"))

    return render_template("addtask.html", editing=False)

@tasks_bp.route("/tasks/<task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    doc = current_app.tasks.find_one({"_id": ObjectId(task_id)})
    if not doc:
        abort(404)

    task = to_task_object(doc)

    if request.method == "POST":
        updated_task = {
            "title": request.form["title"],
            "description": request.form["description"],
            "due_date": request.form["due_date"],
            "importance": request.form["importance"],
            "complexity": int(request.form["complexity"]),
            "energy": int(request.form["energy"])
        }
        current_app.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": updated_task}
        )
        return redirect(url_for("tasks_bp.task_list"))

    return render_template("addtask.html", task=task, editing=True)

@tasks_bp.route("/tasks/<task_id>/delete", methods=["POST"])
def delete_task(task_id):
    current_app.tasks.delete_one({"_id": ObjectId(task_id)})
    return redirect(url_for("tasks_bp.task_list"))
