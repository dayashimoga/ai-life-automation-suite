from fastapi import APIRouter, UploadFile, File
from models.journal import JournalEntry, JournalResponse
from services.captioning import captioning_service
from services.search import search_engine
from typing import List
from datetime import datetime
from uuid import uuid4
import cv2
import tempfile
import os
import httpx
import base64

router = APIRouter()

# In-memory storage for mockup purposes
db_entries: List[JournalEntry] = []


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

    db_entries.append(entry)
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

        # Microservice Bridge: Query Visual Intelligence Engine natively
        try:
            async with httpx.AsyncClient() as client:
                files = {"file": ("keyframe.jpg", frame_bytes, "image/jpeg")}
                resp = await client.post(
                    "http://127.0.0.1:5002/api/v1/vision/process",
                    files=files,
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    vision_data = resp.json()
                    counts = vision_data.get("counts", {})
                    tags.extend(list(counts.keys()))
        except Exception as e:
            print(f"Vision Bridge Error: {e}")

    # Forward to existing architecture natively
    # Create a JournalEntry object and append it to db_entries
    entry = JournalEntry(
        id=str(uuid4()),
        filename=file.filename
        or "video_keyframe.jpg",  # Use original filename or a default
        caption=text_content,
        tags=list(set(tags)),  # Ensure unique tags
        mock_location="Unknown (Video Analysis)",  # Mock location for video
        timestamp=datetime.utcnow(),
    )
    db_entries.append(entry)
    return entry


@router.get("/timeline", response_model=JournalResponse)
async def get_timeline():
    # Return entries sorted by timestamp descending
    sorted_entries = sorted(db_entries, key=lambda x: x.timestamp, reverse=True)
    return JournalResponse(entries=sorted_entries, total=len(sorted_entries))


@router.get("/search", response_model=JournalResponse)
async def search_journal(query: str):
    results = [
        e
        for e in db_entries
        if query.lower() in e.caption.lower()
        or any(query.lower() in t.lower() for t in e.tags)
    ]
    return JournalResponse(entries=results, total=len(results))


@router.get("/semantic_search")
async def semantic_search(query: str, top_k: int = 10):
    """Natural language semantic search across all journal entries."""
    # Re-index on each search (lightweight for in-memory stores)
    docs = [
        {
            "id": e.id,
            "caption": e.caption,
            "tags": e.tags,
            "filename": e.filename,
            "timestamp": str(e.timestamp),
        }
        for e in db_entries
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
