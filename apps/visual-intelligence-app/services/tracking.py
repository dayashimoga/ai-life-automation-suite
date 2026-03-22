from models.vision import Detection, TrackedObject
from typing import List


class MockTrackingModule:
    def __init__(self):
        self._counter = 1

    def track(self, detections: List[Detection]) -> List[TrackedObject]:
        tracked = []
        for det in detections:
            tracked.append(
                TrackedObject(track_id=self._counter, label=det.label, path=[det.bbox])
            )
            self._counter += 1
        return tracked


tracking_module = MockTrackingModule()
