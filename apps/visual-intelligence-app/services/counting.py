from models.vision import TrackedObject, CountReport
from typing import List
from datetime import datetime


class MockCountingModule:
    def generate_report(self, tracked_objects: List[TrackedObject]) -> CountReport:
        counts = {}
        for t in tracked_objects:
            counts[t.label] = counts.get(t.label, 0) + 1

        return CountReport(counts=counts, timestamp=datetime.utcnow())


counting_module = MockCountingModule()
