
# --- Imports used in this file (what we need from libraries/modules) ---
from flask import (


    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    session,
)

# --- Imports used in this file (what we need from libraries/modules) ---
from model.user_model import verify_user, create_user, find_user_by_email

# Blueprint groups related routes into a reusable module
login_bp = Blueprint("login_bp", __name__)


# ---------- LOGIN ----------
# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_bp.route("/login", methods=["GET", "POST"])
# Function: login (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: login
# What happens here: inputs -> logic -> output/return
# -------------------------------
def login():
    error = None
    email_value = ""

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]
        email_value = email

        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if verify_user(email, password):
            user = find_user_by_email(email)
            session["user_id"] = str(user["_id"])
            session["user_email"] = user["email"]
            session["user_name"] = user.get("name", "User")
            return redirect(request.args.get("next") or url_for("onboarding_bp.onboarding"))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error, email=email_value)


# ---------- REGISTER ----------
# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_bp.route("/register", methods=["GET", "POST"])
# Function: register (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: register
# What happens here: inputs -> logic -> output/return
# -------------------------------
def register():
    error = None
    name_value = ""
    email_value = ""

    # Control-flow: starts a 'if' block (indentation shows what belongs to it).
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        name_value = name
        email_value = email

        # Input validation
        # Control-flow: starts a 'if' block (indentation shows what belongs to it).
        if not email or not password:
            error = "Email and password are required."
        elif password != confirm:
            error = "Passwords do not match."
        elif find_user_by_email(email):
            error = "An account with that email already exists."
        else:
            user_id = create_user(name, email, password)
            session["user_id"] = user_id
            session["user_email"] = email
            session["user_name"] = name or "User"
            return redirect(url_for("onboarding_bp.onboarding"))

    return render_template(
        "register.html",
        error=error,
        name=name_value,
        email=email_value,
    )


# ---------- LOGOUT ----------
# Flask decorator: attaches this function to a URL endpoint / request hook
# Decorator: modifies the function below (commonly registers a route in Flask)
@login_bp.route("/logout")
# Function: logout (reads input, applies logic, returns response/value)

# -------------------------------
# FUNCTION: logout
# What happens here: inputs -> logic -> output/return
# -------------------------------
def logout():
    session.clear()
    return redirect(url_for("login_bp.login"))
