from flask import render_template
from app import app

@app.route("/")
@app.route("/splash")
@app.route("/splash.html")
def splash():
    return render_template("splash.html")
