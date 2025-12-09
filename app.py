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

    # Collections
    app.users = app.db["users"]
    app.tasks = app.db["tasks"]
    app.moods = app.db["moods"]               # Stores onboarding mood logs
    app.focus_sessions = app.db["focus_sessions"]  # Stores timer sessions

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

    app.register_blueprint(splash_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(timer_break_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
