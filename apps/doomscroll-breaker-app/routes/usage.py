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
    """Lightweight system process monitor for app usage detection."""
    import subprocess
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object ProcessName, Id, CPU | ConvertTo-Json"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            import json
            processes = json.loads(result.stdout) if result.stdout.strip() else []
            if isinstance(processes, dict):
                processes = [processes]
            return {"active_apps": [{"name": p.get("ProcessName", ""), "pid": p.get("Id", 0)} for p in processes[:20]]}
    except Exception:
        pass
    return {"active_apps": [], "error": "System monitor unavailable"}
