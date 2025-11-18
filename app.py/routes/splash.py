from flask import Blueprint, render_template

splash_bp = Blueprint("splash_bp", __name__)

@splash_bp.route("/")
@splash_bp.route("/splash")
@splash_bp.route("/splash.html")
def splash():
    return render_template("splash.html")
