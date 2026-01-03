from flask import Flask
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)

    # Secret key - required for sessions
    app.secret_key = "dev-secret-key-change-me"

    # -----------------------
    #  MongoDB connection
    # -----------------------
    client = MongoClient("mongodb://localhost:27017/")
    app.db = client["task_manager_database"]

    # Collections (MongoDB will create them automatically on first insert)
    # Core
    app.users = app.db["users"]
    app.tasks = app.db["tasks"]

    # Mood onboarding logs
    app.moods = app.db["moods"]

    # Pomodoro / break sessions
    app.focus_sessions = app.db["focus_sessions"]
    app.break_sessions = app.db["break_sessions"]

    # Extra collections to meet the "4 per person" requirement + add real purpose
    app.projects = app.db["projects"]         # group tasks into projects
    app.tags = app.db["tags"]                 # reusable labels
    app.settings = app.db["settings"]         # per-user defaults (focus/break length)
    app.audit_logs = app.db["audit_logs"]     # store important actions (CRUD trace)

    # -----------------------
    #  Security Pepper
    # -----------------------
    app.config["PEPPER"] = "MY_SUPER_SECRET_KEY_123"

    # -----------------------
    #  Register Blueprints
    # -----------------------
    from routes.dashboard import dashboard_bp
    from routes.login import login_bp          # login + register + logout
    from routes.onboarding import onboarding_bp
    from routes.splash import splash_bp
    from routes.tasks import tasks_bp
    from routes.insights import insights_bp
    from routes.timer_break import timer_break_bp
    from routes.projects import projects_bp
    from routes.settings import settings_bp

    app.register_blueprint(splash_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(timer_break_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(settings_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
