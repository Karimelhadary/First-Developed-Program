from flask import render_template
from app import app
from data import tasks

@app.route("/insights")
@app.route("/insights.html")
def insights():
    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    focus_time = "1h 25m"
    return render_template("insights.html", total_tasks=total, completed_tasks=completed, focus_time=focus_time)

@app.route("/timer")
@app.route("/timer.html")
def timer():
    return render_template("timer.html")

@app.route("/break")
@app.route("/break.html")
def break_page():
    return render_template("break.html")
