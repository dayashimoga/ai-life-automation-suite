"""Usage session analyzer - processes app usage sessions for doomscroll tracking."""


class UsageAnalyzer:
    def __init__(self):
        self.sessions = []

    def process_session(self, usage_request):
        """Process a usage tracking request and store it."""
        self.sessions.append(
            {
                "app_name": usage_request.app_name,
                "minutes": usage_request.minutes,
            }
        )

    def get_total_minutes(self, app_name: str = None) -> int:
        if app_name:
            return sum(s["minutes"] for s in self.sessions if s["app_name"] == app_name)
        return sum(s["minutes"] for s in self.sessions)


analyzer = UsageAnalyzer()
