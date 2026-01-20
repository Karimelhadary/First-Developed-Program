# TaskManager (Flask + MongoDB)

A productivity web app with:
- Auth (register/login/logout)
- Tasks (CRUD, sorting, completion)
- Projects (CRUD, group tasks)
- Tags (reusable labels)
- Mood onboarding (dashboard sorting changes)
- Pomodoro timer + breaks (sessions saved)
- Insights dashboard (based on logged sessions)

## Requirements
- Python 3.10+
- MongoDB running locally (default: mongodb://localhost:27017/)

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python app.py
```

## Code Structure
- `app.py`: Main Flask application file, sets up the app, database connections, and registers blueprints
- `model/`: Contains data models for users, tasks, projects, tags
  - `user_model.py`: Handles user authentication and registration
  - `task_model.py`: Manages task CRUD operations, sorting, and completion
  - `project_model.py`: Handles project creation, updating, deletion
  - `tag_model.py`: Manages reusable tags for tasks
- `routes/`: Flask blueprints for different pages
  - `login.py`: Login and registration routes
  - `dashboard.py`: Main dashboard with mood selection and task display
  - `tasks.py`: Task list, add, edit, delete routes
  - `projects.py`: Project management routes
  - `timer_break.py`: Pomodoro timer and break functionality
  - `insights.py`: Analytics dashboard
  - `settings.py`: User settings page
  - `onboarding.py`: Initial user setup
  - `splash.py`: Landing page
- `static/`: CSS and JS files
  - CSS files for styling each page
  - JS files for client-side functionality like timers and theme toggles
- `templates/`: HTML templates using Jinja2
  - `base.html`: Base template with navigation and layout
  - Other HTML files for specific pages
- `utils/`: Utility modules
  - `auth.py`: Authentication decorator
  - `security.py`: Password hashing and verification
- `requirements.txt`: Python dependencies
