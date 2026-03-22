from models.usage import AppUsage, Alert
from core.config import settings
from typing import List
from datetime import datetime
from uuid import uuid4


class MockUsageTracker:
    def __init__(self):
        self.usage_records: List[AppUsage] = []
        self.alerts: List[Alert] = []

    def log_usage(self, app_name: str, minutes: int) -> AppUsage:
        record = AppUsage(
            app_name=app_name, minutes_used=minutes, timestamp=datetime.utcnow()
        )
        self.usage_records.append(record)
        self._check_threshold(app_name)
        return record

    def _check_threshold(self, app_name: str):
        total_time = sum(
            r.minutes_used for r in self.usage_records if r.app_name == app_name
        )
        if total_time >= settings.usage_threshold_minutes:
            self.alerts.append(
                Alert(
                    id=str(uuid4()),
                    message=f"Excessive usage detected for {app_name}. Consider a focus session.",
                    timestamp=datetime.utcnow(),
                )
            )

    def get_alerts(self) -> List[Alert]:
        return self.alerts


tracker = MockUsageTracker()
