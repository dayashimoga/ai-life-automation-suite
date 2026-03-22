from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.database import init_db
from routes.habit import router
import os

app = FastAPI(title="Micro-Habit Engine", version="1.0.0")
init_db()

app.include_router(router, prefix="/habit")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "micro-habit-engine"}


# Serve static frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_ui():
        return FileResponse(os.path.join(static_dir, "index.html"))
