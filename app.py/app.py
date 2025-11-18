from flask import Flask
from routes.splash import splash_bp
from routes.login import login_bp
from routes.onboarding import onboarding_bp
from routes.dashboard import dashboard_bp
from routes.tasks import tasks_bp
from routes.insights import insights_bp
from routes.timer_break import timer_break_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(splash_bp)
app.register_blueprint(login_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(insights_bp)
app.register_blueprint(timer_break_bp)

if __name__ == "__main__":
    app.run(debug=True)
