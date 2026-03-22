from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class HabitLog(BaseModel):
    habit_name: str  # e.g. "drink_water", "stretch", "walk"
    timestamp: Optional[datetime] = None


class HabitScore(BaseModel):
    habit_name: str
    raw_score: float
    decayed_score: float
    streak_days: int
    last_logged: Optional[str] = None


class HabitInsight(BaseModel):
    habit_name: str
    status: str  # "strong", "moderate", "decaying", "critical"
    nudge: Optional[str] = None
    streak_days: int
    total_logs: int
