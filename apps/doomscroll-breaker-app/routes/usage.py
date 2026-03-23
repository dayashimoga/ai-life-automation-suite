from fastapi import APIRouter
from pydantic import BaseModel
from models.usage import Alert, FocusSession, UsageRequest
from services.tracker import tracker
from typing import List
from services.analyzer import analyzer
from services.predictive_ai import predictor
from datetime import datetime
from uuid import uuid4

router = APIRouter()

active_sessions: List[FocusSession] = []


class FocusRequest(BaseModel):
    duration_minutes: int
    app_to_block: str


@router.post("/track")
async def track_usage(req: UsageRequest):
    analyzer.process_session(req)
    record = tracker.log_usage(req.app_name, req.minutes)
    return record


@router.get("/alerts", response_model=List[Alert])
async def get_alerts():
    return tracker.get_alerts()


@router.post("/predict")
async def predict_risk(req: UsageRequest):
    return predictor.predict_risk(req)


@router.post("/focus", response_model=FocusSession)
async def start_focus_session(req: FocusRequest):
    session = FocusSession(
        id=str(uuid4()),
        duration_minutes=req.duration_minutes,
        is_active=True,
        started_at=datetime.utcnow(),
        app_blocked=req.app_to_block,
    )
    active_sessions.append(session)
    return session


@router.get("/focus", response_model=List[FocusSession])
async def get_active_sessions():
    return [s for s in active_sessions if s.is_active]


@router.get("/analytics")
async def get_usage_analytics():
    """Return aggregate usage analytics from the adaptive ML predictor."""
    return predictor.get_usage_analytics()


@router.get("/monitor")
async def system_monitor():
    """Cross-platform system process monitor for app usage detection."""
    import subprocess
    import platform
    import json

    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object ProcessName, Id, CPU | ConvertTo-Json",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                processes = json.loads(result.stdout) if result.stdout.strip() else []
                if isinstance(processes, dict):
                    processes = [processes]
                return {
                    "active_apps": [
                        {"name": p.get("ProcessName", ""), "pid": p.get("Id", 0)}
                        for p in processes[:20]
                    ]
                }
        else:
            result = subprocess.run(
                ["ps", "aux", "--sort=-%cpu"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:21]
                apps = []
                for line in lines:
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        apps.append({"name": parts[10][:60], "pid": int(parts[1])})
                return {"active_apps": apps}
    except Exception:
        pass
    return {"active_apps": [], "error": "System monitor unavailable"}


# ─── Phase 2: Daily/Weekly Reports ─────────────────────

APP_CATEGORIES = {
    "instagram": "Social",
    "twitter": "Social",
    "tiktok": "Social",
    "facebook": "Social",
    "reddit": "Social",
    "youtube": "Entertainment",
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "vscode": "Productivity",
    "slack": "Productivity",
    "teams": "Productivity",
    "notion": "Productivity",
    "chrome": "Browsing",
    "firefox": "Browsing",
    "safari": "Browsing",
}


@router.get("/report/daily")
async def daily_report():
    """Generate a daily screen time summary with category breakdown."""

    today = datetime.utcnow().date()
    today_records = [r for r in tracker.usage_records if r.timestamp.date() == today]

    # Aggregate by app
    app_totals = {}
    for r in today_records:
        app_totals[r.app_name] = app_totals.get(r.app_name, 0) + r.minutes_used

    # Category breakdown
    category_totals = {}
    for app, minutes in app_totals.items():
        cat = APP_CATEGORIES.get(app.lower(), "Other")
        category_totals[cat] = category_totals.get(cat, 0) + minutes

    total_minutes = sum(app_totals.values())
    top_apps = sorted(app_totals.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "date": str(today),
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 1),
        "top_apps": [{"app": a, "minutes": m} for a, m in top_apps],
        "categories": category_totals,
        "alert_count": len([a for a in tracker.alerts if a.timestamp.date() == today]),
    }


@router.get("/report/weekly")
async def weekly_report():
    """Generate weekly screen time trends with day-over-day comparison."""
    from datetime import timedelta

    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    daily_totals = {}
    for r in tracker.usage_records:
        d = r.timestamp.date()
        if d >= week_ago:
            day_str = str(d)
            daily_totals[day_str] = daily_totals.get(day_str, 0) + r.minutes_used

    total = sum(daily_totals.values())
    avg_daily = round(total / max(len(daily_totals), 1), 1)

    return {
        "period": f"{week_ago} to {today}",
        "daily_breakdown": daily_totals,
        "total_minutes": total,
        "average_daily_minutes": avg_daily,
        "trend": "improving" if avg_daily < 120 else "needs_attention",
    }


# ─── Phase 2: Pomodoro Timer ─────────────────────


@router.post("/pomodoro")
async def start_pomodoro(cycles: int = 4, work_min: int = 25, break_min: int = 5):
    """Create a Pomodoro cycle plan with sequential focus sessions."""
    sessions = []
    for i in range(cycles):
        sessions.append(
            {
                "cycle": i + 1,
                "work_minutes": work_min,
                "break_minutes": break_min if i < cycles - 1 else 15,
                "type": "work" if i % 2 == 0 else "work",
            }
        )
    return {
        "total_cycles": cycles,
        "total_work_minutes": work_min * cycles,
        "total_break_minutes": break_min * (cycles - 1) + 15,
        "sessions": sessions,
    }
