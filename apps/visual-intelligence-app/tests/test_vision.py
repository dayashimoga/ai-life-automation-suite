import pytest
import numpy as np
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from services.event_engine import event_engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_state():
    event_engine.events.clear()
    yield


def _mock_detect(self, image_data: bytes):
    from models.vision import Detection, BoundingBox

    return [
        Detection(
            id="1",
            track_id=1,
            label="person",
            confidence=0.9,
            bbox=BoundingBox(x=0, y=0, width=10, height=10),
        ),
        Detection(
            id="2",
            track_id=2,
            label="vehicle",
            confidence=0.8,
            bbox=BoundingBox(x=0, y=0, width=10, height=10),
        ),
    ], np.zeros((100, 100, 3), dtype=np.uint8)


def _mock_spatial(self, frame_np, detections):
    return frame_np  # pass-through


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("services.spatial_analytics.SpatialAnalyticsEngine.process_frame", _mock_spatial)
@patch("services.detection.RealDetectionModule.detect_and_draw", _mock_detect)
def test_process_frame_generates_report():
    files = {"file": ("frame.jpg", b"fakeImageData", "image/jpeg")}
    response = client.post("/api/v1/vision/process", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "counts" in data
    assert "person" in data["counts"]
    assert "vehicle" in data["counts"]
    assert data["counts"]["person"] == 1
    assert data["counts"]["vehicle"] == 1


@patch("services.spatial_analytics.SpatialAnalyticsEngine.process_frame", _mock_spatial)
@patch("services.detection.RealDetectionModule.detect_and_draw", _mock_detect)
def test_event_engine_generates_queue_event():
    import services.counting

    def mock_generate_report(self, tracked_objects):
        from models.vision import CountReport
        from datetime import datetime

        return CountReport(counts={"person": 10}, timestamp=datetime.utcnow())

    original_report = services.counting.MockCountingModule.generate_report
    services.counting.MockCountingModule.generate_report = mock_generate_report

    try:
        files = {"file": ("frame2.jpg", b"video stream", "image/jpeg")}
        client.post("/api/v1/vision/process", files=files)

        response = client.get("/api/v1/vision/events")
        assert response.status_code == 200
        events = response.json()
        assert len(events) == 1
        assert events[0]["event_type"] == "high_density_detected"
        assert "10 total objects" in events[0]["description"]
    finally:
        services.counting.MockCountingModule.generate_report = original_report


def test_websocket_connect():
    with client.websocket_connect("/api/v1/vision/ws") as websocket:
        # Connection accepted successfully if we reach here
        assert websocket is not None


def test_history_endpoint():
    from core.database import save_analysis

    save_analysis("test_video.mp4", [{"horse": 1, "cat": 2}])
    response = client.get("/api/v1/vision/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_spatial_analytics_line_crossing():
    """Unit test: objects crossing the center line should increment entry/exit counts."""
    from services.spatial_analytics import SpatialAnalyticsEngine
    from models.vision import Detection, BoundingBox

    engine = SpatialAnalyticsEngine()
    frame = np.zeros((200, 200, 3), dtype=np.uint8)

    # Object above center (y=50), then crosses below center (y=110)
    det_above = Detection(
        id="a",
        track_id=10,
        label="person",
        confidence=0.9,
        bbox=BoundingBox(x=50, y=40, width=20, height=20),
    )
    engine.process_frame(frame.copy(), [det_above])

    det_below = Detection(
        id="b",
        track_id=10,
        label="person",
        confidence=0.9,
        bbox=BoundingBox(x=50, y=100, width=20, height=20),
    )
    engine.process_frame(frame.copy(), [det_below])

    assert engine.entry_count == 1
    assert engine.exit_count == 0


def test_spatial_analytics_heatmap():
    """Unit test: heatmap accumulates centroids."""
    from services.spatial_analytics import SpatialAnalyticsEngine
    from models.vision import Detection, BoundingBox

    engine = SpatialAnalyticsEngine()
    frame = np.zeros((200, 200, 3), dtype=np.uint8)

    det = Detection(
        id="c",
        track_id=20,
        label="car",
        confidence=0.95,
        bbox=BoundingBox(x=80, y=80, width=40, height=40),
    )
    result = engine.process_frame(frame.copy(), [det])

    assert result is not None
    assert engine.heatmap_layer is not None
def test_security_dashboard():
    res = client.get("/api/v1/vision/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_analyses" in data
    assert "active_zones" in data
    assert "alert_timeline" in data


def test_zone_configuration():
    # POST
    payload = {
        "name": "Front Door",
        "type": "restricted_area",
        "coordinates": [{"x": 10, "y": 20}]
    }
    res_post = client.post("/api/v1/vision/zones", json=payload)
    assert res_post.status_code == 200
    assert res_post.json()["name"] == "Front Door"

    # GET
    res_get = client.get("/api/v1/vision/zones")
    assert res_get.status_code == 200
    assert len(res_get.json()) >= 1


def test_identity_service():
    import numpy as np
    from services.identity import init_identity_db, analyze_identities
    import services.identity as ident_module
    from unittest.mock import patch, MagicMock

    with patch("os.path.exists", return_value=False):
        with patch("os.makedirs"):
            with patch("builtins.open"):
                init_identity_db()

    ident_module.DEEPFACE_AVAILABLE = True
    
    # Create mock DeepFace class on the module if it doesn't exist
    if not hasattr(ident_module, "DeepFace"):
        ident_module.DeepFace = MagicMock()

    frame = np.zeros((10, 10, 3), dtype=np.uint8)

    with patch.object(ident_module.DeepFace, "find", return_value=[MagicMock(empty=True)]):
        identities = analyze_identities(frame)
        assert identities == ["Unknown Person"]

    with patch.object(ident_module.DeepFace, "find", return_value=[MagicMock(empty=False)]):
        identities = analyze_identities(frame)
        assert identities == ["Authorized User"]

    with patch.object(ident_module.DeepFace, "find", side_effect=ValueError):
        assert analyze_identities(frame) == []


def test_detection_service_with_mock():
    import numpy as np
    import cv2
    from services.detection import detection_module
    
    class MockBoxEntry:
        def __init__(self):
            self.cls = np.array([0])
            self.conf = np.array([0.9])
            self.xyxy = np.array([[10, 10, 20, 20]])
            self.id = np.array([1])

    class MockYoloResult:
        def __init__(self):
            self.boxes = [MockBoxEntry()]

    class MockYolo:
        def __init__(self):
            self.names = {0: "person"}
        def track(self, *args, **kwargs):
            return [MockYoloResult()]

    original_model = detection_module.model
    detection_module.model = MockYolo()
    try:
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", img)

        detections, out_img = detection_module.detect_and_draw(buffer.tobytes())
        assert len(detections) == 1
        assert detections[0].label == "person"
    finally:
        detection_module.model = original_model


def test_process_video():
    import numpy as np
    import cv2
    from unittest.mock import patch

    # Mock analyze identities to return Unknown Person
    with patch("routes.vision.analyze_identities", return_value=["Unknown Person"]):
        # Pass a mock cv2 VideoCapture
        original_cap = cv2.VideoCapture
        class MockCap:
            def __init__(self, *args, **kwargs):
                self.frames_read = 0
            def isOpened(self):
                return True
            def get(self, prop):
                return 20
            def set(self, prop, val):
                pass
            def read(self):
                self.frames_read += 1
                if self.frames_read > 15:
                    return False, None
                return True, np.zeros((10, 10, 3), dtype=np.uint8)
            def release(self):
                pass
        
        cv2.VideoCapture = MockCap
        try:
            files = {
                "file": ("test.mp4", b"fake mp4", "video/mp4")
            }
            res = client.post("/api/v1/vision/process", files=files)
            assert res.status_code == 200
        finally:
            cv2.VideoCapture = original_cap


def test_process_image_unknown_person():
    import numpy as np
    import cv2
    from unittest.mock import patch
    
    with patch("routes.vision.analyze_identities", return_value=["Unknown Person"]):
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", img)
        
        files = {
            "file": ("test.jpg", buffer.tobytes(), "image/jpeg")
        }
        res = client.post("/api/v1/vision/process", files=files)
        assert res.status_code == 200
