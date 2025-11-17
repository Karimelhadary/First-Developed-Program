from flask import render_template, request
from app import app
from data import tasks

@app.route("/dashboard")
@app.route("/dashboard.html")
def dashboard():
    mood = request.args.get("mood", "focused")
    return render_template("dashboard.html", tasks=tasks, mood=mood)
