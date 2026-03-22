from models.vision import CountReport, VisionEvent
from core.config import settings
from typing import List
from datetime import datetime
from uuid import uuid4


class MockEventEngine:
    def __init__(self):
        self.events: List[VisionEvent] = []

    def process_counts(self, report: CountReport) -> List[VisionEvent]:
        new_events = []
        total_objects = sum(report.counts.values())
        if total_objects >= settings.event_threshold:
            event = VisionEvent(
                event_id=str(uuid4()),
                event_type="high_density_detected",
                timestamp=datetime.utcnow(),
                description=f"High object density detected: {total_objects} total objects",
            )
            self.events.append(event)
            new_events.append(event)
        return new_events

    def get_events(self) -> List[VisionEvent]:
        return self.events


event_engine = MockEventEngine()
