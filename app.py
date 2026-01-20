
# Import the 'os' module to access environment variables and operating system functionality
import os
# Import the Flask class from the flask module to create a web application
from flask import Flask
# Import MongoClient from pymongo to connect to a MongoDB database
from pymongo import MongoClient

# Define a function named 'create_app' that sets up and returns a Flask application instance
def create_app():
    # Create a new Flask application instance with the current module's name
    app = Flask(__name__)

    # Retrieve the secret key from environment variables, or use a default development key if not set
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Retrieve the MongoDB URI from environment variables, or use a default local MongoDB URI
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    # Retrieve the database name from environment variables, or use 'task_manager_database' as default
    db_name = os.environ.get("MONGO_DB_NAME", "task_manager_database")

    # Create a MongoClient instance to connect to the MongoDB server using the URI
    client = MongoClient(mongo_uri)
    # Assign the database to the app instance for easy access throughout the application
    app.db = client[db_name]

    # Assign the 'users' collection to the app for storing user data
    app.users = app.db["users"]
    # Assign the 'tasks' collection to the app for storing task data
    app.tasks = app.db["tasks"]
    # Assign the 'moods' collection to the app for storing mood data
    app.moods = app.db["moods"]

    # Assign the 'focus_sessions' collection to the app for storing focus session data
    app.focus_sessions = app.db["focus_sessions"]
    # Assign the 'break_sessions' collection to the app for storing break session data
    app.break_sessions = app.db["break_sessions"]

    # Assign the 'projects' collection to the app for storing project data
    app.projects = app.db["projects"]
    # Assign the 'tags' collection to the app for storing tag data
    app.tags = app.db["tags"]
    # Assign the 'settings' collection to the app for storing user settings
    app.settings = app.db["settings"]
    # Assign the 'audit_logs' collection to the app for storing audit log data
    app.audit_logs = app.db["audit_logs"]

    # Set a pepper value in the app config for additional security in hashing
    app.config["PEPPER"] = os.environ.get("PEPPER", "MY_SUPER_SECRET_KEY_123")

    # Import the dashboard blueprint from the routes module
    from routes.dashboard import dashboard_bp
    # Import the login blueprint
    from routes.login import login_bp
    # Import the onboarding blueprint
    from routes.onboarding import onboarding_bp
    # Import the splash blueprint
    from routes.splash import splash_bp
    # Import the tasks blueprint
    from routes.tasks import tasks_bp
    # Import the insights blueprint
    from routes.insights import insights_bp
    # Import the timer_break blueprint
    from routes.timer_break import timer_break_bp
    # Import the projects blueprint
    from routes.projects import projects_bp
    # Import the settings blueprint
    from routes.settings import settings_bp

    # Register the splash blueprint with the app
    app.register_blueprint(splash_bp)
    # Register the login blueprint
    app.register_blueprint(login_bp)
    # Register the onboarding blueprint
    app.register_blueprint(onboarding_bp)
    # Register the dashboard blueprint
    app.register_blueprint(dashboard_bp)
    # Register the tasks blueprint
    app.register_blueprint(tasks_bp)
    # Register the insights blueprint
    app.register_blueprint(insights_bp)
    # Register the timer_break blueprint
    app.register_blueprint(timer_break_bp)
    # Register the projects blueprint
    app.register_blueprint(projects_bp)
    # Register the settings blueprint
    app.register_blueprint(settings_bp)

    # Return the configured Flask app instance
    return app

# Check if this script is being run directly (not imported as a module)
if __name__ == "__main__":
    # Create the app instance by calling the create_app function
    app = create_app()
    # Get the debug flag from environment, default to True (1 means debug on)
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    # Run the Flask app with the debug setting
    app.run(debug=debug)
