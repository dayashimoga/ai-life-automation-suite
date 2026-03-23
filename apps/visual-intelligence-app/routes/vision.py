from fastapi import APIRouter, File, UploadFile, WebSocket, WebSocketDisconnect
from typing import List
import cv2
import tempfile
import os
from datetime import datetime
from models.vision import CountReport, VisionEvent
from services.detection import detection_module
from services.tracking import tracking_module
from services.counting import counting_module
from services.event_engine import event_engine
from core.database import init_db, save_analysis, get_history
from services.identity import init_identity_db, analyze_identities
from services.spatial_analytics import spatial_analytics_global
from services.webhooks import send_webhook_alert
import base64
import uuid

init_db()
init_identity_db()

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active_connections:
            self.active_connections.remove(ws)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/process", response_model=CountReport)
async def process_frame(file: UploadFile = File(...)):
    data = await file.read()

    filename = getattr(file, "filename", "") or ""
    if filename.endswith(".mp4") or getattr(file, "content_type", "") == "video/mp4":
        # Video Processing Pipeline
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        cap = cv2.VideoCapture(tmp_path)
        frame_count = 0
        max_counts = {}
        last_report = None
        event_dicts = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            # Parse every 10th frame to simulate real-time processing and save compute
            if frame_count % 10 != 0:
                continue

            _, buffer = cv2.imencode(".jpg", frame)

            detections, raw_img = detection_module.detect_and_draw(buffer.tobytes())
            annotated_img = spatial_analytics_global.process_frame(raw_img, detections)

            _, buffer2 = cv2.imencode(".jpg", annotated_img)
            annotated_b64 = base64.b64encode(buffer2).decode("utf-8")

            tracked = tracking_module.track(detections)
            report = counting_module.generate_report(tracked)
            report.annotated_image_base64 = annotated_b64

            for k, v in report.counts.items():
                max_counts[k] = max(max_counts.get(k, 0), v)

            new_events = event_engine.process_counts(report)

            # IDENTITY SECURITY HOOK
            identities = analyze_identities(frame)
            if "Unknown Person" in identities:
                new_events.append(
                    VisionEvent(
                        event_id=str(uuid.uuid4()),
                        event_type="unauthorized_presence_detected",
                        timestamp=datetime.utcnow(),
                        description="DeepFace intercepted an unrecognized face biometric in the frame.",
                    )
                )

            for ev in new_events:
                ev_dict = ev.model_dump(mode="json")
                event_dicts.append(ev_dict)
                await manager.broadcast(ev_dict)

            last_report = report

        cap.release()
        try:
            os.remove(tmp_path)
        except Exception:
            pass

        if last_report:
            last_report.counts = max_counts
            if max_counts:
                save_analysis(max_counts, event_dicts)
            return last_report
        else:
            return CountReport(counts={}, timestamp=datetime.utcnow())

    # Standard Image Pipeline
    detections, raw_img = detection_module.detect_and_draw(data)
    if raw_img is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid image data")

    annotated_img = spatial_analytics_global.process_frame(raw_img, detections)
    
    if annotated_img is None:
        annotated_img = raw_img

    _, buffer2 = cv2.imencode(".jpg", annotated_img)
    annotated_b64 = base64.b64encode(buffer2).decode("utf-8")

    tracked = tracking_module.track(detections)
    report = counting_module.generate_report(tracked)
    report.annotated_image_base64 = annotated_b64

    # Process events based on counts
    new_events = event_engine.process_counts(report)
    event_dicts = []

    # IDENTITY SECURITY HOOK (Single Frame)
    import numpy as np

    np_arr = np.frombuffer(data, np.uint8)
    img_cv2 = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img_cv2 is not None:
        identities = analyze_identities(img_cv2)
        if "Unknown Person" in identities:
            new_events.append(
                VisionEvent(
                    event_id=str(uuid.uuid4()),
                    event_type="unauthorized_presence_detected",
                    timestamp=datetime.utcnow(),
                    description="DeepFace intercepted an unrecognized face biometric in the frame.",
                )
            )

    for ev in new_events:
        ev_dict = ev.model_dump(mode="json")
        event_dicts.append(ev_dict)
        await manager.broadcast(ev_dict)

    # Persist historical data asynchronously or synchronously
    if report.counts:
        save_analysis(report.counts, event_dicts)

    return report


@router.get("/events", response_model=List[VisionEvent])
async def get_events():
    return event_engine.get_events()


@router.get("/history")
async def fetch_historical_analysis():
    return get_history()


# ─── Phase 6.5: Security Dashboard ─────────────────────

# In-memory zone configuration store
monitoring_zones = []


@router.get("/dashboard")
async def security_dashboard():
    """Aggregated security dashboard with alert timeline and zone status."""
    history = get_history()
    events = event_engine.get_events()

    # Build alert timeline from events
    alert_timeline = []
    for ev in events[-50:]:  # Last 50 events
        alert_timeline.append(
            {
                "event_id": ev.event_id,
                "type": ev.event_type,
                "timestamp": (
                    ev.timestamp.isoformat()
                    if hasattr(ev.timestamp, "isoformat")
                    else str(ev.timestamp)
                ),
                "description": ev.description,
                "severity": "high" if "unauthorized" in ev.event_type else "medium",
            }
        )

    return {
        "total_analyses": len(history) if isinstance(history, list) else 0,
        "active_zones": len(monitoring_zones),
        "alert_timeline": alert_timeline,
        "zones": monitoring_zones,
        "live_connections": len(manager.active_connections),
    }


@router.post("/zones")
async def configure_zone(zone: dict):
    """Configure a monitoring zone (line crossing, restricted area, etc.)."""
    zone_config = {
        "id": str(uuid.uuid4()),
        "name": zone.get("name", "Unnamed Zone"),
        "type": zone.get(
            "type", "restricted_area"
        ),  # restricted_area, line_crossing, counting_zone
        "coordinates": zone.get("coordinates", []),
        "created_at": datetime.utcnow().isoformat(),
        "active": True,
    }
    monitoring_zones.append(zone_config)
    return zone_config


@router.get("/zones")
async def get_zones():
    return monitoring_zones


@router.post("/webhook/configure")
async def configure_webhook(config: dict):
    """Configure a webhook URL for alert notifications."""
    import services.webhooks as wh

    url = config.get("url", "")
    if url:
        wh.WEBHOOK_URL = url
        return {"status": "configured", "webhook_url": url}
    return {"status": "error", "message": "No URL provided"}


@router.post("/webhook/test")
async def test_webhook():
    """Send a test webhook notification."""
    result = await send_webhook_alert(
        event_type="test_alert",
        description="This is a test notification from Visual Intelligence.",
        event_id="test-" + str(uuid.uuid4())[:8],
    )
    return result
