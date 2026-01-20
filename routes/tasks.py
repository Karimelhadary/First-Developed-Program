
# Import Blueprint for creating modular route groups, render_template for rendering HTML, request for handling HTTP requests, redirect for redirecting responses, url_for for generating URLs, abort for error responses, session for storing user session data
from flask import Blueprint, render_template, request, redirect, url_for, abort, session

# Import login_required decorator to ensure user is authenticated
from utils.auth import login_required
# Import list_projects function to get user's projects
from model.project_model import list_projects
# Import list_tags and ensure_tags_exist for tag management
from model.tag_model import list_tags, ensure_tags_exist
# Import task model functions for CRUD operations on tasks
from model.task_model import (
    get_all_tasks_sorted,
    get_task_by_id,
    insert_task,
    update_task,
    delete_task,
    toggle_task_complete,
)

# Create a Blueprint named 'tasks_bp' for task-related routes
tasks_bp = Blueprint("tasks_bp", __name__)


# Route decorator: maps the URL '/tasklist' to this function, requires login
@tasks_bp.route("/tasklist")
@login_required
def task_list():
    # Get the sort parameter from query string, default to 'due_date'
    sort_param = request.args.get("sort", "due_date")
    # Get the project filter from query string
    project_id = request.args.get("project") or ""
    # Get the current user's ID from session
    user_id = session.get("user_id")

    # Fetch the list of projects for the user
    projects = list_projects(user_id)
    # Create a dictionary mapping project IDs to names for easy lookup
    project_name = {p["id"]: p["name"] for p in projects}

    # Get filtered and sorted tasks for the user
    tasks = get_all_tasks_sorted(user_id, sort_param, project_id if project_id else None)

    # Enrich task data for the UI by adding project names
    for t in tasks:
        # Get the project ID from the task
        pid = t.get("project_id")
        # Set the project name, defaulting to "No project" if none
        t["project_name"] = project_name.get(pid, "No project") if pid else "No project"

    # Render the tasklist template with tasks, sort param, projects, and current project filter
    return render_template(
        "tasklist.html",
        tasks=tasks,
        sort=sort_param,
        projects=projects,
        project_id=project_id,
    )

# Route for adding a new task, handles GET (show form) and POST (create task)
@tasks_bp.route("/addtask", methods=["GET", "POST"])
@login_required
def add_task():
    # Get the current user's ID
    user_id = session.get("user_id")

    # Ensure default tags exist for the user
    ensure_tags_exist(user_id, ["Study", "Work", "Health", "Personal"])

    # If the request is POST, process the form data to create a new task
    if request.method == "POST":
        # Parse tags from comma-separated string, strip whitespace
        tags_raw = request.form.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        # Collect task data from the form
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
        # Insert the new task into the database
        insert_task(user_id, task_data)
        # Redirect to the dashboard after creation
        return redirect(url_for("dashboard_bp.dashboard"))

    # For GET request, fetch projects and tags to populate the form
    projects = list_projects(user_id)
    tags = list_tags(user_id)
    # Render the add task template
    return render_template("addtask.html", editing=False, projects=projects, tags=tags)


# Route for editing an existing task, handles GET (show form) and POST (update task)
@tasks_bp.route("/tasks/<task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    # Get the current user's ID
    user_id = session.get("user_id")
    # Fetch the task by ID, ensuring it belongs to the user
    task = get_task_by_id(user_id, task_id)
    # If task not found, return 404 error
    if not task:
        abort(404)

    # If POST request, update the task with form data
    if request.method == "POST":
        # Parse tags from form
        tags_raw = request.form.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        # Collect update data
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
        # Update the task in the database
        update_task(user_id, task_id, updates)
        # Redirect back to task list
        return redirect(url_for("tasks_bp.task_list"))

    # For GET, fetch projects and tags for the form
    projects = list_projects(user_id)
    tags = list_tags(user_id)
    # Render the edit form with existing task data
    return render_template("addtask.html", task=task, editing=True, projects=projects, tags=tags)


# Route for deleting a task, only accepts POST requests
@tasks_bp.route("/tasks/<task_id>/delete", methods=["POST"])
@login_required
def delete_task_route(task_id):
    # Get the current user's ID
    user_id = session.get("user_id")
    # Delete the task from the database
    delete_task(user_id, task_id)
    # Preserve the current sort and project filters in the redirect
    sort_param = request.args.get("sort", "due_date")
    project_id = request.args.get("project", "")
    # Redirect back to the task list with filters
    return redirect(url_for("tasks_bp.task_list", sort=sort_param, project=project_id))

# Route for toggling the completion status of a task
@tasks_bp.route("/tasks/<task_id>/toggle_complete", methods=["POST"])
@login_required
def toggle_complete(task_id):
    # Get the current user's ID
    user_id = session.get("user_id")
    # Toggle the task's completed status
    toggle_task_complete(user_id, task_id)

    # Preserve filters for redirect
    sort_param = request.args.get("sort", "due_date")
    project_id = request.args.get("project", "")
    # Redirect back to task list
    return redirect(url_for("tasks_bp.task_list", sort=sort_param, project=project_id))
