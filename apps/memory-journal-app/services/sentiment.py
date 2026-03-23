"""
Sentiment & Burnout Prediction — Lightweight keyword-based wellbeing analysis
on Memory Journal captions to detect early signs of burnout or distress.

No heavy ML dependencies — pure Python keyword scoring for zero-latency results.
"""

import re
from typing import List, Dict

# Weighted term banks
NEGATIVE_TERMS = {
    # High weight — strong burnout signals
    "exhausted": 3,
    "burnout": 3,
    "overwhelmed": 3,
    "hopeless": 3,
    "can't cope": 3,
    "breakdown": 3,
    "depressed": 3,
    "crying": 2,
    "anxiety": 2,
    "panic": 2,
    # Medium weight
    "tired": 1.5,
    "stressed": 1.5,
    "anxious": 1.5,
    "worried": 1.5,
    "lonely": 1.5,
    "frustrated": 1,
    "angry": 1,
    "sad": 1,
    "bored": 1,
    "drained": 1.5,
    # Low weight
    "bad": 0.5,
    "hard": 0.5,
    "tough": 0.5,
    "difficult": 0.5,
    "ugh": 0.5,
}

POSITIVE_TERMS = {
    # High weight — strong wellness signals
    "grateful": 2,
    "productive": 2,
    "energized": 2,
    "happy": 2,
    "thriving": 2,
    "accomplished": 2,
    "excited": 2,
    "inspired": 2,
    "motivated": 2,
    "joyful": 2,
    # Medium weight
    "good": 1,
    "great": 1,
    "calm": 1,
    "relaxed": 1,
    "peaceful": 1,
    "focused": 1,
    "confident": 1,
    "healthy": 1,
    "rested": 1,
    "bright": 0.5,
}


def _score_text(text: str) -> Dict[str, float]:
    """Score a single text for positive/negative sentiment."""
    text_lower = text.lower()
    neg_score = sum(
        weight
        for term, weight in NEGATIVE_TERMS.items()
        if re.search(r"\b" + re.escape(term) + r"\b", text_lower)
    )
    pos_score = sum(
        weight
        for term, weight in POSITIVE_TERMS.items()
        if re.search(r"\b" + re.escape(term) + r"\b", text_lower)
    )
    return {"negative": neg_score, "positive": pos_score}


def analyze_entries(entries: List[Dict]) -> Dict:
    """
    Analyze a list of journal entries for sentiment trends.

    Args:
        entries: List of dicts with at least a 'caption' or 'content' key.

    Returns:
        A wellness report with burnout_risk (0.0-1.0), mood_trend, and top signals.
    """
    if not entries:
        return {
            "burnout_risk": 0.0,
            "mood_trend": "neutral",
            "total_entries_analyzed": 0,
            "signals": [],
            "recommendation": "📔 Keep journaling — your entries will unlock personalized wellness insights.",
        }

    total_neg = 0.0
    total_pos = 0.0
    signals = []

    for entry in entries:
        text = entry.get("caption") or entry.get("content") or entry.get("filename", "")
        scores = _score_text(text)
        total_neg += scores["negative"]
        total_pos += scores["positive"]
        if scores["negative"] > 2:
            signals.append(
                {
                    "entry": text[:50] + "..." if len(text) > 50 else text,
                    "signal": "high_stress",
                    "score": scores["negative"],
                }
            )

    total_signal = total_neg + total_pos + 0.001  # avoid division by zero
    burnout_risk = round(min(1.0, total_neg / total_signal), 2)

    if burnout_risk > 0.65:
        mood_trend, recommendation = (
            "declining",
            "🚨 Signs of burnout detected. Consider a digital detox day and reach out to someone you trust.",
        )
    elif burnout_risk > 0.40:
        mood_trend, recommendation = (
            "stressed",
            "⚠️ Elevated stress in your journal. Try a 5-minute breathing exercise before bed tonight.",
        )
    elif burnout_risk > 0.20:
        mood_trend, recommendation = (
            "mixed",
            "😐 Some mixed emotions lately. A short walk outside could reset your mood.",
        )
    else:
        mood_trend, recommendation = (
            "positive",
            "✅ Your journal reflects a positive mindset! Keep the momentum going.",
        )

    return {
        "burnout_risk": burnout_risk,
        "mood_trend": mood_trend,
        "total_entries_analyzed": len(entries),
        "signals": signals[:5],
        "recommendation": recommendation,
    }
