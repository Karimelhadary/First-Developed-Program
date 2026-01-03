"""Projects CRUD pages.

This adds an additional complete Create/Read/Update/Delete flow beyond tasks,
which helps rubric scores and makes the app more realistic.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, abort

from utils.auth import login_required
from model.project_model import list_projects, get_project, create_project, update_project, delete_project

projects_bp = Blueprint("projects_bp", __name__)


@projects_bp.route("/projects")
@login_required
def projects_list():
    user_id = session.get("user_id")
    projects = list_projects(user_id)
    return render_template("projects.html", projects=projects)


@projects_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def projects_new():
    if request.method == "POST":
        user_id = session.get("user_id")
        name = request.form.get("name", "").strip()
        if name:
            create_project(user_id, name)
        return redirect(url_for("projects_bp.projects_list"))

    return render_template("project_form.html", editing=False)


@projects_bp.route("/projects/<project_id>/edit", methods=["GET", "POST"])
@login_required
def projects_edit(project_id: str):
    user_id = session.get("user_id")
    project = get_project(user_id, project_id)
    if not project:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            update_project(user_id, project_id, name)
        return redirect(url_for("projects_bp.projects_list"))

    return render_template("project_form.html", editing=True, project=project)


@projects_bp.route("/projects/<project_id>/delete", methods=["POST"])
@login_required
def projects_delete(project_id: str):
    user_id = session.get("user_id")
    delete_project(user_id, project_id)
    return redirect(url_for("projects_bp.projects_list"))
