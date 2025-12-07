from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
from datetime import datetime

timer_break_bp = Blueprint("timer_break_bp", __name__)


@timer_break_bp.route("/timer", methods=["GET", "POST"])
def timer():
    if request.method == "POST":
        # minutes from form; default 25 if missing
        try:
            minutes = int(request.form.get("minutes", 25))
        except ValueError:
            minutes = 25

        current_app.focus_sessions.insert_one(
            {
                "user_id": session.get("user_id"),
                "minutes": minutes,
                "created_at": datetime.utcnow(),
            }
        )

        # After logging, just reload the timer page
        return redirect(url_for("timer_break_bp.timer"))

    return render_template("timer.html")


@timer_break_bp.route("/break")
def break_page():
    return render_template("break.html")
