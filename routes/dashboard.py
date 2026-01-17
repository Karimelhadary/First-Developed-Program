from __future__ import annotations

from datetime import datetime, date
from collections import defaultdict

from flask import Blueprint, render_template, session, current_app

from model.task_model import get_tasks_for_dashboard
from model.project_model import list_projects
from utils.auth import login_required

dashboard_bp = Blueprint("dashboard_bp", __name__)


def _parse_due(due_str: str):
    if not due_str:
        return None
    try:
        return datetime.strptime(due_str, "%Y-%m-%d").date()
    except Exception:
        return None


def _due_status(d: date | None, today: date):
    if not d:
        return "none", None
    delta = (d - today).days
    if delta < 0:
        return "overdue", delta
    if delta == 0:
        return "today", 0
    if 1 <= delta <= 3:
        return "soon", delta
    return "later", delta


def _importance_class(importance: str):
    if importance == "High":
        return "high"
    if importance == "Medium":
        return "med"
    return "low"


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session.get("user_id")

    mood = session.get("current_mood", "focused")
    mood_labels = {
        "energetic": "⚡ Energetic",
        "focused": "🎯 Focused",
        "calm": "😊 Calm",
        "creative": "✨ Creative",
    }
    mood_label = mood_labels.get(mood, "🎯 Focused")

    tasks = get_tasks_for_dashboard(user_id=user_id, mood=mood)

    projects = list_projects(user_id)
    project_name = {p["id"]: p["name"] for p in projects}

    # focus aggregation per task
    focus_docs = list(current_app.focus_sessions.find({"user_id": user_id}))
    focus_minutes_by_task = defaultdict(int)
    focus_sessions_by_task = defaultdict(int)
    for s in focus_docs:
        tid = s.get("task_id")
        if tid:
            focus_minutes_by_task[tid] += int(s.get("minutes", 0) or 0)
            focus_sessions_by_task[tid] += 1

    today = datetime.utcnow().date()

    enriched = []
    for t in tasks:
        due = _parse_due(t.get("due_date", ""))
        status, days_left = _due_status(due, today)

        tid = t.get("id")
        focus_min = focus_minutes_by_task.get(tid, 0)
        focus_cnt = focus_sessions_by_task.get(tid, 0)

        pid = t.get("project_id")
        p_name = project_name.get(pid, "No project") if pid else "No project"

        importance = t.get("importance", "Low")
        imp_code = _importance_class(importance)

        enriched.append(
            {
                **t,
                "project_name": p_name,
                "due_status": status,
                "days_left": days_left,
                "focus_minutes": focus_min,
                "focus_sessions": focus_cnt,
                "importance_code": imp_code,
            }
        )

    open_tasks = [t for t in enriched if not t.get("completed")]
    done_tasks = [t for t in enriched if t.get("completed")]

    overdue = [t for t in open_tasks if t["due_status"] == "overdue"]
    due_today = [t for t in open_tasks if t["due_status"] == "today"]
    due_soon = [t for t in open_tasks if t["due_status"] == "soon"]

    # ---------- Suggested focus plan ----------
    suggested = sorted(
        open_tasks,
        key=lambda x: (
            0 if x["due_status"] in ("overdue", "today", "soon") else 1,
            0 if x.get("importance") == "High" else 1,
            x.get("due_date", "9999-12-31"),
        ),
    )[:6]

    # ---------- NEW: Smart suggestions that ALWAYS have meaning ----------
    # Quick wins: low complexity + urgent
    quick_wins = sorted(
        [t for t in open_tasks if t["due_status"] in ("overdue", "today", "soon") and int(t.get("complexity", 1)) <= 2],
        key=lambda x: (0 if x["due_status"] == "overdue" else 1, x.get("due_date", "9999-12-31")),
    )[:4]

    # Big rocks: highest complexity tasks (these matter even if low/medium importance)
    big_rocks = sorted(
        [t for t in open_tasks],
        key=lambda x: (int(x.get("complexity", 1)), 0 if x["due_status"] in ("overdue", "today", "soon") else 1),
        reverse=True,
    )[:4]

    # Neglected but urgent: 0 focus minutes and due soon/today
    neglected_urgent = sorted(
        [t for t in open_tasks if (t.get("focus_minutes", 0) == 0) and t["due_status"] in ("overdue", "today", "soon")],
        key=lambda x: (0 if x["due_status"] == "overdue" else 1, x.get("due_date", "9999-12-31")),
    )[:4]

    # Keep your original sections too (still useful)
    high_priority = [t for t in open_tasks if t.get("importance") == "High"][:5]
    neglected = [t for t in open_tasks if (t.get("focus_minutes", 0) == 0)][:5]

    kpis = {
        "open": len(open_tasks),
        "done": len(done_tasks),
        "overdue": len(overdue),
        "due_soon": len(due_today) + len(due_soon),
    }

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "User"),
        mood_label=mood_label,
        kpis=kpis,
        suggested=suggested,
        overdue=overdue[:5],
        due_today=due_today[:5],
        due_soon=due_soon[:5],
        high_priority=high_priority,
        neglected=neglected,
        quick_wins=quick_wins,
        big_rocks=big_rocks,
        neglected_urgent=neglected_urgent,
    )
