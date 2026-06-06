#!/usr/bin/env python3
"""
MEOK AI Labs - Worker CLI
Manage workers and tasks
"""

import asyncio
import argparse
import sys
from typing import Optional

from task_worker import WorkerPool, TaskQueue
from monitoring import MonitoringService
from notification import NotificationService, NotificationType, NotificationPriority


async def run_workers(num_workers: int = 4):
    """Run worker pool"""
    pool = WorkerPool(num_workers=num_workers)

    print(f"Starting {num_workers} workers...")

    await pool.start()


async def run_monitoring():
    """Run monitoring service"""
    service = MonitoringService()

    print("Starting monitoring service...")

    await service.start_collection()


async def submit_task(
    task_type: str,
    payload: dict,
    priority: str = "normal",
):
    """Submit a task to the queue"""
    queue = TaskQueue()

    task_id = await queue.enqueue(task_type, payload, priority)

    print(f"Task submitted: {task_id}")

    return task_id


async def send_notification(
    subject: str,
    message: str,
    channel: str = "slack",
    priority: str = "medium",
):
    """Send a notification"""
    service = NotificationService()

    notif_type = NotificationType(channel)
    notif_priority = NotificationPriority(priority)

    result = await service.send_alert(
        subject=subject,
        message=message,
        priority=notif_priority,
        channels=[notif_type],
    )

    print(f"Notification sent: {result}")


def main():
    parser = argparse.ArgumentParser(description="MEOK AI Labs Worker CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    worker_parser = subparsers.add_parser("worker", help="Run worker pool")
    worker_parser.add_argument(
        "--workers", "-w", type=int, default=4, help="Number of workers"
    )

    monitor_parser = subparsers.add_parser("monitor", help="Run monitoring service")

    submit_parser = subparsers.add_parser("submit", help="Submit a task")
    submit_parser.add_argument("type", help="Task type")
    submit_parser.add_argument("payload", help="Task payload (JSON)")
    submit_parser.add_argument(
        "--priority",
        "-p",
        default="normal",
        choices=["low", "normal", "high"],
        help="Task priority",
    )

    notify_parser = subparsers.add_parser("notify", help="Send notification")
    notify_parser.add_argument("subject", help="Notification subject")
    notify_parser.add_argument("message", help="Notification message")
    notify_parser.add_argument(
        "--channel",
        "-c",
        default="slack",
        choices=["email", "slack", "webhook"],
        help="Notification channel",
    )
    notify_parser.add_argument(
        "--priority",
        "-p",
        default="medium",
        choices=["low", "medium", "high", "critical"],
        help="Priority",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "worker":
        asyncio.run(run_workers(args.workers))

    elif args.command == "monitor":
        asyncio.run(run_monitoring())

    elif args.command == "submit":
        import json

        payload = json.loads(args.payload)
        asyncio.run(submit_task(args.type, payload, args.priority))

    elif args.command == "notify":
        asyncio.run(
            send_notification(
                args.subject,
                args.message,
                args.channel,
                args.priority,
            )
        )


if __name__ == "__main__":
    main()
