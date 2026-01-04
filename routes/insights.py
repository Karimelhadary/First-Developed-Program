from __future__ import annotations

from datetime import datetime, timedelta
from flask import Blueprint, render_template, session, jsonify, current_app
from utils.auth import login_required

insights_bp = Blueprint("insights_bp", __name__)


def _insights_payload(user_id: str) -> dict:
    # -------- Tasks --------
    total = current_app.db["tasks"].count_documents({"user_id": user_id})
    completed = current_app.db["tasks"].count_documents({"user_id": user_id, "completed": True})
    remaining = max(total - completed, 0)
    progress_pct = int(round((completed / total) * 100)) if total > 0 else 0

    # -------- Timer sessions --------
    focus_docs = list(current_app.db["focus_sessions"].find({"user_id": user_id}))
    break_docs = list(current_app.db["break_sessions"].find({"user_id": user_id}))

    focus_minutes = sum(int(d.get("minutes", 0) or 0) for d in focus_docs)
    break_minutes = sum(int(d.get("minutes", 0) or 0) for d in break_docs)

    # -------- Mood logs --------
    mood_logs_count = current_app.db["moods"].count_documents({"user_id": user_id})

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
                per[day] += int(doc.get("minutes", 0) or 0)
        return [per[d] for d in days]

    focus_series = sum_by_day(focus_docs)
    break_series = sum_by_day(break_docs)

    # IMPORTANT: return the exact keys insights.html expects
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
        },
        "mood": {"logs": mood_logs_count},
        "charts": {
            "labels": labels,
            "focus_minutes": focus_series,
            "break_minutes": break_series,
        },
    }


@insights_bp.route("/insights")
@login_required
def insights():
    return render_template("insights.html")


@insights_bp.route("/api/insights")
@login_required
def insights_api():
    user_id = session.get("user_id")
    return jsonify(_insights_payload(user_id))
