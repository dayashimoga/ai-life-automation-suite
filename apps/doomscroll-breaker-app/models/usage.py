from pydantic import BaseModel
from datetime import datetime


class AppUsage(BaseModel):
    app_name: str
    minutes_used: int
    timestamp: datetime


class FocusSession(BaseModel):
    id: str
    duration_minutes: int
    is_active: bool
    started_at: datetime
    app_blocked: str


class Alert(BaseModel):
    id: str
    message: str
    timestamp: datetime


class UsageRequest(BaseModel):
    app_name: str
    minutes: int
