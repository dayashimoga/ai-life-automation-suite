import pytest
from fastapi.testclient import TestClient
from main import app
from routes.usage import active_sessions
from services.tracker import tracker

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    tracker.usage_records.clear()
    tracker.alerts.clear()
    active_sessions.clear()
    yield


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_track_usage():
    response = client.post(
        "/api/v1/usage/track", json={"app_name": "social_media_x", "minutes": 20}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "social_media_x"
    assert data["minutes_used"] == 20


def test_alerts_generated_on_threshold():
    # settings threshold is 60 minutes
    client.post("/api/v1/usage/track", json={"app_name": "social_app", "minutes": 40})
    response = client.get("/api/v1/usage/alerts")
    assert response.json() == []

    # exceed threshold
    client.post("/api/v1/usage/track", json={"app_name": "social_app", "minutes": 25})
    response = client.get("/api/v1/usage/alerts")
    alerts = response.json()
    assert len(alerts) == 1
    assert "social_app" in alerts[0]["message"]


def test_focus_sessions():
    response = client.post(
        "/api/v1/usage/focus", json={"duration_minutes": 30, "app_to_block": "video_app"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"]
    assert data["app_blocked"] == "video_app"

    get_resp = client.get("/api/v1/usage/focus")
    assert get_resp.status_code == 200
    sessions = get_resp.json()
    assert len(sessions) == 1
    assert sessions[0]["app_blocked"] == "video_app"

def test_predict_risk():
    response = client.post(
        "/api/v1/usage/predict", json={"app_name": "tiktok", "minutes": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction_score" in data
    assert "will_doomscroll" in data
    assert "intervention_recommended" in data
    assert "message" in data
