from services.tracker import get_all_scores

NUDGES = {
    "drink_water": "💧 Stay hydrated! A glass of water boosts focus by 14%.",
    "stretch": "🧘 Quick stretch! Just 30 seconds releases tension and improves circulation.",
    "walk": "🚶 A 5 minute walk resets your brain and sparks creativity.",
}

DEFAULT_NUDGE = "🌟 Keep going! Consistency is what builds lasting change."


def classify_strength(decayed_score: float) -> str:
    if decayed_score >= 80:
        return "strong"
    elif decayed_score >= 40:
        return "moderate"
    elif decayed_score >= 15:
        return "decaying"
    else:
        return "critical"


def generate_insights() -> list:
    scores = get_all_scores()
    insights = []
    for s in scores:
        status = classify_strength(s["decayed_score"])
        nudge = None
        if status in ("decaying", "critical"):
            nudge = NUDGES.get(s["habit_name"], DEFAULT_NUDGE)

        insights.append(
            {
                "habit_name": s["habit_name"],
                "status": status,
                "nudge": nudge,
                "streak_days": s["streak_days"],
                "total_logs": int(s["raw_score"] / 10),
            }
        )
    return insights
