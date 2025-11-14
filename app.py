# app.py
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)

# ------------------------
# Simple in-memory "database"
# ------------------------

class Task:
    def __init__(self, id, title, description, due_date, importance,
                 complexity, energy, completed=False):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date          # string "YYYY-MM-DD"
        self.importance = importance      # "Low", "Medium", "High"
        self.complexity = complexity      # int 1–5
        self.energy = energy              # int 1–5
        self.completed = completed        # bool

tasks = []
_next_id = 1


def get_next_id():
    global _next_id
    current = _next_id
    _next_id += 1
    return current


def find_task(task_id: int) -> Task | None:
    for t in tasks:
        if t.id == task_id:
            return t
    return None


# ------------------------
# Routes: Splash & auth
# ------------------------

@app.route("/")
def index():
    return render_template("splash.html")

@app.route("/splash")
def splash():
    return render_template("splash.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # TODO: real authentication
        # For now, accept anything and go to onboarding
        if not email or not password:
            # very basic "validation"
            return render_template("login.html", error="Please enter email and password.")

        return redirect(url_for("onboarding"))

    # GET
    return render_template("login.html")


@app.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    if request.method == "POST":
        mood = request.form.get("mood", "focused")
        return redirect(url_for("dashboard", mood=mood))

    selected_mood = request.args.get("mood", "focused")
    return render_template("onboarding.html", selected_mood=selected_mood)


# Routes: Dashboard & tasks

@app.route("/dashboard")
def dashboard():
    mood = request.args.get("mood", "focused")

    # Here you could do smart filtering based on mood.
    # For now, just show all tasks and pass mood to template.
    return render_template("dashboard.html", mood=mood, tasks=tasks)


@app.route("/tasks")
def task_list():
    sort_by = request.args.get("sort_by", "due_date")

    def sort_key(task: Task):
        if sort_by == "importance":
            order = {"Low": 0, "Medium": 1, "High": 2}
            return order.get(task.importance, 0)
        if sort_by == "complexity":
            return task.complexity
        # default: due_date as string
        return task.due_date or ""

    sorted_tasks = sorted(tasks, key=sort_key)
    return render_template("tasklist.html", tasks=sorted_tasks, sort_by=sort_by)


@app.route("/tasks/new", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description", "")
        due_date = request.form.get("due_date")
        importance = request.form.get("importance", "Low")
        complexity = request.form.get("complexity", "1")
        energy = request.form.get("energy", "1")

        if not title or not due_date:
            # re-render with error
            return render_template(
                "addtask.html",
                error="Title and due date are required.",
            )

        new_task = Task(
            id=get_next_id(),
            title=title,
            description=description,
            due_date=due_date,
            importance=importance,
            complexity=int(complexity),
            energy=int(energy),
        )
        tasks.append(new_task)
        return redirect(url_for("dashboard"))

    # GET
    return render_template("addtask.html")


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        abort(404)

    tasks.remove(task)
    # redirect back to the page that sent us here, or task list as fallback
    return redirect(request.referrer or url_for("task_list"))


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


# Routes: Insights & timer

@app.route("/insights")
def insights():
    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    # For now, fake focus time
    focus_time = "1h 25m"

    return render_template(
        "insights.html",
        total_tasks=total,
        completed_tasks=completed,
        focus_time=focus_time,
    )


@app.route("/timer")
def timer():
    return render_template("timer.html")


@app.route("/break")
def break_page():
    return render_template("break.html")

# Entry point

if __name__ == "__main__":
    app.run(debug=True)
