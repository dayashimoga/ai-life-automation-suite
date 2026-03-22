from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from routes.usage import router as usage_router
from core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(usage_router, prefix=settings.api_prefix + "/usage")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


# Mount frontend UI
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
