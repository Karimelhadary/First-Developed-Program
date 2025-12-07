from flask import Blueprint, render_template, request, redirect, url_for, abort, current_app
from bson import ObjectId

tasks_bp = Blueprint("tasks_bp", __name__)


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


@tasks_bp.route("/tasklist")
def task_list():
    """Show all tasks, with optional sorting."""
    sort_param = request.args.get("sort", "due_date")

    # Fetch all tasks first
    docs = list(current_app.tasks.find())

    # Helpers for ranking
    importance_rank = {"Low": 1, "Medium": 2, "High": 3}

    if sort_param == "importance":
        # High -> Medium -> Low
        docs.sort(
            key=lambda d: importance_rank.get(d.get("importance", "Low"), 0),
            reverse=True,
        )
    elif sort_param == "complexity":
        # 5 -> 1
        docs.sort(key=lambda d: d.get("complexity", 1), reverse=True)
    else:
        # due_date: earliest -> latest (string compare is OK for YYYY-MM-DD)
        docs.sort(key=lambda d: d.get("due_date", ""))

    tasks = [to_task_object(doc) for doc in docs]

    return render_template("tasklist.html", tasks=tasks, sort=sort_param)


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
            "completed": False,
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
            "energy": int(request.form["energy"]),
        }
        current_app.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": updated_task},
        )
        return redirect(url_for("tasks_bp.task_list"))

    return render_template("addtask.html", task=task, editing=True)


@tasks_bp.route("/tasks/<task_id>/delete", methods=["POST"])
def delete_task(task_id):
    current_app.tasks.delete_one({"_id": ObjectId(task_id)})
    return redirect(url_for("tasks_bp.task_list"))


@tasks_bp.route("/tasks/<task_id>/toggle_complete", methods=["POST"])
def toggle_complete(task_id):
    """Toggle the 'completed' status of a task."""
    doc = current_app.tasks.find_one({"_id": ObjectId(task_id)})
    if not doc:
        abort(404)

    new_value = not doc.get("completed", False)

    current_app.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"completed": new_value}},
    )

    # Preserve current sort choice if present
    sort_param = request.args.get("sort")
    if sort_param:
        return redirect(url_for("tasks_bp.task_list", sort=sort_param))
    return redirect(url_for("tasks_bp.task_list"))
