from flask import render_template, request, redirect, url_for
from main import app

@app.route("/login", methods=["GET", "POST"])
@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Please enter email and password.")

        return redirect(url_for("onboarding"))

    return render_template("login.html")


@app.route("/onboarding", methods=["GET", "POST"])
@app.route("/onboarding.html", methods=["GET", "POST"])
def onboarding():
    if request.method == "POST":
        mood = request.form.get("mood", "focused")
        return redirect(url_for("dashboard", mood=mood))

    return render_template("onboarding.html", selected_mood=request.args.get("mood", "focused"))
