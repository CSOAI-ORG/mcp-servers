"""
Base webhook handler for MEOK AI Labs
"""

import hashlib
import hmac
import json
import logging
from enum import Enum
from typing import Any, Callable, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    GOVERNANCE_ANALYSIS = "governance.analysis"
    GOVERNANCE_VIOLATION = "governance.violation"
    MEMORY_STORED = "memory.stored"
    MEMORY_QUERIED = "memory.queried"
    AGENT_TASK_CREATED = "agent.task.created"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    AGENT_TASK_FAILED = "agent.task.failed"
    CONSCIOUSNESS_STATE_CHANGED = "consciousness.state_changed"
    CONSCIOUSNESS_DREAM_STARTED = "consciousness.dream_started"
    CONSCIOUSNESS_DREAM_COMPLETED = "consciousness.dream_completed"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"
    ERROR_OCCURRED = "error.occurred"


class WebhookHandler:
    """
    Base webhook handler with signature verification

    Usage:
        handler = WebhookHandler(
            webhook_secret="your-secret",
            handlers={
                EventType.GOVERNANCE_ANALYSIS: handle_analysis,
                EventType.AGENT_TASK_COMPLETED: handle_task_done,
            }
        )

        # FastAPI route
        @app.post("/webhooks/meok")
        async def webhook(request: Request):
            return await handler.handle(request)
    """

    def __init__(
        self,
        webhook_secret: Optional[str] = None,
        handlers: Optional[Dict[EventType, Callable]] = None,
        verify_signatures: bool = True,
    ):
        self.webhook_secret = webhook_secret or os.environ.get("MEOK_WEBHOOK_SECRET")
        self.handlers = handlers or {}
        self.verify_signatures = verify_signatures
        self._client = httpx.AsyncClient(timeout=30.0)

    def verify_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: Optional[str] = None,
    ) -> bool:
        """
        Verify webhook signature

        Args:
            payload: Raw request body
            signature: X-Meok-Signature header value
            timestamp: X-Meok-Timestamp header value (optional, for replay protection)

        Returns:
            True if signature is valid
        """
        if not self.webhook_secret or not self.verify_signatures:
            return True

        if timestamp:
            age = int(time.time()) - int(timestamp)
            if age > 300:
                logger.warning("Webhook timestamp too old, possible replay attack")
                return False

        expected = hmac.new(
            self.webhook_secret.encode(), payload, hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)

    async def handle(
        self,
        request,
        sync_response: bool = False,
    ) -> Dict[str, Any]:
        """
        Process incoming webhook

        Args:
            request: FastAPI Request or similar
            sync_response: If True, wait for handlers; if False, process async

        Returns:
            Response dict with status
        """
        payload = await request.body()
        signature = request.headers.get("x-meok-signature", "")
        timestamp = request.headers.get("x-meok-timestamp")

        if self.verify_signatures and not self.verify_signature(
            payload, signature, timestamp
        ):
            return {"status": "error", "message": "Invalid signature"}

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON"}

        event_type = data.get("event_type") or data.get("type")
        event_data = data.get("data", {})

        handler = self.handlers.get(event_type)
        if handler:
            try:
                if sync_response:
                    result = await handler(event_data)
                    return {"status": "success", "result": result}
                else:
                    asyncio.create_task(handler(event_data))
                    return {"status": "accepted"}
            except Exception as e:
                logger.exception(f"Handler error for {event_type}")
                return {"status": "error", "message": str(e)}

        return {"status": "ignored", "message": f"No handler for {event_type}"}

    async def send(
        self,
        url: str,
        event_type: EventType,
        data: Dict[str, Any],
        secret: Optional[str] = None,
    ) -> httpx.Response:
        """
        Send webhook to external URL

        Args:
            url: Destination webhook URL
            event_type: Event type
            data: Event data
            secret: HMAC secret (uses self.webhook_secret if not provided)

        Returns:
            Response from destination
        """
        payload = json.dumps({"event_type": event_type, "data": data})
        headers = {
            "Content-Type": "application/json",
            "X-Meok-Event": event_type,
            "X-Meok-Delivery": str(uuid4()),
        }

        secret = secret or self.webhook_secret
        if secret:
            signature = hmac.new(
                secret.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Meok-Signature"] = f"sha256={signature}"

        return await self._client.post(url, content=payload, headers=headers)

    async def close(self):
        await self._client.aclose()


import asyncio
import os
import time
import uuid
