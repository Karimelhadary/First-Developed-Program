from flask import Blueprint, render_template, redirect, request, url_for

login_bp = Blueprint("login_bp", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
@login_bp.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("/templates/login.html", error="Please enter email and password.")
        return redirect(url_for("onboarding_bp.onboarding"))

    return render_template("/templates/login.html")
