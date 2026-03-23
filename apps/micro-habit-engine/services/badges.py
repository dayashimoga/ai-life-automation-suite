"""
Achievement Badges System — Gamification layer for micro-habit engagement.
Awards badges for milestones and generates shareable streak cards.
"""

from services.tracker import get_all_scores
from datetime import datetime

BADGE_DEFINITIONS = [
    {
        "id": "first_log",
        "name": "🌱 First Step",
        "description": "Logged your first habit ever",
        "condition": lambda s: s["raw_score"] >= 10,
    },
    {
        "id": "week_streak",
        "name": "🔥 Week Warrior",
        "description": "Maintained a 7-day streak",
        "condition": lambda s: s["streak_days"] >= 7,
    },
    {
        "id": "month_streak",
        "name": "⭐ Monthly Master",
        "description": "Maintained a 30-day streak",
        "condition": lambda s: s["streak_days"] >= 30,
    },
    {
        "id": "century_club",
        "name": "🏆 Century Club",
        "description": "Logged a habit 100 times",
        "condition": lambda s: s["raw_score"] >= 1000,
    },
    {
        "id": "strong_habit",
        "name": "💪 Iron Habit",
        "description": "Achieved a habit strength score above 80",
        "condition": lambda s: s["decayed_score"] >= 80,
    },
    {
        "id": "habit_cluster",
        "name": "🔗 Habit Architect",
        "description": "Maintain 3+ strong habits simultaneously",
        "condition": None,  # Special: checked globally
    },
]


def get_badges() -> dict:
    """Calculate earned badges for all habits."""
    scores = get_all_scores()
    earned_badges = []
    in_progress = []

    strong_count = sum(1 for s in scores if s["decayed_score"] >= 80)

    for s in scores:
        for badge in BADGE_DEFINITIONS:
            if badge["id"] == "habit_cluster":
                continue
            if badge["condition"] and badge["condition"](s):
                badge_entry = {
                    "badge_id": badge["id"],
                    "name": badge["name"],
                    "description": badge["description"],
                    "habit": s["habit_name"],
                    "earned_at": datetime.utcnow().isoformat(),
                }
                if badge_entry not in earned_badges:
                    earned_badges.append(badge_entry)

    # Special cluster badge
    if strong_count >= 3:
        earned_badges.append(
            {
                "badge_id": "habit_cluster",
                "name": "🔗 Habit Architect",
                "description": "Maintain 3+ strong habits simultaneously",
                "habit": "global",
                "earned_at": datetime.utcnow().isoformat(),
            }
        )

    # In-progress badges
    for s in scores:
        if s["streak_days"] >= 3 and s["streak_days"] < 7:
            in_progress.append(
                {
                    "badge": "🔥 Week Warrior",
                    "habit": s["habit_name"],
                    "progress": f"{s['streak_days']}/7 days",
                }
            )
        if s["raw_score"] >= 500 and s["raw_score"] < 1000:
            in_progress.append(
                {
                    "badge": "🏆 Century Club",
                    "habit": s["habit_name"],
                    "progress": f"{s['raw_score'] // 10}/100 logs",
                }
            )

    return {
        "total_badges": len(earned_badges),
        "earned": earned_badges,
        "in_progress": in_progress,
        "generated_at": datetime.utcnow().isoformat(),
    }


def generate_streak_card(habit_name: str) -> dict:
    """Generate a shareable streak card for a specific habit."""
    scores = get_all_scores()
    target = None
    for s in scores:
        if s["habit_name"] == habit_name:
            target = s
            break

    if not target:
        return {"error": f"Habit '{habit_name}' not found"}

    return {
        "card_type": "streak_card",
        "habit_name": habit_name,
        "streak_days": target["streak_days"],
        "strength_score": round(target["decayed_score"], 1),
        "total_logs": target["raw_score"] // 10,
        "message": f"🔥 I've been doing {habit_name} for {target['streak_days']} days straight!",
        "share_text": f"I've built a {target['streak_days']}-day streak on {habit_name} using AI Life Automation Suite! 💪",
        "generated_at": datetime.utcnow().isoformat(),
    }
