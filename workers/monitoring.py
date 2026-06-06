#!/usr/bin/env python3
"""
MEOK AI Labs - Monitoring Service
Metrics collection and alerting
"""

import asyncio
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alert:
    name: str
    severity: str
    message: str
    timestamp: datetime
    fired: bool = False


class MetricsCollector:
    """Collect and store metrics"""

    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.alerts: Dict[str, Alert] = {}

    def record(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Record a metric"""
        metric = Metric(
            name=name,
            value=value,
            labels=labels or {},
        )
        self.metrics[name].append(metric)

        self._check_alerts(name, value)

    def _check_alerts(self, metric_name: str, value: float) -> None:
        """Check if any alerts should fire"""
        alert_key = f"{metric_name}_alert"

        if alert_key not in self.alerts:
            return

        alert = self.alerts[alert_key]

        if not alert.fired:
            condition_met = self._evaluate_condition(metric_name, value, alert)
            if condition_met:
                alert.fired = True
                logger.warning(f"ALERT: {alert.name} - {alert.message}")

    def _evaluate_condition(self, metric_name: str, value: float, alert: Alert) -> bool:
        """Evaluate alert condition"""
        if "high_error_rate" in alert.name:
            return value > 0.05
        if "high_latency" in alert.name:
            return value > 2000
        if "violation_spike" in alert.name:
            return value > 10
        return False

    def define_alert(
        self,
        name: str,
        severity: str,
        message: str,
    ) -> None:
        """Define an alert"""
        self.alerts[name] = Alert(
            name=name,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
        )

    def get_metrics(
        self,
        name: str,
        duration: timedelta = timedelta(minutes=5),
    ) -> List[Metric]:
        """Get metrics for a time window"""
        cutoff = datetime.utcnow() - duration
        return [m for m in self.metrics[name] if m.timestamp >= cutoff]

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = {}

        for name, metrics in self.metrics.items():
            if not metrics:
                continue

            values = [m.value for m in metrics[-100:]]
            summary[name] = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "last": values[-1],
            }

        return summary

    def get_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []

        for name, metrics in self.metrics.items():
            if not metrics:
                continue

            latest = metrics[-1]
            label_str = ",".join(f'{k}="{v}"' for k, v in latest.labels.items())

            if label_str:
                lines.append(f"{name}{{{label_str}}} {latest.value}")
            else:
                lines.append(f"{name} {latest.value}")

        return "\n".join(lines)


class RequestTracker:
    """Track request metrics"""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.latencies: Dict[str, List[float]] = defaultdict(list)

    def record_request(
        self, endpoint: str, latency_ms: float, error: bool = False
    ) -> None:
        """Record a request"""
        self.request_counts[endpoint] += 1
        self.collector.record("meokai_requests_total", 1, {"endpoint": endpoint})

        if error:
            self.error_counts[endpoint] += 1
            self.collector.record("meokai_errors_total", 1, {"endpoint": endpoint})

        self.latencies[endpoint].append(latency_ms)
        self.collector.record(
            "meokai_request_duration_seconds", latency_ms / 1000, {"endpoint": endpoint}
        )

    def get_stats(self, endpoint: str) -> Dict[str, Any]:
        """Get stats for an endpoint"""
        latencies = self.latencies.get(endpoint, [])

        if not latencies:
            return {"requests": 0, "errors": 0}

        sorted_latencies = sorted(latencies)

        return {
            "requests": self.request_counts[endpoint],
            "errors": self.error_counts[endpoint],
            "error_rate": self.error_counts[endpoint]
            / max(self.request_counts[endpoint], 1),
            "latency_avg": sum(latencies) / len(latencies),
            "latency_p50": sorted_latencies[len(sorted_latencies) // 2],
            "latency_p95": sorted_latencies[int(len(sorted_latencies) * 0.95)],
            "latency_p99": sorted_latencies[int(len(sorted_latencies) * 0.99)],
        }


class ViolationTracker:
    """Track governance violations"""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.violations: Dict[str, int] = defaultdict(int)

    def record_violation(self, violation_type: str, severity: str) -> None:
        """Record a violation"""
        self.violations[violation_type] += 1

        self.collector.record(
            "meokai_violations_total", 1, {"type": violation_type, "severity": severity}
        )

    def get_top_violations(self, limit: int = 10) -> List[tuple]:
        """Get most common violations"""
        return sorted(self.violations.items(), key=lambda x: x[1], reverse=True)[:limit]


class MonitoringService:
    """Main monitoring service"""

    def __init__(self):
        self.collector = MetricsCollector()
        self.request_tracker = RequestTracker(self.collector)
        self.violation_tracker = ViolationTracker(self.collector)

        self._setup_alerts()

    def _setup_alerts(self) -> None:
        """Set up default alerts"""
        self.collector.define_alert(
            "high_error_rate", "critical", "Error rate exceeds 5%"
        )

        self.collector.define_alert(
            "high_latency", "warning", "p99 latency exceeds 2 seconds"
        )

        self.collector.define_alert(
            "violation_spike", "warning", "Violation rate unusually high"
        )

    async def start_collection(self) -> None:
        """Start background metrics collection"""
        logger.info("Starting metrics collection")

        while True:
            summary = self.collector.get_summary()

            logger.debug(f"Metrics summary: {summary}")

            await asyncio.sleep(60)

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        summary = self.collector.get_summary()

        error_rate = 0
        if "meokai_requests_total" in summary and "meokai_errors_total" in summary:
            error_rate = summary["meokai_errors_total"]["last"] / max(
                summary["meokai_requests_total"]["last"], 1
            )

        latency_p99 = 0
        if "meokai_request_duration_seconds" in summary:
            latency_p99 = summary["meokai_request_duration_seconds"]["max"] * 1000

        healthy = error_rate < 0.05 and latency_p99 < 2000

        return {
            "healthy": healthy,
            "error_rate": error_rate,
            "latency_p99_ms": latency_p99,
            "alerts_fired": sum(1 for a in self.collector.alerts.values() if a.fired),
        }


async def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)

    service = MonitoringService()

    await service.start_collection()


if __name__ == "__main__":
    asyncio.run(main())
