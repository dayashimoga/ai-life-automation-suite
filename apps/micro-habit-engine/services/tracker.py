import math
from datetime import datetime
from core.database import get_logs, get_distinct_habits


SCORE_PER_LOG = 10
DECAY_RATE_PER_HOUR = 0.05  # 5% per hour


def calculate_score(habit_name: str) -> dict:
    logs = get_logs(habit_name)
    if not logs:
        return {"raw_score": 0, "decayed_score": 0, "streak_days": 0, "last_logged": None}

    raw_score = len(logs) * SCORE_PER_LOG
    last_logged_str = logs[0]["timestamp"]
    last_logged_dt = datetime.fromisoformat(last_logged_str)
    hours_since = (datetime.utcnow() - last_logged_dt).total_seconds() / 3600

    # Exponential decay: score * e^(-rate * hours)
    decayed_score = round(raw_score * math.exp(-DECAY_RATE_PER_HOUR * hours_since), 2)

    # Streak calculation: count consecutive days with at least one log
    streak = _calculate_streak(logs)

    return {
        "raw_score": raw_score,
        "decayed_score": decayed_score,
        "streak_days": streak,
        "last_logged": last_logged_str,
    }


def _calculate_streak(logs: list) -> int:
    if not logs:
        return 0

    dates = set()
    for log in logs:
        dt = datetime.fromisoformat(log["timestamp"])
        dates.add(dt.date())

    sorted_dates = sorted(dates, reverse=True)
    streak = 1
    for i in range(1, len(sorted_dates)):
        diff = (sorted_dates[i - 1] - sorted_dates[i]).days
        if diff == 1:
            streak += 1
        else:
            break
    return streak


def get_all_scores() -> list:
    habits = get_distinct_habits()
    scores = []
    for h in habits:
        s = calculate_score(h)
        s["habit_name"] = h
        scores.append(s)
    return scores
