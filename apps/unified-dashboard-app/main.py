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

# Services map
SERVICES = {
    "journal": "http://localhost:8001",
    "doomscroll": "http://localhost:8002",
    "vision": "http://localhost:8003",
    "habit": "http://localhost:8004",
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
            client_queue.put_nowait(payload.dict())
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


# Serve static frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_ui():
        return FileResponse(os.path.join(static_dir, "index.html"))
