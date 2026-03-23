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
        "/api/v1/usage/focus",
        json={"duration_minutes": 30, "app_to_block": "video_app"},
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
    assert "message" in data


def test_usage_analytics():
    client.post("/api/v1/usage/track", json={"app_name": "instagram", "minutes": 10})
    client.post("/api/v1/usage/predict", json={"app_name": "tiktok", "minutes": 1})
    response = client.get("/api/v1/usage/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "doomscroll_sessions" in data
    assert "average_risk" in data


def test_system_monitor():
    response = client.get("/api/v1/usage/monitor")
    assert response.status_code == 200
    data = response.json()
    assert "active_apps" in data


def test_analyzer_total_minutes():
    from services.analyzer import analyzer

    analyzer.sessions.clear()

    class DummyReq:
        def __init__(self, app_name, minutes):
            self.app_name = app_name
            self.minutes = minutes

    analyzer.process_session(DummyReq("x", 5))
    analyzer.process_session(DummyReq("y", 10))
    assert analyzer.get_total_minutes() == 15
    assert analyzer.get_total_minutes("x") == 5


def test_predictive_ai_analytics_exception():
    from services.predictive_ai import predictor
    from unittest.mock import patch

    with patch("services.predictive_ai._get_db", side_effect=Exception("DB Error")):
        data = predictor.get_usage_analytics()
        assert data["total_sessions"] == 0


def test_system_monitor_exception():
    from unittest.mock import patch

    with patch("subprocess.run", side_effect=Exception("Timeout")):
        response = client.get("/api/v1/usage/monitor")
        assert response.status_code == 200
        assert response.json()["error"] == "System monitor unavailable"
