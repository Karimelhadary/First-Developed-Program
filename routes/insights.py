from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, render_template, session, jsonify, current_app
from utils.auth import login_required

insights_bp = Blueprint("insights_bp", __name__)


def _col(name: str):
    # Supports both styles: current_app.db["x"] or current_app.x
    if hasattr(current_app, "db"):
        return current_app.db[name]
    return getattr(current_app, name)


def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _insights_payload(user_id: str) -> dict:
    tasks_col = _col("tasks")
    focus_col = _col("focus_sessions")
    break_col = _col("break_sessions")
    moods_col = _col("moods")
    projects_col = _col("projects")

    # -------- Tasks summary --------
    total = tasks_col.count_documents({"user_id": user_id})
    completed = tasks_col.count_documents({"user_id": user_id, "completed": True})
    remaining = max(total - completed, 0)
    progress_pct = int(round((completed / total) * 100)) if total > 0 else 0

    # -------- Timer sessions totals --------
    focus_docs = list(focus_col.find({"user_id": user_id}))
    break_docs = list(break_col.find({"user_id": user_id}))

    focus_minutes = sum(_safe_int(d.get("minutes", 0)) for d in focus_docs)
    break_minutes = sum(_safe_int(d.get("minutes", 0)) for d in break_docs)

    # -------- Mood logs --------
    mood_logs_count = moods_col.count_documents({"user_id": user_id})

    # -------- Chart: last 7 days focus/break minutes --------
    today = datetime.utcnow().date()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    labels = [d.strftime("%a") for d in days]

    def sum_by_day(docs):
        per = {d: 0 for d in days}
        for doc in docs:
            dt = doc.get("created_at")
            if not dt:
                continue
            try:
                day = dt.date()
            except Exception:
                continue
            if day in per:
                per[day] += _safe_int(doc.get("minutes", 0))
        return [per[d] for d in days]

    focus_series = sum_by_day(focus_docs)
    break_series = sum_by_day(break_docs)

    # -------- NEW: Focus by task (so "Link to task" has a purpose) --------
    task_minutes = defaultdict(int)
    task_sessions = defaultdict(int)
    unlinked_minutes = 0
    unlinked_sessions = 0

    for s in focus_docs:
        mins = _safe_int(s.get("minutes", 0))
        tid = s.get("task_id")
        if tid:
            task_minutes[tid] += mins
            task_sessions[tid] += 1
        else:
            unlinked_minutes += mins
            unlinked_sessions += 1

    # Load task titles + project_id for those tasks
    task_ids = list(task_minutes.keys())
    task_docs = list(tasks_col.find({"user_id": user_id, "_id": {"$in": [__import__("bson").ObjectId(t) for t in task_ids if _looks_like_objectid(t)]}})) if task_ids else []
    # If your focus_sessions stores task_id as string (not ObjectId), we also try string matching:
    task_docs += list(tasks_col.find({"user_id": user_id, "_id": {"$in": []}}))  # no-op, keeps structure stable

    # Because your tasks model converts IDs to strings for templates, in Mongo _id is ObjectId.
    # We'll map by string(ObjectId).
    tasks_by_id = {str(d["_id"]): d for d in task_docs}

    # Projects map
    projects = list(projects_col.find({"user_id": user_id}))
    project_name = {str(p["_id"]): p.get("name", "Untitled") for p in projects}

    top_tasks = []
    for tid, mins in sorted(task_minutes.items(), key=lambda x: x[1], reverse=True)[:8]:
        doc = tasks_by_id.get(tid)
        title = doc.get("title") if doc else "Deleted task"
        pid = (doc.get("project_id") if doc else None) or None
        top_tasks.append(
            {
                "task_id": tid,
                "title": title,
                "minutes": mins,
                "sessions": task_sessions.get(tid, 0),
                "project": project_name.get(pid, "No project") if pid else "No project",
            }
        )

    # -------- NEW: Project stats (so Projects feel real) --------
    project_stats = []
    for p in projects:
        pid = str(p["_id"])
        p_tasks = list(tasks_col.find({"user_id": user_id, "project_id": pid}))
        p_total = len(p_tasks)
        p_done = sum(1 for t in p_tasks if t.get("completed") is True)

        # sum focus minutes for tasks inside this project
        p_task_ids = {str(t["_id"]) for t in p_tasks}
        p_focus_minutes = sum(task_minutes.get(tid, 0) for tid in p_task_ids)

        project_stats.append(
            {
                "project_id": pid,
                "name": p.get("name", "Untitled"),
                "tasks_total": p_total,
                "tasks_done": p_done,
                "focus_minutes": p_focus_minutes,
            }
        )

    project_stats.sort(key=lambda x: x["focus_minutes"], reverse=True)

    return {
        "tasks": {
            "total": total,
            "completed": completed,
            "remaining": remaining,
            "progress_pct": progress_pct,
        },
        "timer": {
            "focus_minutes": focus_minutes,
            "focus_sessions": len(focus_docs),
            "break_minutes": break_minutes,
            "break_sessions": len(break_docs),
            "unlinked_focus_minutes": unlinked_minutes,
            "unlinked_focus_sessions": unlinked_sessions,
        },
        "mood": {"logs": mood_logs_count},
        "charts": {
            "labels": labels,
            "focus_minutes": focus_series,
            "break_minutes": break_series,
        },
        "top_tasks": top_tasks,
        "projects": project_stats[:8],
    }


def _looks_like_objectid(s: str) -> bool:
    if not isinstance(s, str) or len(s) != 24:
        return False
    try:
        int(s, 16)
        return True
    except Exception:
        return False


@insights_bp.route("/insights")
@login_required
def insights():
    return render_template("insights.html")


@insights_bp.route("/api/insights")
@login_required
def insights_api():
    user_id = session.get("user_id")
    return jsonify(_insights_payload(user_id))
