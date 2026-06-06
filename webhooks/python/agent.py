"""
Agent webhook handlers
"""

from typing import Any, Callable, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AgentWebhookHandler:
    """
    Handle agent-related webhooks

    Events:
        - agent.task.created: New task created
        - agent.task.completed: Task completed
        - agent.task.failed: Task failed
    """

    def __init__(
        self,
        on_created: Optional[Callable] = None,
        on_completed: Optional[Callable] = None,
        on_failed: Optional[Callable] = None,
    ):
        self.on_created = on_created
        self.on_completed = on_completed
        self.on_failed = on_failed

    async def handle_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task created event

        Data expected:
            - task_id: str
            - agent_id: str
            - instruction: str
            - priority: str
            - created_at: str
        """
        logger.info(
            f"Task created: {data.get('task_id')} for agent {data.get('agent_id')}"
        )

        if self.on_created:
            return await self.on_created(data)

        return {"queued": True}

    async def handle_completed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task completed event

        Data expected:
            - task_id: str
            - agent_id: str
            - result: Any
            - duration_ms: float
            - completed_at: str
        """
        logger.info(f"Task completed: {data.get('task_id')}")

        if self.on_completed:
            return await self.on_completed(data)

        return {"acknowledged": True}

    async def handle_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task failed event

        Data expected:
            - task_id: str
            - agent_id: str
            - error: str
            - error_type: str
            - failed_at: str
            - retry_count: int
        """
        logger.error(f"Task failed: {data.get('task_id')} error: {data.get('error')}")

        if self.on_failed:
            return await self.on_failed(data)

        return {"alerted": True}


def create_task_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a human-readable task summary

    Args:
        data: Task event data

    Returns:
        Summary dict
    """
    return {
        "summary": f"Task {data.get('task_id')} "
        f"({data.get('agent_id')}) - {data.get('status', 'unknown')}",
        "duration": data.get("duration_ms", 0) / 1000,
        "priority": data.get("priority", "normal"),
    }


def create_retry_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create payload to retry a failed task

    Args:
        data: Failed task data

    Returns:
        Retry payload
    """
    return {
        "task_id": data.get("task_id"),
        "agent_id": data.get("agent_id"),
        "instruction": data.get("instruction"),
        "priority": "high",
        "retry_count": data.get("retry_count", 0) + 1,
    }


def aggregate_task_metrics(tasks: List[Dict]) -> Dict[str, Any]:
    """
    Aggregate metrics from multiple tasks

    Args:
        tasks: List of task data dicts

    Returns:
        Metrics summary
    """
    completed = [t for t in tasks if t.get("status") == "completed"]
    failed = [t for t in tasks if t.get("status") == "failed"]

    durations = [t.get("duration_ms", 0) for t in completed]

    return {
        "total_tasks": len(tasks),
        "completed": len(completed),
        "failed": len(failed),
        "success_rate": len(completed) / len(tasks) if tasks else 0,
        "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
        "min_duration_ms": min(durations) if durations else 0,
        "max_duration_ms": max(durations) if durations else 0,
    }
