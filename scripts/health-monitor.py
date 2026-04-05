#!/usr/bin/env python3
"""
MEOK AI Labs - Health Monitor
Uptime monitoring and alerting for production services
"""

import asyncio
import time
import smtplib
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List
from enum import Enum
import argparse
import sys

try:
    import aiohttp
    import redis
except ImportError:
    print("Installing dependencies...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "redis"])
    import aiohttp
    import redis


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    service: str
    url: str
    status: ServiceStatus
    latency_ms: float
    timestamp: datetime
    error: Optional[str] = None


@dataclass
class Alert:
    service: str
    severity: str  # critical, warning, info
    message: str
    timestamp: datetime


class HealthMonitor:
    """Monitors MEOK AI Labs services"""

    def __init__(
        self,
        services: dict = None,
        redis_url: str = "redis://localhost:6379",
        webhook_url: str = None,
        email_config: dict = None,
    ):
        self.services = services or {
            "meok-os": "http://localhost:3000/health",
            "sov3": "http://localhost:3101/health",
            "postgres": "http://localhost:5432",  # Will use pg_isready
            "redis": "redis://localhost:6379",
        }
        self.redis_url = redis_url
        self.webhook_url = webhook_url
        self.email_config = email_config
        self.alerts: List[Alert] = []
        self.last_check_time = {}
        self.alert_cooldown = {}  # Prevent alert spam

    async def check_service(
        self, session: aiohttp.ClientSession, name: str, url: str
    ) -> HealthCheck:
        """Check a single service"""
        start = time.time()

        try:
            if url.startswith("redis://"):
                # Redis check
                r = redis.from_url(url)
                r.ping()
                latency = (time.time() - start) * 1000
                return HealthCheck(
                    name, url, ServiceStatus.HEALTHY, latency, datetime.now()
                )

            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                latency = (time.time() - start) * 1000

                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status") == "ok":
                        return HealthCheck(
                            name, url, ServiceStatus.HEALTHY, latency, datetime.now()
                        )
                    else:
                        return HealthCheck(
                            name, url, ServiceStatus.DEGRADED, latency, datetime.now()
                        )
                else:
                    return HealthCheck(
                        name,
                        url,
                        ServiceStatus.DOWN,
                        latency,
                        datetime.now(),
                        f"HTTP {resp.status}",
                    )

        except asyncio.TimeoutError:
            latency = (time.time() - start) * 1000
            return HealthCheck(
                name, url, ServiceStatus.DOWN, latency, datetime.now(), "Timeout"
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return HealthCheck(
                name, url, ServiceStatus.DOWN, latency, datetime.now(), str(e)
            )

    async def check_all(self) -> List[HealthCheck]:
        """Check all services"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.check_service(session, name, url)
                for name, url in self.services.items()
            ]
            return await asyncio.gather(*tasks)

    def should_alert(self, service: str, severity: str) -> bool:
        """Check if we should send alert (cooldown)"""
        key = f"{service}:{severity}"
        now = datetime.now()

        cooldown_seconds = {
            "critical": 300,  # 5 min
            "warning": 900,  # 15 min
            "info": 3600,  # 1 hour
        }

        if key in self.alert_cooldown:
            last_alert = self.alert_cooldown[key]
            if now - last_alert < timedelta(
                seconds=cooldown_seconds.get(severity, 300)
            ):
                return False

        self.alert_cooldown[key] = now
        return True

    async def send_alert(self, alert: Alert):
        """Send alert via configured channels"""
        if not self.should_alert(alert.service, alert.severity):
            return

        print(f"🚨 ALERT [{alert.severity.upper()}] {alert.service}: {alert.message}")

        # Discord/Slack webhook
        if self.webhook_url:
            await self._send_webhook(alert)

        # Email
        if self.email_config:
            self._send_email(alert)

        self.alerts.append(alert)

    async def _send_webhook(self, alert: Alert):
        """Send to Discord/Slack"""
        color = {
            "critical": 15158332,  # Red
            "warning": 15105570,  # Orange
            "info": 3447003,  # Blue
        }

        payload = {
            "embeds": [
                {
                    "title": f"🚨 {alert.service} - {alert.severity.upper()}",
                    "description": alert.message,
                    "color": color.get(alert.severity, 3447003),
                    "timestamp": alert.timestamp.isoformat(),
                    "footer": {"text": "MEOK AI Labs Health Monitor"},
                }
            ]
        }

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f"Failed to send webhook: {e}")

    def _send_email(self, alert: Alert):
        """Send email alert"""
        if not self.email_config:
            return

        try:
            server = smtplib.SMTP(
                self.email_config["smtp_host"], self.email_config["smtp_port"]
            )
            server.starttls()
            server.login(self.email_config["username"], self.email_config["password"])

            msg = f"Subject: [{alert.severity.upper()}] MEOK AI - {alert.service}\n\n{alert.message}"
            server.sendmail(self.email_config["from"], self.email_config["to"], msg)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")

    def store_status(self, checks: List[HealthCheck]):
        """Store status in Redis for dashboard"""
        try:
            r = redis.from_url(self.redis_url)
            for check in checks:
                key = f"health:{check.service}"
                r.hset(
                    key,
                    mapping={
                        "status": check.status.value,
                        "latency_ms": check.latency_ms,
                        "timestamp": check.timestamp.isoformat(),
                        "error": check.error or "",
                    },
                )
                r.expire(key, 3600)  # 1 hour TTL
        except Exception as e:
            print(f"Failed to store status: {e}")

    async def run_continuous(self, interval: int = 60):
        """Run continuous monitoring"""
        print(f"🔍 Starting MEOK AI Labs Health Monitor (interval: {interval}s)")
        print("=" * 60)

        while True:
            try:
                checks = await self.check_all()

                # Store in Redis
                self.store_status(checks)

                # Check for alerts
                for check in checks:
                    if check.status == ServiceStatus.DOWN:
                        await self.send_alert(
                            Alert(
                                check.service,
                                "critical",
                                f"Service DOWN - {check.error or 'Unknown error'} - Latency: {check.latency_ms:.0f}ms",
                                check.timestamp,
                            )
                        )
                    elif check.status == ServiceStatus.DEGRADED:
                        await self.send_alert(
                            Alert(
                                check.service,
                                "warning",
                                f"Service DEGRADED - Latency: {check.latency_ms:.0f}ms",
                                check.timestamp,
                            )
                        )

                # Print status
                print(f"\n{datetime.now().strftime('%H:%M:%S')}")
                for check in checks:
                    icon = (
                        "✅"
                        if check.status == ServiceStatus.HEALTHY
                        else "⚠️"
                        if check.status == ServiceStatus.DEGRADED
                        else "❌"
                    )
                    print(
                        f"  {icon} {check.service}: {check.status.value} ({check.latency_ms:.0f}ms)"
                    )

            except Exception as e:
                print(f"Monitor error: {e}")

            await asyncio.sleep(interval)

    def print_report(self, checks: List[HealthCheck]):
        """Print health report"""
        print("\n" + "=" * 60)
        print("MEOK AI LABS - HEALTH REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        overall = ServiceStatus.HEALTHY
        for check in checks:
            if check.status == ServiceStatus.DOWN:
                overall = ServiceStatus.DOWN
                break
            elif check.status == ServiceStatus.DEGRADED:
                overall = ServiceStatus.DEGRADED

        print(f"Overall Status: {overall.value.upper()}\n")

        for check in checks:
            icon = (
                "✅"
                if check.status == ServiceStatus.HEALTHY
                else "⚠️"
                if check.status == ServiceStatus.DEGRADED
                else "❌"
            )
            print(f"  {icon} {check.service}")
            print(f"     URL: {check.url}")
            print(f"     Status: {check.status.value}")
            print(f"     Latency: {check.latency_ms:.0f}ms")
            if check.error:
                print(f"     Error: {check.error}")
            print()


async def main():
    parser = argparse.ArgumentParser(description="MEOK AI Labs Health Monitor")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument(
        "--interval", type=int, default=60, help="Check interval in seconds"
    )
    parser.add_argument("--webhook", help="Discord/Slack webhook URL")
    parser.add_argument("--smtp-host", help="SMTP host for email alerts")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port")
    parser.add_argument("--smtp-user", help="SMTP username")
    parser.add_argument("--smtp-pass", help="SMTP password")
    parser.add_argument("--email-to", help="Email recipient")

    args = parser.parse_args()

    email_config = None
    if args.smtp_host:
        email_config = {
            "smtp_host": args.smtp_host,
            "smtp_port": args.smtp_port,
            "username": args.smtp_user,
            "password": args.smtp_pass,
            "from": args.smtp_user,
            "to": args.email_to,
        }

    monitor = HealthMonitor(webhook_url=args.webhook, email_config=email_config)

    if args.once:
        checks = await monitor.check_all()
        monitor.print_report(checks)
    else:
        await monitor.run_continuous(interval=args.interval)


if __name__ == "__main__":
    asyncio.run(main())
