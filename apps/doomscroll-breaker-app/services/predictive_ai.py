"""
ML-Based Doomscroll Prediction — Replaces the static risk_factors dict with
a personalized prediction model that learns from the user's historical patterns.
Uses exponential weighted moving average (EWMA) for pattern detection.
"""
import datetime
import random
import sqlite3
import os

from models.usage import UsageRequest


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "usage_history.db")


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            hour INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            duration_minutes REAL DEFAULT 0,
            risk_score REAL DEFAULT 0,
            was_doomscroll BOOLEAN DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


class AdaptivePredictor:
    """
    ML-inspired adaptive prediction engine that learns from past usage patterns.
    Uses EWMA (Exponential Weighted Moving Average) over historical sessions
    at each (hour, day_of_week) slot to personalize risk scoring.
    """

    # Base heuristic risk as a fallback when no history exists
    BASE_RISK = {
        0: 0.70, 1: 0.85, 2: 0.95, 3: 0.90, 4: 0.60, 5: 0.20,
        6: 0.10, 7: 0.15, 8: 0.20, 9: 0.25, 10: 0.20, 11: 0.15,
        12: 0.30, 13: 0.35, 14: 0.25, 15: 0.20, 16: 0.30, 17: 0.40,
        18: 0.50, 19: 0.60, 20: 0.70, 21: 0.75, 22: 0.85, 23: 0.90
    }

    ADDICTIVE_APPS = ["tiktok", "instagram", "twitter", "reddit", "youtube", "shorts"]
    EWMA_ALPHA = 0.3  # Higher = more weight on recent sessions

    def _get_historical_risk(self, hour: int, day: int) -> float:
        """Query the EWMA of historical risk scores for this time slot."""
        try:
            db = _get_db()
            rows = db.execute(
                "SELECT risk_score FROM usage_log WHERE hour = ? AND day_of_week = ? ORDER BY timestamp DESC LIMIT 20",
                (hour, day)
            ).fetchall()
            db.close()

            if not rows:
                return self.BASE_RISK.get(hour, 0.5)

            # EWMA computation
            ewma = rows[0]["risk_score"]
            for row in rows[1:]:
                ewma = self.EWMA_ALPHA * row["risk_score"] + (1 - self.EWMA_ALPHA) * ewma
            return ewma
        except Exception:
            return self.BASE_RISK.get(hour, 0.5)

    def _log_session(self, app_name: str, hour: int, day: int, risk: float, was_doom: bool):
        """Persist this session for future learning."""
        try:
            db = _get_db()
            db.execute(
                "INSERT INTO usage_log (app_name, hour, day_of_week, risk_score, was_doomscroll) VALUES (?, ?, ?, ?, ?)",
                (app_name, hour, day, risk, was_doom)
            )
            db.commit()
            db.close()
        except Exception:
            pass

    def predict_risk(self, session: UsageRequest) -> dict:
        """
        Adaptive prediction combining historical EWMA with heuristic features.
        """
        now = datetime.datetime.utcnow()
        hour = now.hour
        day = now.weekday()
        app = session.app_name.lower()

        # 1. Historical personalized baseline
        hist_risk = self._get_historical_risk(hour, day)

        # 2. App-specific dopamine modifier
        app_modifier = 0.15 if any(a in app for a in self.ADDICTIVE_APPS) else 0.0

        # 3. Late-night amplifier (circadian pattern)
        circadian_boost = 0.1 if hour in [0, 1, 2, 3, 23] else 0.0

        # 4. Weekend amplifier
        weekend_boost = 0.05 if day in [5, 6] else 0.0

        # 5. Stochastic variance
        noise = random.uniform(-0.03, 0.03)

        # Combine all features
        raw_risk = hist_risk + app_modifier + circadian_boost + weekend_boost + noise
        final_risk = min(max(raw_risk, 0.01), 0.99)

        will_doomscroll = final_risk >= 0.70
        confidence = min(0.95, 0.5 + abs(final_risk - 0.5))

        # Log this prediction for future learning
        self._log_session(app, hour, day, final_risk, will_doomscroll)

        return {
            "prediction_score": round(final_risk, 3),
            "confidence": round(confidence, 3),
            "will_doomscroll": will_doomscroll,
            "intervention_recommended": will_doomscroll,
            "model_type": "adaptive_ewma",
            "features_used": {
                "historical_baseline": round(hist_risk, 3),
                "app_modifier": app_modifier,
                "circadian_boost": circadian_boost,
                "weekend_boost": weekend_boost,
            },
            "message": (
                "🚨 CRITICAL RISK: High probability of doomscroll spiral. "
                "Deploying preemptive 15-minute Focus Block."
                if will_doomscroll
                else "✅ Safe usage probability. Proceed with caution."
            ),
            "timestamp": now.isoformat(),
        }

    def get_usage_analytics(self) -> dict:
        """Return aggregate usage analytics for the dashboard."""
        try:
            db = _get_db()
            total = db.execute("SELECT COUNT(*) as cnt FROM usage_log").fetchone()["cnt"]
            doom_count = db.execute("SELECT COUNT(*) as cnt FROM usage_log WHERE was_doomscroll = 1").fetchone()["cnt"]
            avg_risk = db.execute("SELECT AVG(risk_score) as avg FROM usage_log").fetchone()["avg"] or 0
            top_apps = db.execute(
                "SELECT app_name, COUNT(*) as cnt FROM usage_log GROUP BY app_name ORDER BY cnt DESC LIMIT 5"
            ).fetchall()
            hotspot_hours = db.execute(
                "SELECT hour, AVG(risk_score) as avg_risk FROM usage_log GROUP BY hour ORDER BY avg_risk DESC LIMIT 5"
            ).fetchall()
            db.close()

            return {
                "total_sessions": total,
                "doomscroll_sessions": doom_count,
                "average_risk": round(avg_risk, 3),
                "top_apps": [{"app": r["app_name"], "sessions": r["cnt"]} for r in top_apps],
                "risk_hotspots": [{"hour": r["hour"], "avg_risk": round(r["avg_risk"], 3)} for r in hotspot_hours],
            }
        except Exception:
            return {"total_sessions": 0, "doomscroll_sessions": 0, "average_risk": 0}


predictor = AdaptivePredictor()
