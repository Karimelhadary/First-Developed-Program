from flask import Blueprint, render_template, current_app

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    raw_tasks = list(current_app.tasks.find())
    
    # convert MongoDB docs → template-friendly objects
    tasks = []
    for t in raw_tasks:
        tasks.append({
            "id": str(t["_id"]),
            "title": t.get("title", ""),
            "description": t.get("description", ""),
            "due_date": t.get("due_date", ""),
            "importance": t.get("importance", "Low"),
            "complexity": t.get("complexity", 1),
            "energy": t.get("energy", 1),
            "completed": t.get("completed", False)
        })

    return render_template("dashboard.html", tasks=tasks)
