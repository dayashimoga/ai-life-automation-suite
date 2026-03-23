from fastapi import APIRouter
from datetime import datetime
from models.habit import HabitLog, HabitScore, HabitInsight
from core.database import log_habit
from services.tracker import get_all_scores
from services.insights import generate_insights
from services.correlation import compute_correlations
from services.badges import get_badges, generate_streak_card
from typing import List

router = APIRouter()

HABIT_TEMPLATES = [
    {
        "id": "hydration",
        "name": "💧 Stay Hydrated",
        "habit_name": "drink_water",
        "description": "Drink a glass of water every 2 hours",
        "frequency": "8x daily",
    },
    {
        "id": "stretch",
        "name": "🧘 Quick Stretch",
        "habit_name": "stretch",
        "description": "30-second stretch to release tension",
        "frequency": "Every 2 hours",
    },
    {
        "id": "walk",
        "name": "🚶 5-Min Walk",
        "habit_name": "walk",
        "description": "A 5-minute walk to reset your brain",
        "frequency": "3x daily",
    },
    {
        "id": "meditation",
        "name": "🧠 Mindful Minute",
        "habit_name": "meditate",
        "description": "1-minute breathing exercise for clarity",
        "frequency": "Morning & evening",
    },
    {
        "id": "reading",
        "name": "📖 Read 10 Pages",
        "habit_name": "read",
        "description": "Read 10 pages of any book",
        "frequency": "Daily",
    },
    {
        "id": "gratitude",
        "name": "🙏 Gratitude Log",
        "habit_name": "gratitude",
        "description": "Write 3 things you're grateful for",
        "frequency": "Every evening",
    },
    {
        "id": "screen_break",
        "name": "👁️ Screen Break",
        "habit_name": "screen_break",
        "description": "Look away from screen for 20 seconds",
        "frequency": "Every 20 minutes",
    },
]


@router.post("/log")
async def log_micro_habit(entry: HabitLog):
    ts = entry.timestamp or datetime.utcnow()
    log_habit(entry.habit_name, ts.isoformat())
    return {"status": "logged", "habit": entry.habit_name, "timestamp": ts.isoformat()}


@router.get("/score", response_model=List[HabitScore])
async def get_scores():
    scores = get_all_scores()
    return [
        HabitScore(
            habit_name=s["habit_name"],
            raw_score=s["raw_score"],
            decayed_score=s["decayed_score"],
            streak_days=s["streak_days"],
            last_logged=s.get("last_logged"),
        )
        for s in scores
    ]


@router.get("/insights", response_model=List[HabitInsight])
async def get_insights():
    insights = generate_insights()
    return [
        HabitInsight(
            habit_name=i["habit_name"],
            status=i["status"],
            nudge=i.get("nudge"),
            streak_days=i["streak_days"],
            total_logs=i["total_logs"],
        )
        for i in insights
    ]


@router.get("/correlations")
async def get_correlations():
    """Cross-app correlation analysis — habit patterns vs outcomes."""
    return compute_correlations()


@router.get("/badges")
async def get_all_badges():
    """Gamification: list all earned and in-progress achievement badges."""
    return get_badges()


@router.get("/streak/{habit_name}")
async def get_streak_card(habit_name: str):
    """Generate a shareable streak card for a specific habit."""
    return generate_streak_card(habit_name)


@router.get("/templates")
async def get_templates():
    """Pre-built habit templates for one-click activation."""
    return {"templates": HABIT_TEMPLATES, "total": len(HABIT_TEMPLATES)}


@router.post("/templates/{template_id}/activate")
async def activate_template(template_id: str):
    """Activate a habit template and log the first entry."""
    template = next((t for t in HABIT_TEMPLATES if t["id"] == template_id), None)
    if not template:
        return {"error": f"Template '{template_id}' not found"}

    ts = datetime.utcnow()
    log_habit(template["habit_name"], ts.isoformat())
    return {
        "status": "activated",
        "template": template,
        "first_log": ts.isoformat(),
    }
