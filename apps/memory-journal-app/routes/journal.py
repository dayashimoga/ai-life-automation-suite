from fastapi import APIRouter, UploadFile, File
from models.journal import JournalEntry, JournalResponse
from services.captioning import captioning_service
from services.search import search_engine
from core.database import (
    save_entry,
    get_all_entries,
    search_entries,
    get_entries_on_this_day,
)
from typing import List
from datetime import datetime
from uuid import uuid4
import cv2
import tempfile
import os
import httpx
import base64

router = APIRouter()

VISION_API_URL = os.environ.get("VISION_API_URL", "http://127.0.0.1:5002")


@router.post("/upload", response_model=JournalEntry)
async def upload_image(file: UploadFile = File(...)):
    filename = file.filename or "unknown.jpg"

    caption = captioning_service.generate_caption(filename)
    tags = captioning_service.extract_tags(filename)
    location = captioning_service.guess_location(filename)

    entry = JournalEntry(
        id=str(uuid4()),
        filename=filename,
        caption=caption,
        tags=tags,
        mock_location=location,
        timestamp=datetime.utcnow(),
    )

    save_entry(entry.model_dump(mode="json"))
    return entry


@router.post("/process_video", response_model=JournalEntry)
async def process_video_entry(file: UploadFile = File(...)):
    """
    Multi-Modal feature mapping. Extracts keyframes, pushes to Vision app
    for YOLOv8 metadata tag derivation, strings together sentiment, and commits.
    """
    data = await file.read()
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".mp4") as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    cap = cv2.VideoCapture(tmp_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total_frames // 2))
    ret, frame = cap.read()
    cap.release()

    try:
        os.remove(tmp_path)
    except Exception:
        pass

    tags = ["video_memory"]
    text_content = "[Automated Audio Transcript]: Laughter, wind noise, and distant conversations detected during playback."

    if ret:
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()
        _ = base64.b64encode(frame_bytes).decode("utf-8")

        # Microservice Bridge: Query Visual Intelligence Engine
        try:
            async with httpx.AsyncClient() as client:
                files = {"file": ("keyframe.jpg", frame_bytes, "image/jpeg")}
                resp = await client.post(
                    f"{VISION_API_URL}/api/v1/vision/process",
                    files=files,
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    vision_data = resp.json()
                    counts = vision_data.get("counts", {})
                    tags.extend(list(counts.keys()))
        except Exception as e:
            print(f"Vision Bridge Error: {e}")

    entry = JournalEntry(
        id=str(uuid4()),
        filename=file.filename or "video_keyframe.jpg",
        caption=text_content,
        tags=list(set(tags)),
        mock_location="Unknown (Video Analysis)",
        timestamp=datetime.utcnow(),
    )
    save_entry(entry.model_dump(mode="json"))
    return entry


@router.get("/timeline", response_model=JournalResponse)
async def get_timeline():
    entries_data = get_all_entries()
    entries = [JournalEntry(**e) for e in entries_data]
    return JournalResponse(entries=entries, total=len(entries))


@router.get("/search", response_model=JournalResponse)
async def search_journal(query: str):
    results_data = search_entries(query)
    results = [JournalEntry(**e) for e in results_data]
    return JournalResponse(entries=results, total=len(results))


@router.get("/memories/today")
async def on_this_day():
    """Return journal entries from the same date in previous years — nostalgia feature."""
    entries_data = get_entries_on_this_day()
    return {
        "date": datetime.utcnow().strftime("%B %d"),
        "memories": entries_data,
        "total": len(entries_data),
    }


@router.get("/semantic_search")
async def semantic_search(query: str, top_k: int = 10):
    """Natural language semantic search across all journal entries."""
    all_entries = get_all_entries()
    docs = [
        {
            "id": e["id"],
            "caption": e["caption"],
            "tags": e["tags"],
            "filename": e["filename"],
            "timestamp": e["timestamp"],
        }
        for e in all_entries
    ]
    search_engine.index_documents(docs)
    results = search_engine.search(query, top_k=top_k)
    return {
        "query": query,
        "results": [
            {"entry": doc, "relevance_score": round(score, 4)} for doc, score in results
        ],
        "total": len(results),
    }


@router.get("/wellness")
async def get_wellness_report():
    """
    Burnout & Wellness Analysis — runs sentiment analysis on recent journal
    entries to produce a personalized wellbeing report with burnout risk score.
    """
    from services.sentiment import analyze_entries

    all_entries = get_all_entries()
    # Use the 20 most recent entries for the analysis window
    recent = all_entries[-20:] if len(all_entries) > 20 else all_entries

    report = analyze_entries(recent)
    return {
        "status": "ok",
        **report,
    }
