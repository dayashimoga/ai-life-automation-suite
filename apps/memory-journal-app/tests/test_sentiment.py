import pytest
from services.sentiment import analyze_entries, _score_text

def test_score_text_positive():
    text = "I am so happy and excited today!"
    scores = _score_text(text)
    assert scores["positive"] > 0
    assert scores["negative"] == 0

def test_score_text_negative():
    text = "I feel exhausted and burnt out."
    scores = _score_text(text)
    assert scores["negative"] > 0
    assert scores["positive"] == 0

def test_analyze_entries_empty():
    report = analyze_entries([])
    assert report["burnout_risk"] == 0.0
    assert "Keep journaling" in report["recommendation"]

def test_analyze_entries_burnout():
    entries = [
        {"caption": "I am exhausted and overwhelmed"},
        {"caption": "Everything is hopeless and I am depressed"}
    ]
    report = analyze_entries(entries)
    assert report["burnout_risk"] > 0.6
    assert report["mood_trend"] == "declining"
    assert "Signs of burnout" in report["recommendation"]

def test_analyze_entries_positive():
    entries = [
        {"caption": "I am grateful and happy"},
        {"caption": "Feeling energized and motivated"}
    ]
    report = analyze_entries(entries)
    assert report["burnout_risk"] < 0.2
    assert report["mood_trend"] == "positive"
    assert "positive mindset" in report["recommendation"]

def test_analyze_entries_mixed():
    entries = [
        {"caption": "I am tired but happy"},
        {"caption": "A bit stressed but productive"}
    ]
    report = analyze_entries(entries)
    assert 0.2 < report["burnout_risk"] < 0.6
    assert report["mood_trend"] in ["mixed", "stressed"]
