"""
MEOK AI Labs - FastAPI Webhook Server Example
Run with: uvicorn webhooks.python.example_server:app --port 8080
"""

import os
import asyncio
import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

from meokai.webhooks.base import WebhookHandler, EventType
from meokai.webhooks.governance import GovernanceWebhookHandler, create_slack_alert
from meokai.webhooks.memory import MemoryWebhookHandler
from meokai.webhooks.agent import AgentWebhookHandler, create_retry_payload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MEOK AI Webhooks")


class TaskCreate(BaseModel):
    task_id: str
    agent_id: str
    instruction: str
    priority: str = "normal"


async def handle_violation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Custom handler for governance violations"""
    logger.warning(f"Critical violation: {data.get('violation_type')}")
    return {"alert_sent": True}


async def handle_task_completed(data: Dict[str, Any]) -> Dict[str, Any]:
    """Custom handler for completed tasks"""
    logger.info(f"Task {data.get('task_id')} completed")
    return {"result_stored": True}


async def handle_memory_stored(data: Dict[str, Any]) -> Dict[str, Any]:
    """Custom handler for stored memories"""
    logger.debug(f"Memory {data.get('memory_id')} stored")
    return {"indexed": True}


governance_handler = GovernanceWebhookHandler(on_violation=handle_violation)
memory_handler = MemoryWebhookHandler(on_stored=handle_memory_stored)
agent_handler = AgentWebhookHandler(on_completed=handle_task_completed)

webhook_handler = WebhookHandler(
    webhook_secret=os.environ.get("MEOK_WEBHOOK_SECRET"),
    handlers={
        EventType.GOVERNANCE_ANALYSIS: governance_handler.handle_analysis,
        EventType.GOVERNANCE_VIOLATION: governance_handler.handle_violation,
        EventType.MEMORY_STORED: memory_handler.handle_stored,
        EventType.MEMORY_QUERIED: memory_handler.handle_queried,
        EventType.AGENT_TASK_CREATED: agent_handler.handle_created,
        EventType.AGENT_TASK_COMPLETED: agent_handler.handle_completed,
        EventType.AGENT_TASK_FAILED: agent_handler.handle_failed,
    },
)


@app.post("/webhooks/meok")
async def webhook_endpoint(request: Request):
    """Main MEOK webhook endpoint"""
    result = await webhook_handler.handle(request)
    return result


@app.post("/webhooks/test")
async def test_webhook(task_data: TaskCreate):
    """Simulate a webhook event for testing"""
    result = await webhook_handler.send(
        url="https://your-app.com/webhooks/meok",
        event_type=EventType.AGENT_TASK_CREATED,
        data=task_data.dict(),
    )
    return {"sent": result.status_code == 200}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "meok-webhooks"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
