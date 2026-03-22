from fastapi import APIRouter
from datetime import datetime
from models.habit import HabitLog, HabitScore, HabitInsight
from core.database import log_habit
from services.tracker import get_all_scores
from services.insights import generate_insights
from services.correlation import compute_correlations
from typing import List

router = APIRouter()


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
