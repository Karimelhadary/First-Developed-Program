

# --- Imports used in this file (what we need from libraries/modules) ---
from flask import Blueprint, render_template



# Blueprint groups related routes into a reusable module
splash_bp = Blueprint("splash_bp", __name__)

# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@splash_bp.route("/")
# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@splash_bp.route("/splash")
# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@splash_bp.route("/splash.html")
# Function: splash (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: splash
# What happens here: inputs -> logic -> output/return
# -------------------------------
def splash():
    return render_template("splash.html")
