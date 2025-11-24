from flask import Blueprint, render_template

timer_break_bp = Blueprint("timer_break_bp", __name__)

@timer_break_bp.route("/timer")
@timer_break_bp.route("/timer.html")
def timer():
    return render_template("timer.html")


@timer_break_bp.route("/break")
@timer_break_bp.route("/break.html")
def break_page():
    return render_template("break.html")
