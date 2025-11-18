from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)

# ------------------------
# In-memory "database"
# ------------------------

class Task:
    def __init__(self, id, title, description, due_date,
                 importance, complexity, energy, completed=False):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date        # "YYYY-MM-DD" string
        self.importance = importance    # "Low" | "Medium" | "High"
        self.complexity = complexity    # int 1–5
        self.energy = energy            # int 1–5
        self.completed = completed      # bool


tasks = []          # list[Task]
_next_id = 1        # simple counter


def get_next_id():
    global _next_id
    current = _next_id
    _next_id += 1
    return current


def find_task(task_id: int):
    for t in tasks:
        if t.id == task_id:
            return t
    return None


# ------------------------
# Routes: Splash / Home
# ------------------------

@app.route("/")
@app.route("/splash")
@app.route("/splash.html")   # so /splash.html also works
def splash():
    return render_template("splash.html")


# ------------------------
# Routes: Login & Onboarding
# ------------------------

@app.route("/login", methods=["GET", "POST"])
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # no real auth for now – just go to onboarding
        if not email or not password:
            return render_template("login.html", error="Please enter email and password.")
        return redirect(url_for("onboarding"))
    return render_template("login.html")


@app.route("/onboarding", methods=["GET", "POST"])
@app.route("/onboarding.html", methods=["GET", "POST"])
def onboarding():
    if request.method == "POST":
        mood = request.form.get("mood", "focused")
        # pass mood as query param to dashboard (optional)
        return redirect(url_for("dashboard", mood=mood))

    selected_mood = request.args.get("mood", "focused")
    return render_template("onboarding.html", selected_mood=selected_mood)


# ------------------------
# Routes: Dashboard
# ------------------------

@app.route("/dashboard")
@app.route("/dashboard.html")
def dashboard():
    mood = request.args.get("mood", "focused")
    # For now: just show all tasks; you could filter by mood later.
    return render_template("dashboard.html", tasks=tasks, mood=mood)


# ------------------------
# Routes: Tasks (list, add, edit, delete)
# ------------------------

@app.route("/tasklist")
@app.route("/tasklist.html")
def task_list():
    # later you can add sort_by from query params
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
            # re-render with an error (optional)
            return render_template(
                "addtask.html",
                task=None,
                editing=False,
                error="Title and due date are required.",
            )

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
        return redirect(url_for("dashboard"))

    # GET – new task
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

    # GET – edit form prefilled
    return render_template("addtask.html", task=task, editing=True)


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        abort(404)

    tasks.remove(task)
    # go back to task list (or previous page)
    return redirect(url_for("task_list"))


# ------------------------
# Routes: Insights, Timer & Break
# ------------------------

@app.route("/insights")
@app.route("/insights.html")
def insights():
    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    # dummy focus time for now
    focus_time = "1h 25m"

    return render_template(
        "insights.html",
        total_tasks=total,
        completed_tasks=completed,
        focus_time=focus_time,
    )


@app.route("/timer")
@app.route("/timer.html")
def timer():
    return render_template("timer.html")


@app.route("/break")
@app.route("/break.html")
def break_page():
    return render_template("break.html")


# ------------------------
# Entrypoint
# ------------------------

if __name__ == "__main__":
    app.run(debug=True)
