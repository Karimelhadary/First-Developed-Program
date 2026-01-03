from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    session,
)

from model.user_model import verify_user, create_user, find_user_by_email

login_bp = Blueprint("login_bp", __name__)


# ---------- LOGIN ----------
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    email_value = ""

    if request.method == "POST":
        email = request.form["email"].lower().strip()
        password = request.form["password"]
        email_value = email

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
@login_bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    name_value = ""
    email_value = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        name_value = name
        email_value = email

        # Input validation
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
@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_bp.login"))
