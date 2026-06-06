#!/usr/bin/env python3
"""
MEOK AI Labs - Health Monitor
Comprehensive health checking for all services
"""

import sys
import asyncio
import argparse
from typing import Dict, List, Any
from dataclasses import dataclass
import httpx
import asyncpg
import redis.asyncio as redis


@dataclass
class HealthStatus:
    service: str
    healthy: bool
    latency_ms: float
    details: Dict[str, Any] = None


class HealthMonitor:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip("/")
        self.results: List[HealthStatus] = []

    async def check_api(self) -> HealthStatus:
        """Check API health endpoint"""
        start = asyncio.get_event_loop().time()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.api_url}/health")
                latency = (asyncio.get_event_loop().time() - start) * 1000

                return HealthStatus(
                    service="api",
                    healthy=resp.status_code == 200,
                    latency_ms=latency,
                    details=resp.json()
                    if resp.status_code == 200
                    else {"error": "Health check failed"},
                )
        except Exception as e:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return HealthStatus(
                service="api",
                healthy=False,
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def check_database(self, dsn: str) -> HealthStatus:
        """Check PostgreSQL connection"""
        start = asyncio.get_event_loop().time()
        try:
            conn = await asyncpg.connect(dsn, timeout=5)
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            latency = (asyncio.get_event_loop().time() - start) * 1000

            return HealthStatus(
                service="database",
                healthy=result == 1,
                latency_ms=latency,
                details={"status": "connected"},
            )
        except Exception as e:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return HealthStatus(
                service="database",
                healthy=False,
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def check_redis(self, url: str) -> HealthStatus:
        """Check Redis connection"""
        start = asyncio.get_event_loop().time()
        try:
            r = redis.from_url(url)
            await r.ping()
            latency = (asyncio.get_event_loop().time() - start) * 1000

            return HealthStatus(
                service="redis",
                healthy=True,
                latency_ms=latency,
                details={"status": "connected"},
            )
        except Exception as e:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return HealthStatus(
                service="redis",
                healthy=False,
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def check_rate_limit(self) -> HealthStatus:
        """Check rate limit endpoint"""
        start = asyncio.get_event_loop().time()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.api_url}/auth/rate-limit")
                latency = (asyncio.get_event_loop().time() - start) * 1000

                data = resp.json()
                return HealthStatus(
                    service="rate-limit",
                    healthy=True,
                    latency_ms=latency,
                    details={
                        "remaining": data.get("remaining"),
                        "limit": data.get("limit"),
                        "reset": data.get("reset"),
                    },
                )
        except Exception as e:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return HealthStatus(
                service="rate-limit",
                healthy=False,
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def check_memory_service(self) -> HealthStatus:
        """Check memory service"""
        start = asyncio.get_event_loop().time()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{self.api_url}/memory",
                    json={"content": "health check", "type": "semantic"},
                )
                latency = (asyncio.get_event_loop().time() - start) * 1000

                return HealthStatus(
                    service="memory",
                    healthy=resp.status_code in [200, 201],
                    latency_ms=latency,
                    details={"status_code": resp.status_code},
                )
        except Exception as e:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return HealthStatus(
                service="memory",
                healthy=False,
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def check_governance(self) -> HealthStatus:
        """Check governance engine"""
        start = asyncio.get_event_loop().time()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{self.api_url}/governance/analyze",
                    json={"content": "hello world", "framework": "constitutional"},
                )
                latency = (asyncio.get_event_loop().time() - start) * 1000

                return HealthStatus(
                    service="governance",
                    healthy=resp.status_code == 200,
                    latency_ms=latency,
                    details={
                        "status_code": resp.status_code,
                        "score": resp.json().get("score"),
                    },
                )
        except Exception as e:
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return HealthStatus(
                service="governance",
                healthy=False,
                latency_ms=latency,
                details={"error": str(e)},
            )

    async def run_all_checks(self) -> List[HealthStatus]:
        """Run all health checks"""
        checks = [
            self.check_api(),
            self.check_rate_limit(),
            self.check_memory_service(),
            self.check_governance(),
        ]

        results = await asyncio.gather(*checks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                self.results.append(
                    HealthStatus(
                        service="unknown",
                        healthy=False,
                        latency_ms=0,
                        details={"error": str(result)},
                    )
                )
            else:
                self.results.append(result)

        return self.results

    def print_report(self):
        """Print health check report"""
        print("\n" + "=" * 60)
        print("MEOK AI Labs - Health Report")
        print("=" * 60)

        all_healthy = True
        for status in self.results:
            icon = "✓" if status.healthy else "✗"
            color = "\033[92m" if status.healthy else "\033[91m"
            reset = "\033[0m"

            print(f"{color}{icon}{reset} {status.service.upper():15} ", end="")
            print(f"Latency: {status.latency_ms:>8.2f}ms  ", end="")

            if not status.healthy:
                all_healthy = False
                if status.details and "error" in status.details:
                    print(f"  Error: {status.details['error'][:40]}")
                else:
                    print()
            else:
                print()

        print("-" * 60)
        if all_healthy:
            print("\033[92m✓ All services healthy\033[0m\n")
            return 0
        else:
            print("\033[91m✗ Some services unhealthy\033[0m\n")
            return 1


async def main():
    parser = argparse.ArgumentParser(description="MEOK AI Health Monitor")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    args = parser.parse_args()

    monitor = HealthMonitor(api_url=args.api_url)
    await monitor.run_all_checks()
    return monitor.print_report()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
