from fastapi import FastAPI
from auth import router as auth_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import asyncio
import json
import zipfile
import io
import datetime

app = FastAPI(title="Unified API Gateway Dashboard", version="1.0.0")

# Include auth routes
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services map — configurable via environment variables for cloud deployment
SERVICES = {
    "journal": os.environ.get("JOURNAL_API_URL", "http://localhost:8001"),
    "doomscroll": os.environ.get("DOOMSCROLL_API_URL", "http://localhost:8002"),
    "vision": os.environ.get("VISION_API_URL", "http://localhost:8003"),
    "habit": os.environ.get("HABIT_API_URL", "http://localhost:8004"),
}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "unified-dashboard"}


@app.get("/api/v1/status")
async def get_services_status():
    """Ping all microservices for health status."""
    statuses = {}
    async with httpx.AsyncClient(timeout=1.0) as client:
        for name, url in SERVICES.items():
            try:
                r = await client.get(f"{url}/health")
                statuses[name] = "online" if r.status_code == 200 else "error"
            except httpx.RequestError:
                statuses[name] = "offline"
    return statuses


# Notification Pub/Sub queues
clients = set()


class NotificationPayload(BaseModel):
    title: str
    body: str
    icon: str = "fa-bell"


@app.post("/api/v1/notifications/push")
async def push_notification(payload: NotificationPayload):
    """Internal endpoint for other microservices to trigger a global notification."""
    dead_clients = set()
    for client_queue in clients:
        try:
            client_queue.put_nowait(payload.model_dump())
        except asyncio.QueueFull:
            dead_clients.add(client_queue)

    for c in dead_clients:
        clients.remove(c)

    return {"status": "dispatched", "listeners": len(clients)}


@app.get("/api/v1/notifications/stream")
async def notification_stream():
    """SSE endpoint for the frontend dashboard to listen for pushes."""
    client_queue = asyncio.Queue(maxsize=100)
    clients.add(client_queue)

    async def event_generator():
        try:
            while True:
                data = await client_queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            clients.remove(client_queue)
            raise

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/v1/export")
async def export_data():
    """Dynamically packages all microservice independent SQLite DBs into a single GDPR ZIP."""
    memory_buffer = io.BytesIO()

    # Paths to the independent DBs
    db_paths = {
        "journal_history.db": "../memory-journal-app/history.db",
        "vision_history.db": "../visual-intelligence-app/history.db",
        "doomscroll_history.db": "../doomscroll-breaker-app/history.db",
        "habit_state.db": "../micro-habit-engine/habit_state.db",
    }

    with zipfile.ZipFile(memory_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Also dump a meta summary
        meta = {"version": "1.0", "timestamp": "current"}
        zf.writestr("export_metadata.json", json.dumps(meta, indent=2))

        for name, rel_path in db_paths.items():
            abs_path = os.path.join(os.path.dirname(__file__), rel_path)
            if os.path.exists(abs_path):
                zf.write(abs_path, arcname=name)

    memory_buffer.seek(0)

    return StreamingResponse(
        memory_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=ai_life_suite_export.zip"
        },
    )


@app.get("/api/v1/digest")
async def weekly_digest():
    """Weekly activity digest aggregating data from all microservices."""
    digest = {
        "period": "Last 7 days",
        "services": {},
        "highlights": [],
    }

    async with httpx.AsyncClient(timeout=3.0) as client:
        # Doomscroll weekly report
        try:
            r = await client.get(f"{SERVICES['doomscroll']}/api/v1/usage/report/weekly")
            if r.status_code == 200:
                digest["services"]["doomscroll"] = r.json()
        except httpx.RequestError:
            digest["services"]["doomscroll"] = {"status": "unavailable"}

        # Habit scores
        try:
            r = await client.get(f"{SERVICES['habit']}/api/v1/habit/score")
            if r.status_code == 200:
                scores = r.json()
                digest["services"]["habits"] = {
                    "total_habits": len(scores),
                    "scores": scores[:5],
                }
        except httpx.RequestError:
            digest["services"]["habits"] = {"status": "unavailable"}

        # Journal timeline
        try:
            r = await client.get(f"{SERVICES['journal']}/api/v1/journal/timeline")
            if r.status_code == 200:
                data = r.json()
                digest["services"]["journal"] = {
                    "total_entries": data.get("total", 0),
                }
        except httpx.RequestError:
            digest["services"]["journal"] = {"status": "unavailable"}

        # Vision events
        try:
            r = await client.get(f"{SERVICES['vision']}/api/v1/vision/dashboard")
            if r.status_code == 200:
                digest["services"]["vision"] = r.json()
        except httpx.RequestError:
            digest["services"]["vision"] = {"status": "unavailable"}

    return digest


@app.get("/api/v1/intelligence")
async def cross_app_intelligence():
    """
    The 'Deep Brain' — Cross-app AI intelligence layer.
    Pulls live data from Habit Engine and Doomscroll Breaker to generate
    real-time behavioral correlation insights.
    """
    habit_scores = []
    screen_analytics = {}
    journal_entries = []
    insights = []

    async with httpx.AsyncClient(timeout=3.0) as client:
        # 1. Pull habit scores from Habit Engine
        try:
            r = await client.get(f"{SERVICES['habit']}/api/v1/habit/score")
            if r.status_code == 200:
                habit_scores = r.json()
        except httpx.RequestError:
            pass

        # 2. Pull screen time analytics from Doomscroll
        try:
            r = await client.get(f"{SERVICES['doomscroll']}/api/v1/usage/analytics")
            if r.status_code == 200:
                screen_analytics = r.json()
        except httpx.RequestError:
            pass

        # 3. Pull journal entries for burnout signals
        try:
            r = await client.get(f"{SERVICES['journal']}/api/v1/journal/timeline")
            if r.status_code == 200:
                data = r.json()
                journal_entries = data.get("entries", [])
        except httpx.RequestError:
            pass

    # ── Correlation Algorithm ──
    avg_screen = screen_analytics.get("average_risk", 0)
    doomscroll_sessions = screen_analytics.get("doomscroll_sessions", 0)
    total_sessions = screen_analytics.get("total_sessions", 1)
    doomscroll_ratio = doomscroll_sessions / max(total_sessions, 1)

    for habit in habit_scores:
        name = habit.get("habit_name", "").replace("_", " ").title()
        streak = habit.get("streak_days", 0)
        score = habit.get("decayed_score", 0)

        # Insight: High screen time + failing habit → strong correlation warning
        if score < 40 and doomscroll_ratio > 0.4:
            insights.append(
                {
                    "type": "screen_habit_conflict",
                    "severity": "high",
                    "insight": (
                        f"📵 You tend to fail '{name}' on days with high screen time. "
                        f"Your doomscroll ratio is {doomscroll_ratio:.0%} — try blocking distracting apps "
                        f"30 minutes before your habit time."
                    ),
                    "confidence": round(min(0.95, 0.5 + doomscroll_ratio), 2),
                    "habit": name,
                }
            )
        # Insight: Strong habit streak + low screen risk → reinforce the pattern
        elif streak >= 5 and avg_screen < 0.3:
            insights.append(
                {
                    "type": "positive_reinforcement",
                    "severity": "low",
                    "insight": (
                        f"🔥 Your {streak}-day streak on '{name}' correlates with lower screen risk scores "
                        f"({avg_screen:.0%}). Your habits are shielding you from doomscrolling. Keep it up!"
                    ),
                    "confidence": round(min(0.95, 0.6 + streak * 0.04), 2),
                    "habit": name,
                }
            )
        # Insight: Moderate habit + elevated screen risk → early warning
        elif 40 <= score < 70 and avg_screen > 0.5:
            insights.append(
                {
                    "type": "early_warning",
                    "severity": "medium",
                    "insight": (
                        f"⚠️ '{name}' is weakening (score: {score:.0f}). "
                        f"Your screen time risk is elevated ({avg_screen:.0%}). "
                        f"These two patterns together predict a full habit reset within 3 days."
                    ),
                    "confidence": 0.75,
                    "habit": name,
                }
            )

    # Burnout signal from journal frequency
    if len(journal_entries) == 0:
        insights.append(
            {
                "type": "burnout_signal",
                "severity": "medium",
                "insight": (
                    "📔 You haven't journaled recently. Silence in your memory journal, "
                    "combined with active screen time, is an early burnout signal. "
                    "Write one sentence about today."
                ),
                "confidence": 0.65,
                "habit": "journaling",
            }
        )

    return {
        "status": "ok",
        "insights": insights,
        "data_sources": {
            "habits_analyzed": len(habit_scores),
            "screen_sessions": total_sessions,
            "journal_entries": len(journal_entries),
            "doomscroll_ratio": round(doomscroll_ratio, 2),
        },
        "generated_at": datetime.datetime.utcnow().isoformat(),
    }


# Serve static frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_ui():
        return FileResponse(os.path.join(static_dir, "index.html"))
