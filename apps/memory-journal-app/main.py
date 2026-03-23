from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from routes.journal import router as journal_router
from core.config import settings
from core.database import init_db

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(journal_router, prefix=settings.api_prefix + "/journal")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


# Mount frontend UI
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
