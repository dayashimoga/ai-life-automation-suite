import pytest
from fastapi.testclient import TestClient
from main import app
from core.database import init_db

# Ensure DB is initialized
init_db()

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    import sqlite3

    conn = sqlite3.connect("journal.db", check_same_thread=False)
    try:
        conn.execute("DELETE FROM journal_entries")
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()
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
    assert "test image" in data["caption"]
    assert "photo" in data["tags"]
    assert "Location pending" in data["mock_location"]

    # Verify via DB/timeline
    timeline_resp = client.get("/api/v1/journal/timeline")
    assert timeline_resp.json()["total"] >= 1


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
        def __init__(self, *args, **kwargs):
            pass

        def get(self, prop):
            return 10

        def set(self, prop, val):
            pass

        def read(self):
            return True, np.zeros((10, 10, 3), dtype=np.uint8)

        def release(self):
            pass

    cv2.VideoCapture = MockCap
    try:
        files = {
            "file": (
                "test.mp4",
                b"fake video memory bytes representing mp4 structure",
                "video/mp4",
            )
        }
        response = client.post("/api/v1/journal/process_video", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "video_memory" in data["tags"]
        assert "Transcript" in data["caption"]
    finally:
        cv2.VideoCapture = original_cap


def test_caption_gps_parsing(tmp_path):
    from services.captioning import captioning_service

    f1 = tmp_path / "empty.jpg"
    f1.write_bytes(b"")
    assert captioning_service._parse_exif_gps(str(f1)) is None

    f2 = tmp_path / "dummy.jpg"
    f2.write_bytes(b"\xff\xd8\xff\xe1\x00\x00Exif\x00\x00")
    assert captioning_service._parse_exif_gps(str(f2)) is None

    f3 = tmp_path / "gps.jpg"
    f3.write_bytes(b"\xff\xd8\xff\xe1\x00\x00Exif\x00\x00GPS")
    assert captioning_service._parse_exif_gps(str(f3)) is None

    assert captioning_service._parse_exif_gps("/non/existent/file.jpg") is None


def test_caption_reverse_geocode():
    from services.captioning import captioning_service

    assert captioning_service._reverse_geocode(35.0, -90.0) == "United States"
    assert captioning_service._reverse_geocode(45.0, 10.0) == "Europe"
    assert captioning_service._reverse_geocode(20.0, 80.0) == "India"
    assert captioning_service._reverse_geocode(-20.0, 140.0) == "Australia"
    assert "Coordinates" in captioning_service._reverse_geocode(0.0, 0.0)


def test_caption_date_extraction():
    from services.captioning import captioning_service

    assert (
        captioning_service._extract_date_from_name("IMG_15-03-2024.jpg") == "2024-03-15"
    )
    assert captioning_service._extract_date_from_name("NoDate.jpg") is None


def test_semantic_search_engine():
    from services.search import search_engine

    docs = [
        {"caption": "A beautiful sunset at the beach", "tags": ["nature", "ocean"]},
        {"caption": "City skyline at night", "tags": ["urban"]},
        {"caption": "Family dinner", "tags": ["food", "celebration"]},
    ]
    search_engine.index_documents(docs)

    res = search_engine.search("sunset beach", top_k=1)
    assert len(res) == 1
    assert "sunset" in res[0][0]["caption"]

    res2 = search_engine.search("city", top_k=1)
    assert len(res2) == 1
    assert "skyline" in res2[0][0]["caption"]

    assert search_engine.search("nothinghere") == []

    search_engine.index_documents([])
    assert search_engine.search("a") == []


def test_video_processing_failure():
    res = client.post(
        "/api/v1/journal/process_video",
        files={"file": ("fake.mp4", b"not a video structure", "video/mp4")},
    )
    assert res.status_code == 200
    assert "video_memory" in res.json()["tags"]


def test_semantic_search_endpoint():
    client.post(
        "/api/v1/journal/entry",
        json={"caption": "Test hello", "tags": ["hello"]},
    )
    res = client.get("/api/v1/journal/semantic_search?query=hello")
    assert res.status_code == 200
    assert "results" in res.json()
