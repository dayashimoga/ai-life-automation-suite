from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Detection(BaseModel):
    id: str
    track_id: Optional[int] = None
    label: str  # e.g. person, vehicle, etc.
    confidence: float
    bbox: BoundingBox


class TrackedObject(BaseModel):
    track_id: int
    label: str
    path: List[BoundingBox]


class VisionEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    description: str


class CountReport(BaseModel):
    counts: Dict[str, int]
    timestamp: datetime
    annotated_image_base64: Optional[str] = None
