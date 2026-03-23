"""
Webhook Alert Service — Sends notifications to external services
(Slack, Discord, Telegram) when critical vision events occur.
"""

import os
import httpx
from datetime import datetime

WEBHOOK_URL = os.environ.get("VISION_WEBHOOK_URL", "")


async def send_webhook_alert(event_type: str, description: str, event_id: str = ""):
    """Fire a webhook notification to configured external services."""
    if not WEBHOOK_URL:
        return {"status": "skipped", "reason": "No webhook URL configured"}

    payload = {
        "text": f"🚨 *Vision Alert*: {event_type}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Event:* `{event_type}`\n*Description:* {description}\n*Event ID:* `{event_id}`\n*Timestamp:* {datetime.utcnow().isoformat()}",
                },
            }
        ],
        # Discord-compatible format
        "content": f"🚨 **Vision Alert**: {event_type}\n{description}",
        "embeds": [
            {
                "title": f"Vision Alert: {event_type}",
                "description": description,
                "color": 16711680,
                "footer": {"text": f"Event ID: {event_id}"},
            }
        ],
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(WEBHOOK_URL, json=payload, timeout=5.0)
            return {
                "status": "sent",
                "webhook_status_code": resp.status_code,
                "event_type": event_type,
            }
    except Exception as e:
        return {"status": "failed", "error": str(e)}
