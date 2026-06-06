#!/usr/bin/env python3
"""
MEOK AI Labs - Webhook Testing Tool
Test and debug webhooks locally
"""

import asyncio
import json
import hmac
import hashlib
import time
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
import httpx
from aiohttp import web


class WebhookEvent(str, Enum):
    GOVERNANCE_ANALYSIS = "governance.analysis"
    GOVERNANCE_VIOLATION = "governance.violation"
    MEMORY_STORED = "memory.stored"
    MEMORY_QUERIED = "memory.queried"
    AGENT_TASK_CREATED = "agent.task.created"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    AGENT_TASK_FAILED = "agent.task.failed"
    CONSCIOUSNESS_STATE_CHANGED = "consciousness.state_changed"


@dataclass
class WebhookRequest:
    url: str
    event_type: WebhookEvent
    data: Dict
    secret: Optional[str] = None
    retries: int = 3
    timeout: float = 10.0


@dataclass
class WebhookResponse:
    status_code: int
    body: str
    headers: Dict
    duration_ms: float
    success: bool
    error: Optional[str] = None


class WebhookBuilder:
    """Build webhook payloads"""

    @staticmethod
    def governance_analysis(
        content_hash: str, score: float, passed: bool, violations: List
    ) -> Dict:
        return {
            "event_type": WebhookEvent.GOVERNANCE_ANALYSIS.value,
            "data": {
                "content_hash": content_hash,
                "score": score,
                "passed": passed,
                "violations": violations,
                "framework": "constitutional",
                "timestamp": time.time(),
            },
        }

    @staticmethod
    def governance_violation(
        content_hash: str, violation_type: str, severity: str
    ) -> Dict:
        return {
            "event_type": WebhookEvent.GOVERNANCE_VIOLATION.value,
            "data": {
                "content_hash": content_hash,
                "violation_type": violation_type,
                "severity": severity,
                "timestamp": time.time(),
            },
        }

    @staticmethod
    def memory_stored(memory_id: str, content: str, memory_type: str) -> Dict:
        return {
            "event_type": WebhookEvent.MEMORY_STORED.value,
            "data": {
                "memory_id": memory_id,
                "content_preview": content[:100],
                "type": memory_type,
                "timestamp": time.time(),
            },
        }

    @staticmethod
    def agent_task_completed(task_id: str, agent_id: str, result: Dict) -> Dict:
        return {
            "event_type": WebhookEvent.AGENT_TASK_COMPLETED.value,
            "data": {
                "task_id": task_id,
                "agent_id": agent_id,
                "result": result,
                "timestamp": time.time(),
            },
        }


class WebhookTester:
    """Test webhooks locally"""

    def __init__(self):
        self.received: List[Dict] = []
        self.signature_verified: List[bool] = []
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        self.app.router.add_post("/webhook", self.handle_webhook)
        self.app.router.add_get("/webhook/status", self.get_status)

    async def handle_webhook(self, request):
        body = await request.read()
        signature = request.headers.get("X-Meok-Signature", "")
        timestamp = request.headers.get("X-Meok-Timestamp", "")
        event_type = request.headers.get("X-Meok-Event", "unknown")

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        verified = False
        secret = request.app.get("secret")
        if secret and signature:
            expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
            verified = hmac.compare_digest(f"sha256={expected}", signature)

        self.received.append(
            {
                "event_type": event_type,
                "data": data,
                "signature": signature[:20] + "..." if signature else None,
                "verified": verified,
                "timestamp": time.time(),
                "headers": dict(request.headers),
            }
        )

        return web.json_response(
            {"received": True, "event_type": event_type, "verified": verified}
        )

    async def get_status(self, request):
        return web.json_response(
            {
                "total_received": len(self.received),
                "signatures_verified": sum(self.signature_verified),
                "recent": self.received[-10:],
            }
        )

    async def start_server(
        self, host: str = "127.0.0.1", port: int = 8080, secret: str = None
    ):
        if secret:
            self.app["secret"] = secret
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        return f"http://{host}:{port}/webhook"

    def get_received(self) -> List[Dict]:
        return self.received

    def clear(self):
        self.received = []


class WebhookSender:
    """Send webhooks to endpoints"""

    def __init__(self):
        self.history: List[WebhookResponse] = []

    def _sign(self, payload: bytes, secret: str) -> str:
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return f"sha256={signature}"

    async def send(self, webhook: WebhookRequest) -> WebhookResponse:
        start = time.time()

        headers = {
            "Content-Type": "application/json",
            "X-Meok-Event": webhook.event_type.value,
            "X-Meok-Delivery": str(uuid.uuid4()),
            "X-Meok-Timestamp": str(int(time.time())),
        }

        if webhook.secret:
            payload = json.dumps(webhook.data).encode()
            headers["X-Meok-Signature"] = self._sign(payload, webhook.secret)

        for attempt in range(webhook.retries):
            try:
                async with httpx.AsyncClient(timeout=webhook.timeout) as client:
                    response = await client.post(
                        webhook.url, content=json.dumps(webhook.data), headers=headers
                    )

                duration_ms = (time.time() - start) * 1000

                result = WebhookResponse(
                    status_code=response.status_code,
                    body=response.text[:500],
                    headers=dict(response.headers),
                    duration_ms=duration_ms,
                    success=200 <= response.status_code < 300,
                )

                self.history.append(result)
                return result

            except Exception as e:
                if attempt == webhook.retries - 1:
                    result = WebhookResponse(
                        status_code=0,
                        body="",
                        headers={},
                        duration_ms=(time.time() - start) * 1000,
                        success=False,
                        error=str(e),
                    )
                    self.history.append(result)
                    return result

            await asyncio.sleep(0.5 * (attempt + 1))

    async def send_batch(self, webhooks: List[WebhookRequest]) -> List[WebhookResponse]:
        tasks = [self.send(w) for w in webhooks]
        return await asyncio.gather(*tasks)

    def get_history(self) -> List[WebhookResponse]:
        return self.history

    def print_history(self):
        print("\n" + "=" * 70)
        print("Webhook Send History")
        print("=" * 70)

        for i, resp in enumerate(self.history[-10:], 1):
            status = "✓" if resp.success else "✗"
            print(f"\n{i}. [{status}] {resp.status_code} - {resp.duration_ms:.1f}ms")
            if resp.error:
                print(f"   Error: {resp.error}")
            else:
                print(f"   Body: {resp.body[:100]}...")


async def demo_local_testing():
    """Demo local webhook testing"""
    print("MEOK AI Labs - Webhook Testing Tool")
    print("=" * 50)

    tester = WebhookTester()
    url = await tester.start_server(port=8080, secret="test-secret")
    print(f"\nTest server started: {url}")

    sender = WebhookSender()

    test_webhooks = [
        WebhookRequest(
            url=url,
            event_type=WebhookEvent.GOVERNANCE_ANALYSIS,
            data=WebhookBuilder.governance_analysis("abc123", 0.85, True, []),
            secret="test-secret",
        ),
        WebhookRequest(
            url=url,
            event_type=WebhookEvent.MEMORY_STORED,
            data=WebhookBuilder.memory_stored(
                "mem123", "User prefers dark mode", "semantic"
            ),
            secret="test-secret",
        ),
        WebhookRequest(
            url=url,
            event_type=WebhookEvent.GOVERNANCE_VIOLATION,
            data=WebhookBuilder.governance_violation(
                "def456", "harmful_content", "high"
            ),
            secret="test-secret",
        ),
    ]

    print("\nSending test webhooks...")
    results = await sender.send_batch(test_webhooks)

    for result in results:
        status = "✓" if result.success else "✗"
        print(f"  {status} {result.status_code} ({result.duration_ms:.1f}ms)")

    sender.print_history()

    status = await httpx.AsyncClient().get(
        f"{url.replace('/webhook', '')}/webhook/status"
    )
    data = await status.json()
    print(f"\nServer received {data['total_received']} webhooks")
    print(f"Signatures verified: {data['signatures_verified']}")


if __name__ == "__main__":
    asyncio.run(demo_local_testing())
