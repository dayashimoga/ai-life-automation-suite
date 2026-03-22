import pytest
import sys
import os

from datetime import datetime, timedelta

# Add app root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app
from core.database import init_db, DB_PATH

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    """Wipe the DB before each test for isolation."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


# ---------- Health ----------
def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ---------- Log Habit ----------
def test_log_habit():
    r = client.post("/habit/log", json={"habit_name": "drink_water"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "logged"
    assert data["habit"] == "drink_water"


def test_log_habit_with_timestamp():
    ts = "2026-03-22T10:00:00"
    r = client.post("/habit/log", json={"habit_name": "stretch", "timestamp": ts})
    assert r.status_code == 200
    assert r.json()["habit"] == "stretch"


def test_log_multiple_habits():
    for name in ["walk", "walk", "drink_water"]:
        r = client.post("/habit/log", json={"habit_name": name})
        assert r.status_code == 200


# ---------- Scores ----------
def test_score_empty():
    r = client.get("/habit/score")
    assert r.status_code == 200
    assert r.json() == []


def test_score_after_logging():
    client.post("/habit/log", json={"habit_name": "walk"})
    client.post("/habit/log", json={"habit_name": "walk"})
    r = client.get("/habit/score")
    assert r.status_code == 200
    scores = r.json()
    assert len(scores) == 1
    assert scores[0]["habit_name"] == "walk"
    assert scores[0]["raw_score"] == 20  # 2 logs * 10


def test_score_decays():
    """Score should be lower when last log was hours ago."""
    from core.database import log_habit

    old_ts = (datetime.utcnow() - timedelta(hours=10)).isoformat()
    log_habit("stretch", old_ts)

    r = client.get("/habit/score")
    scores = r.json()
    s = scores[0]
    assert s["raw_score"] == 10
    assert s["decayed_score"] < s["raw_score"]


# ---------- Insights ----------
def test_insights_empty():
    r = client.get("/habit/insights")
    assert r.status_code == 200
    assert r.json() == []


def test_insights_after_logging():
    client.post("/habit/log", json={"habit_name": "drink_water"})
    r = client.get("/habit/insights")
    insights = r.json()
    assert len(insights) == 1
    assert insights[0]["habit_name"] == "drink_water"
    assert insights[0]["status"] in ("strong", "moderate", "decaying", "critical")
    assert insights[0]["total_logs"] == 1


def test_insights_nudge_for_decayed():
    """Old logs should produce a nudge."""
    from core.database import log_habit

    old_ts = (datetime.utcnow() - timedelta(hours=48)).isoformat()
    log_habit("walk", old_ts)

    r = client.get("/habit/insights")
    insights = r.json()
    assert len(insights) == 1
    assert insights[0]["status"] in ("decaying", "critical")
    assert insights[0]["nudge"] is not None


# ---------- Tracker Service Unit Tests ----------
def test_streak_consecutive_days():
    from core.database import log_habit

    today = datetime.utcnow()
    for i in range(5):
        ts = (today - timedelta(days=i)).isoformat()
        log_habit("walk", ts)

    from services.tracker import calculate_score

    result = calculate_score("walk")
    assert result["streak_days"] == 5


def test_streak_broken():
    from core.database import log_habit

    today = datetime.utcnow()
    log_habit("walk", today.isoformat())
    log_habit("walk", (today - timedelta(days=3)).isoformat())

    from services.tracker import calculate_score

    result = calculate_score("walk")
    assert result["streak_days"] == 1  # gap breaks streak


# ---------- Insights Service Unit Tests ----------
def test_classify_strength():
    from services.insights import classify_strength

    assert classify_strength(100) == "strong"
    assert classify_strength(50) == "moderate"
    assert classify_strength(20) == "decaying"
    assert classify_strength(5) == "critical"
