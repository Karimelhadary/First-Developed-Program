This is the repo for the project
# Task Management System (Flask + MongoDB)

## Overview
This project is a Flask web app that helps users:
- Register/login securely (salt + pepper hashed passwords)
- Add, edit, delete and complete tasks
- Group tasks into **Projects** and label them with **Tags**
- Track mood (onboarding) and view personalized **Insights**
- Use a Pomodoro-style **Focus Timer** and **Break Timer** with session logging

The application was improved to match the assessment rubric:
- Consistent user scoping (`user_id`) across all features
- Proper CRUD flows (Tasks + Projects)
- Clear GET/POST API endpoints for session logging + analytics
- Multiple meaningful MongoDB collections (users, tasks, projects, tags, moods, focus_sessions, break_sessions, settings, audit_logs)
- JavaScript interactive elements (timers, analytics charts)

## Tech Stack
- **Backend:** Flask
- **Database:** MongoDB (PyMongo)
- **Front-end:** HTML, CSS, Bootstrap 5, vanilla JavaScript
- **Charts:** Chart.js

## Setup Instructions
### 1) Prerequisites
- Python 3.10+
- MongoDB running locally (`mongodb://localhost:27017/`)

### 2) Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3) Run the app
```bash
python app.py
```
Open the app at:
- `http://127.0.0.1:5000/`

## Core Routes
### Pages (GET)
- `/` splash
- `/login`, `/register`, `/logout`
- `/onboarding` mood selection
- `/dashboard`
- `/tasklist`, `/addtask`, `/tasks/<id>/edit`
- `/projects`, `/projects/new`, `/projects/<id>/edit`
- `/timer`, `/break`
- `/insights`
- `/settings`

### APIs
- `GET /api/settings` (timer defaults)
- `POST /api/focus-sessions` (log a focus session)
- `POST /api/break-sessions` (log a break session)
- `GET /api/focus-sessions` (last 10 focus sessions)
- `GET /api/insights` (stats for Insights page)

## Database Collections
- `users`
- `tasks`
- `projects`
- `tags`
- `moods`
- `focus_sessions`
- `break_sessions`
- `settings`
- `audit_logs`

## Team Roles (fill in)
- **Backend/Database:** <name>
- **Front-end/UI:** <name>
- **Testing/Docs/Presentation:** <name>

## Notes
- Passwords are hashed using SHA-256 with a per-user salt and a server-side pepper.
- All data is scoped to the logged-in user via `session["user_id"]`.
