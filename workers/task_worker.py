#!/usr/bin/env python3
"""
MEOK AI Labs - Worker System
Background task processing
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Task:
    id: str
    type: str
    payload: Dict[str, Any]
    priority: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None


class TaskQueue:
    """In-memory task queue (use Redis in production)"""

    def __init__(self):
        self.queue = asyncio.Queue()
        self.tasks: Dict[str, Task] = {}
        self.running = False

    async def enqueue(
        self, task_type: str, payload: Dict, priority: str = "normal"
    ) -> str:
        """Add task to queue"""
        task = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            payload=payload,
            priority=priority,
            status="pending",
            created_at=datetime.utcnow(),
        )

        self.tasks[task.id] = task
        await self.queue.put(task)

        logger.info(f"Enqueued task {task.id} of type {task_type}")
        return task.id

    async def dequeue(self) -> Optional[Task]:
        """Get next task from queue"""
        try:
            task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            task.status = "running"
            task.started_at = datetime.utcnow()
            return task
        except asyncio.TimeoutError:
            return None

    async def complete(self, task_id: str, result: Dict) -> None:
        """Mark task as completed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.result = result
            logger.info(f"Task {task_id} completed")

    async def fail(self, task_id: str, error: str) -> None:
        """Mark task as failed"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "failed"
            task.completed_at = datetime.utcnow()
            task.error = error
            logger.error(f"Task {task_id} failed: {error}")


class AnalysisWorker:
    """Worker for governance analysis tasks"""

    async def process(self, payload: Dict) -> Dict:
        """Process analysis task"""
        from meokai.governance import ConstitutionalAnalyzer

        analyzer = ConstitutionalAnalyzer()

        content = payload.get("content", "")
        framework = payload.get("framework", "constitutional")

        result = await analyzer.analyze(content, framework=framework)

        return {
            "task_type": "analysis",
            "result": result,
            "processed_at": datetime.utcnow().isoformat(),
        }


class MemoryWorker:
    """Worker for memory operations"""

    async def process(self, payload: Dict) -> Dict:
        """Process memory task"""
        from meokai.memory import VectorStore

        store = VectorStore()

        action = payload.get("action")
        user_id = payload.get("user_id")

        if action == "store":
            memory_id = await store.store(
                user_id=user_id,
                content=payload.get("content", ""),
                memory_type=payload.get("memory_type", "episodic"),
                tags=payload.get("tags", []),
                importance=payload.get("importance", 0.5),
            )
            return {"memory_id": memory_id, "action": "stored"}

        elif action == "query":
            results = await store.query(
                query=payload.get("query", ""),
                user_id=user_id,
                limit=payload.get("limit", 10),
            )
            return {"action": "queried", "results": results}

        return {"error": "Unknown action"}


class WorkerPool:
    """Pool of workers processing tasks"""

    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.queue = TaskQueue()
        self.workers = {
            "analysis": AnalysisWorker(),
            "memory": MemoryWorker(),
        }
        self.running = False

    async def submit(
        self, task_type: str, payload: Dict, priority: str = "normal"
    ) -> str:
        """Submit a task for processing"""
        return await self.queue.enqueue(task_type, payload, priority)

    async def process_task(self, task: Task) -> None:
        """Process a single task"""
        worker = self.workers.get(task.type)

        if not worker:
            await self.queue.fail(task.id, f"Unknown task type: {task.type}")
            return

        try:
            result = await worker.process(task.payload)
            await self.queue.complete(task.id, result)
        except Exception as e:
            await self.queue.fail(task.id, str(e))

    async def worker_loop(self, worker_id: int) -> None:
        """Worker loop"""
        logger.info(f"Worker {worker_id} started")

        while self.running:
            task = await self.queue.dequeue()

            if task:
                await self.process_task(task)

            await asyncio.sleep(0.1)

        logger.info(f"Worker {worker_id} stopped")

    async def start(self) -> None:
        """Start all workers"""
        self.running = True

        workers = [
            asyncio.create_task(self.worker_loop(i)) for i in range(self.num_workers)
        ]

        logger.info(f"Started {self.num_workers} workers")

        await asyncio.gather(*workers)

    async def stop(self) -> None:
        """Stop all workers"""
        self.running = False
        logger.info("Workers stopping...")


async def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)

    pool = WorkerPool(num_workers=4)

    await pool.start()


if __name__ == "__main__":
    asyncio.run(main())
