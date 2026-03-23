import pytest
from unittest.mock import patch, MagicMock
from services.badges import get_badges, generate_streak_card
from services.correlation import compute_correlations

@patch("services.badges.get_all_scores")
def test_get_badges_all_types(mock_scores):
    # Mock scores to trigger various badges
    mock_scores.return_value = [
        {
            "habit_name": "meditation",
            "streak_days": 10,
            "raw_score": 1500,
            "decayed_score": 90,
            "last_log": "2026-03-23"
        },
        {
            "habit_name": "reading",
            "streak_days": 8,
            "raw_score": 100,
            "decayed_score": 85,
            "last_log": "2026-03-23"
        },
        {
            "habit_name": "exercise",
            "streak_days": 5,
            "raw_score": 50,
            "decayed_score": 82,
            "last_log": "2026-03-23"
        }
    ]
    
    badges = get_badges()
    assert badges["total_badges"] >= 4  # First Step, Week Warrior, Iron Habit, and Habit Architect
    ids = [b["badge_id"] for b in badges["earned"]]
    assert "habit_cluster" in ids
    assert "week_streak" in ids
    assert "strong_habit" in ids

def test_streak_card_not_found():
    with patch("services.badges.get_all_scores", return_value=[]):
        card = generate_streak_card("nonexistent")
        assert "error" in card

@patch("services.correlation.get_all_scores")
def test_compute_correlations_logic(mock_scores):
    mock_scores.return_value = [
        {
            "habit_name": "coding",
            "streak_days": 10,
            "decayed_score": 95
        },
        {
            "habit_name": "doomscrolling_prevention",
            "streak_days": 0,
            "decayed_score": 10
        }
    ]
    
    report = compute_correlations()
    assert report["summary"]["strong"] == 1
    assert report["summary"]["weak"] == 1
    types = [c["type"] for c in report["correlations"]]
    assert "positive_correlation" in types
    assert "negative_correlation" in types
