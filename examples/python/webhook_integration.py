"""
MEOK AI Labs - Webhook Integration Examples
Real-time event processing with webhooks
"""

import os
import json
import asyncio
from meokai.webhooks.base import WebhookHandler, EventType
from meokai.webhooks.governance import create_slack_alert, create_email_alert
from meokai.webhooks.agent import aggregate_task_metrics


async def handle_violation_alert(data):
    """Send Slack alert for governance violations"""
    slack_payload = create_slack_alert(data)

    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url:
        import httpx

        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=slack_payload)

    return {"slack_notified": True}


async def handle_critical_violation_email(data):
    """Send email for critical violations"""
    if data.get("severity") == "critical":
        email_payload = create_email_alert(data)

        print(f"Would send email to: {email_payload['to']}")
        print(f"Subject: {email_payload['subject']}")

    return {"email_queued": True}


async def handle_completed_tasks_batch(data):
    """Process completed task metrics"""
    metrics = aggregate_task_metrics(data.get("tasks", []))
    print(f"Task metrics: {json.dumps(metrics, indent=2)}")
    return {"metrics_stored": True}


async def auto_retry_failed(data):
    """Automatically retry failed tasks"""
    if data.get("retry_count", 0) < 3:
        return {"retry_scheduled": True, "next_retry": data.get("retry_count", 0) + 1}
    return {"max_retries_exceeded": True}


def create_governance_webhook_handler() -> WebhookHandler:
    """Create handler for governance events"""
    return WebhookHandler(
        webhook_secret=os.environ.get("MEOK_WEBHOOK_SECRET"),
        handlers={
            EventType.GOVERNANCE_ANALYSIS: handle_violation_alert,
            EventType.GOVERNANCE_VIOLATION: handle_critical_violation_email,
        },
    )


def create_agent_webhook_handler() -> WebhookHandler:
    """Create handler for agent events"""
    return WebhookHandler(
        webhook_secret=os.environ.get("MEOK_WEBHOOK_SECRET"),
        handlers={
            EventType.AGENT_TASK_COMPLETED: handle_completed_tasks_batch,
            EventType.AGENT_TASK_FAILED: auto_retry_failed,
        },
    )


async def example_outgoing_webhook():
    """Send webhook to external service"""
    handler = WebhookHandler(webhook_secret="your-secret")

    await handler.send(
        url="https://api.example.com/webhook",
        event_type=EventType.MEMORY_STORED,
        data={
            "memory_id": "mem_123",
            "content_preview": "Important discovery...",
            "tags": ["research", "important"],
        },
    )

    await handler.close()


async def example_test_webhook():
    """Test webhook with simulated event"""
    handler = create_governance_webhook_handler()

    test_violation = {
        "content_hash": "abc123",
        "framework": "constitutional",
        "severity": "high",
        "violation_type": "harmful_content",
        "description": "Request for dangerous instructions",
        "timestamp": "2026-04-05T12:00:00Z",
    }

    result = await handler.handle(MockRequest(test_violation), sync_response=True)

    print(f"Webhook result: {result}")
    await handler.close()
    return result


class MockRequest:
    """Mock request object for testing"""

    def __init__(self, data: dict):
        self._data = json.dumps(data).encode()

    async def body(self):
        return self._data

    @property
    def headers(self):
        return {"x-meok-signature": "sha256=test", "x-meok-timestamp": "1234567890"}


if __name__ == "__main__":
    asyncio.run(example_test_webhook())
