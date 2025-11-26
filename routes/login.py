from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    current_app,
    session,
)
from werkzeug.security import generate_password_hash, check_password_hash

login_bp = Blueprint("login_bp", __name__)


# ---------- LOGIN ----------
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")

        if not email or not password:
            error = "Please fill in both email and password."
        else:
            users = current_app.users
            user = users.find_one({"email": email})

            if not user or not check_password_hash(user.get("password", ""), password):
                error = "Invalid email or password."
            else:
                # login success -> store basic user info in session
                session["user_id"] = str(user["_id"])
                session["user_email"] = user["email"]
                # go to onboarding or dashboard
                return redirect(url_for("onboarding_bp.onboarding"))

    return render_template("login.html", error=error)


# ---------- REGISTER ----------
@login_bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    name = ""
    email = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not email or not password:
            error = "Email and password are required."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            users = current_app.users
            existing = users.find_one({"email": email})
            if existing:
                error = "An account with that email already exists."
            else:
                hashed = generate_password_hash(password)
                result = users.insert_one(
                    {
                        "name": name,
                        "email": email,
                        "password": hashed,
                    }
                )
                # auto-login after registration
                session["user_id"] = str(result.inserted_id)
                session["user_email"] = email
                return redirect(url_for("onboarding_bp.onboarding"))

    return render_template("register.html", error=error, name=name, email=email)


# ---------- LOGOUT ----------
@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_bp.login"))
