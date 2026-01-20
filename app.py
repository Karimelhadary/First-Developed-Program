
import os
from flask import Flask
from pymongo import MongoClient



# Function: create_app (reads input, applies logic, returns response/value)
def create_app():
    app = Flask(__name__)

    # -----------------------
    #  Config (ENV first)
    # -----------------------
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.environ.get("MONGO_DB_NAME", "task_manager_database")

    # -----------------------
    #  MongoDB connection
    # -----------------------
    client = MongoClient(mongo_uri)
    app.db = client[db_name]

    # Collections
# MongoDB operation: read/write data in a collection
    app.users = app.db["users"]
# MongoDB operation: read/write data in a collection
    app.tasks = app.db["tasks"]
# MongoDB operation: read/write data in a collection
    app.moods = app.db["moods"]

# MongoDB operation: read/write data in a collection
    app.focus_sessions = app.db["focus_sessions"]
# MongoDB operation: read/write data in a collection
    app.break_sessions = app.db["break_sessions"]

# MongoDB operation: read/write data in a collection
    app.projects = app.db["projects"]
# MongoDB operation: read/write data in a collection
    app.tags = app.db["tags"]
# MongoDB operation: read/write data in a collection
    app.settings = app.db["settings"]
# MongoDB operation: read/write data in a collection
    app.audit_logs = app.db["audit_logs"]

    # -----------------------
    #  Security Pepper
    # -----------------------
    app.config["PEPPER"] = os.environ.get("PEPPER", "MY_SUPER_SECRET_KEY_123")

    # -----------------------
    #  Register Blueprints
    # -----------------------
    from routes.dashboard import dashboard_bp
    from routes.login import login_bp
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


# Entry point: this block runs only when you execute this file directly
if __name__ == "__main__":
    app = create_app()
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug)
