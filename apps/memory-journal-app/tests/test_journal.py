import pytest
from fastapi.testclient import TestClient
from main import app
from routes.journal import db_entries

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    db_entries.clear()
    yield


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_image():
    files = {"file": ("test_image.jpg", b"fake image content", "image/jpeg")}
    response = client.post("/api/v1/journal/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_image.jpg"
    assert "test_image.jpg" in data["caption"]
    assert "memory" in data["tags"]
    assert "San Francisco" in data["mock_location"]
    assert len(db_entries) == 1


def test_get_timeline():
    # Setup
    files1 = {"file": ("img1.jpg", b"content", "image/jpeg")}
    client.post("/api/v1/journal/upload", files=files1)

    files2 = {"file": ("img2.jpg", b"content", "image/jpeg")}
    client.post("/api/v1/journal/upload", files=files2)

    response = client.get("/api/v1/journal/timeline")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["entries"]) == 2


def test_search_journal():
    files1 = {"file": ("vacation.jpg", b"content", "image/jpeg")}
    client.post("/api/v1/journal/upload", files=files1)

    response = client.get("/api/v1/journal/search?query=vacation")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["entries"][0]["filename"] == "vacation.jpg"

    response_empty = client.get("/api/v1/journal/search?query=notfound")
    assert response_empty.status_code == 200
    assert response_empty.json()["total"] == 0

def test_process_video():
    import cv2
    import numpy as np
    
    original_cap = cv2.VideoCapture
    class MockCap:
        def __init__(self, *args, **kwargs): pass
        def get(self, prop): return 10
        def set(self, prop, val): pass
        def read(self): return True, np.zeros((10,10,3), dtype=np.uint8)
        def release(self): pass
        
    cv2.VideoCapture = MockCap
    try:
        files = {"file": ("test.mp4", b"fake video memory bytes representing mp4 structure", "video/mp4")}
        response = client.post("/api/v1/journal/process_video", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "video_memory" in data["tags"]
        assert "Transcript" in data["caption"]
    finally:
        cv2.VideoCapture = original_cap
