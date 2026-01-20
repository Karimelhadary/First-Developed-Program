# Import Flask utilities: Blueprint for route grouping, render_template for HTML rendering, redirect for URL redirection,
# request for handling form data, url_for for URL generation, session for user session management
from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    url_for,
    session,
)

# Import user model functions: verify_user for authentication, create_user for registration, find_user_by_email for user lookup
from model.user_model import verify_user, create_user, find_user_by_email

# Create Blueprint for login-related routes
login_bp = Blueprint("login_bp", __name__)


# Route for login page, handles both GET (show form) and POST (process login)
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    # Initialize error message and email value for form repopulation
    error = None
    email_value = ""

    # Check if the request is a POST (form submission)
    if request.method == "POST":
        # Get and normalize email from form
        email = request.form["email"].lower().strip()
        # Get password from form
        password = request.form["password"]
        # Store email for form repopulation on error
        email_value = email

        # Verify user credentials using the user model
        if verify_user(email, password):
            # If valid, get user document
            user = find_user_by_email(email)
            # Store user info in session
            session["user_id"] = str(user["_id"])
            session["user_email"] = user["email"]
            session["user_name"] = user.get("name", "User")
            # Redirect to next URL or onboarding
            return redirect(request.args.get("next") or url_for("onboarding_bp.onboarding"))
        else:
            # Set error message for invalid credentials
            error = "Invalid credentials"

    # Render login template with error and email value
    return render_template("login.html", error=error, email=email_value)


# Route for registration page, handles both GET and POST
@login_bp.route("/register", methods=["GET", "POST"])
def register():
    # Initialize error and form values
    error = None
    name_value = ""
    email_value = ""

    # Handle POST request (form submission)
    if request.method == "POST":
        # Get form data, with defaults
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        # Store values for form repopulation
        name_value = name
        email_value = email

        # Validate inputs
        if not email or not password:
            error = "Email and password are required."
        elif password != confirm:
            error = "Passwords do not match."
        elif find_user_by_email(email):
            error = "An account with that email already exists."
        else:
            # Create new user
            user_id = create_user(name, email, password)
            # Set session data
            session["user_id"] = user_id
            session["user_email"] = email
            session["user_name"] = name or "User"
            # Redirect to onboarding
            return redirect(url_for("onboarding_bp.onboarding"))

    # Render register template with error and form values
    return render_template(
        "register.html",
        error=error,
        name=name_value,
        email=email_value,
    )


# Route for logout
@login_bp.route("/logout")
def logout():
    # Clear all session data
    session.clear()
    # Redirect to login page
    return redirect(url_for("login_bp.login"))
