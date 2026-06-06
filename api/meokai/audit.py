#!/usr/bin/env python3
"""
MEOK AI Labs - Audit System
Comprehensive audit logging with persistence, compliance, and real-time streaming
"""

import json
import uuid
import asyncio
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncIterator
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import hashlib
import asyncpg
from pathlib import Path


class AuditEventType(str, Enum):
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    API_REQUEST = "api.request"
    DATA_ACCESS = "data.access"
    DATA_MODIFY = "data.modify"
    DATA_DELETE = "data.delete"
    POLICY_VIOLATION = "policy.violation"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"
    AUTH_FAILURE = "auth.failure"
    PERMISSION_DENIED = "permission.denied"
    AGENT_TASK = "agent.task"
    MEMORY_STORE = "memory.store"
    MEMORY_QUERY = "memory.query"
    GOVERNANCE_ANALYSIS = "governance.analysis"
    CONSCIOUSNESS_EVENT = "consciousness.event"
    SYSTEM_CONFIG_CHANGE = "system.config_change"
    ADMIN_ACTION = "admin.action"
    DATA_BREACH = "data.breach"
    GDPR_REQUEST = "gdpr.request"


class Severity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class GDPRRequestType(str, Enum):
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICTION = "restriction"
    PORTABILITY = "portability"
    OBJECTION = "objection"


@dataclass
class AuditEvent:
    id: str
    timestamp: datetime
    event_type: AuditEventType
    user_id: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    severity: Severity
    success: bool
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    duration_ms: Optional[float] = None
    checksum: Optional[str] = None


@dataclass
class BreachAlert:
    type: str
    severity: Severity
    users_affected: List[str]
    timestamp: datetime
    description: str
    recommended_action: str


class AuditLogger:
    """Production audit logging with database persistence"""

    def __init__(self, database_url: str = None, storage_path: str = "./audit_logs"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.db_url = database_url or "postgresql://meok:password@localhost:5432/meokai"
        self.events: List[AuditEvent] = []
        self.event_counts: Dict[str, int] = defaultdict(int)
        self._subscribers: List[asyncio.Queue] = []
        self._breach_detector = BreachDetector(self)
        self._pool: Optional[asyncpg.Pool] = None

    async def init_db(self):
        """Initialize database connection"""
        try:
            self._pool = await asyncpg.connect(self.db_url)
            await self._pool.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id UUID PRIMARY KEY,
                    timestamp TIMESTAMPTZ NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    user_id VARCHAR(255),
                    resource_type VARCHAR(100),
                    resource_id VARCHAR(255),
                    action TEXT NOT NULL,
                    details JSONB,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    severity VARCHAR(20) NOT NULL,
                    success BOOLEAN NOT NULL,
                    request_id VARCHAR(255),
                    session_id VARCHAR(255),
                    duration_ms FLOAT,
                    checksum VARCHAR(64)
                )
            """)
            await self._pool.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON audit_events(timestamp DESC)
            """)
            await self._pool.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_user 
                ON audit_events(user_id, timestamp DESC)
            """)
        except Exception as e:
            print(f"Database init failed, using memory: {e}")

    async def close(self):
        """Close database connection"""
        if self._pool:
            await self._pool.close()

    def _generate_checksum(self, event: AuditEvent) -> str:
        content = f"{event.id}{event.timestamp}{event.event_type}{event.user_id}{event.action}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    async def log(
        self,
        event_type: AuditEventType,
        action: str,
        severity: Severity = Severity.INFO,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            success=success,
            request_id=request_id,
            session_id=session_id,
            duration_ms=duration_ms,
        )
        event.checksum = self._generate_checksum(event)

        self.events.append(event)
        self.event_counts[event_type.value] += 1

        if self._pool:
            await self._persist_event(event)

        await self._notify_subscribers(event)

        self._breach_detector.check(event)

        return event

    async def _persist_event(self, event: AuditEvent):
        """Persist event to database"""
        try:
            await self._pool.execute(
                """
                INSERT INTO audit_events 
                (id, timestamp, event_type, user_id, resource_type, resource_id, 
                 action, details, ip_address, user_agent, severity, success, 
                 request_id, session_id, duration_ms, checksum)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            """,
                event.id,
                event.timestamp,
                event.event_type.value,
                event.user_id,
                event.resource_type,
                event.resource_id,
                event.action,
                json.dumps(event.details),
                event.ip_address,
                event.user_agent,
                event.severity.value,
                event.success,
                event.request_id,
                event.session_id,
                event.duration_ms,
                event.checksum,
            )
        except Exception:
            pass

    async def _notify_subscribers(self, event: AuditEvent):
        """Notify real-time subscribers"""
        for queue in self._subscribers:
            await queue.put(asdict(event))

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to real-time audit events"""
        queue = asyncio.Queue(maxsize=1000)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from events"""
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def stream_events(
        self,
        event_types: List[AuditEventType] = None,
        user_id: str = None,
    ) -> AsyncIterator[AuditEvent]:
        """Stream events in real-time"""
        queue = self.subscribe()
        try:
            while True:
                event_dict = await queue.get()
                event = AuditEvent(**event_dict)
                if event_types and event.event_type not in event_types:
                    continue
                if user_id and event.user_id != user_id:
                    continue
                yield event
        finally:
            self.unsubscribe(queue)

    def log_api_request(self, **kwargs) -> AuditEvent:
        return asyncio.create_task(
            self.log(
                event_type=AuditEventType.API_REQUEST,
                action=f"{kwargs.get('method', 'GET')} {kwargs.get('endpoint', '/')}",
                severity=Severity.INFO
                if kwargs.get("status_code", 200) < 400
                else Severity.WARNING,
                success=200 <= kwargs.get("status_code", 200) < 400,
                details={
                    "endpoint": kwargs.get("endpoint"),
                    "method": kwargs.get("method"),
                    "status_code": kwargs.get("status_code"),
                },
                duration_ms=kwargs.get("duration_ms"),
                user_id=kwargs.get("user_id"),
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
            )
        )

    def log_gdpr_request(
        self,
        user_id: str,
        request_type: GDPRRequestType,
        details: Dict = None,
    ) -> AuditEvent:
        return asyncio.create_task(
            self.log(
                event_type=AuditEventType.GDPR_REQUEST,
                action=f"gdpr.{request_type.value}",
                user_id=user_id,
                severity=Severity.INFO,
                success=True,
                details={"request_type": request_type.value, **(details or {})},
            )
        )

    async def query(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[Severity] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        resource_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        if self._pool:
            return await self._query_db(
                user_id,
                event_type,
                severity,
                start_time,
                end_time,
                resource_type,
                limit,
            )

        results = []
        for event in reversed(self.events):
            if user_id and event.user_id != user_id:
                continue
            if event_type and event.event_type != event_type:
                continue
            if severity and event.severity != severity:
                continue
            if resource_type and event.resource_type != resource_type:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            results.append(asdict(event))
            if len(results) >= limit:
                break
        return results

    async def _query_db(self, **kwargs) -> List[Dict]:
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []
        param_idx = 1

        if kwargs.get("user_id"):
            query += f" AND user_id = ${param_idx}"
            params.append(kwargs["user_id"])
            param_idx += 1

        if kwargs.get("event_type"):
            query += f" AND event_type = ${param_idx}"
            params.append(kwargs["event_type"].value)
            param_idx += 1

        if kwargs.get("severity"):
            query += f" AND severity = ${param_idx}"
            params.append(kwargs["severity"].value)
            param_idx += 1

        if kwargs.get("start_time"):
            query += f" AND timestamp >= ${param_idx}"
            params.append(kwargs["start_time"])
            param_idx += 1

        if kwargs.get("end_time"):
            query += f" AND timestamp <= ${param_idx}"
            params.append(kwargs["end_time"])
            param_idx += 1

        query += " ORDER BY timestamp DESC"
        query += f" LIMIT ${param_idx}"
        params.append(kwargs.get("limit", 100))

        rows = await self._pool.fetch(query, *params)
        return [dict(row) for row in rows]

    def get_user_activity(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        start = datetime.utcnow() - timedelta(days=days)
        events = [
            e for e in self.events if e.user_id == user_id and e.timestamp >= start
        ]

        event_types = defaultdict(int)
        for e in events:
            event_types[e.event_type.value] += 1

        return {
            "user_id": user_id,
            "period_days": days,
            "total_events": len(events),
            "violations": sum(
                1 for e in events if e.event_type == AuditEventType.POLICY_VIOLATION
            ),
            "failed_auths": sum(
                1 for e in events if e.event_type == AuditEventType.AUTH_FAILURE
            ),
            "event_types": dict(event_types),
        }

    def get_compliance_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        events = [e for e in self.events if start_date <= e.timestamp <= end_date]

        violations = [
            e for e in events if e.event_type == AuditEventType.POLICY_VIOLATION
        ]
        auth_failures = [
            e for e in events if e.event_type == AuditEventType.AUTH_FAILURE
        ]
        gdpr_requests = [
            e for e in events if e.event_type == AuditEventType.GDPR_REQUEST
        ]

        severity_counts = defaultdict(int)
        for e in events:
            severity_counts[e.severity.value] += 1

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_events": len(events),
            "unique_users": len(set(e.user_id for e in events if e.user_id)),
            "violations": {
                "total": len(violations),
                "by_type": self._group_by(
                    violations, lambda e: e.details.get("violation_type")
                ),
            },
            "auth_failures": {
                "total": len(auth_failures),
                "unique_ips": len(
                    set(e.ip_address for e in auth_failures if e.ip_address)
                ),
            },
            "gdpr_requests": {
                "total": len(gdpr_requests),
                "by_type": self._group_by(
                    gdpr_requests, lambda e: e.details.get("request_type")
                ),
            },
            "severity_distribution": dict(severity_counts),
            "compliance_score": self._calculate_compliance_score(
                len(violations), len(events)
            ),
        }

    def _group_by(self, events: List[AuditEvent], key_fn) -> Dict[str, int]:
        counts = defaultdict(int)
        for e in events:
            key = key_fn(e) or "unknown"
            counts[key] += 1
        return dict(counts)

    def _calculate_compliance_score(self, violations: int, total: int) -> float:
        if total == 0:
            return 1.0
        return max(0.0, 1.0 - (violations / total) * 3)

    def export(self, format: str = "json", compress: bool = False) -> str:
        data = [asdict(e) for e in self.events]
        if format == "json":
            content = json.dumps(data, indent=2, default=str)
            if compress:
                return gzip.compress(content.encode()).hex()
            return content
        return str(data)

    def get_breach_alerts(self) -> List[BreachAlert]:
        return self._breach_detector.get_alerts()


class BreachDetector:
    """Detect potential data breaches from audit patterns"""

    def __init__(self, logger: AuditLogger):
        self.logger = logger
        self.alerts: List[BreachAlert] = []
        self.failed_auth_by_ip: Dict[str, List[datetime]] = defaultdict(list)
        self.violation_burst: Dict[str, List[datetime]] = defaultdict(list)

    def check(self, event: AuditEvent):
        now = datetime.utcnow()

        if event.event_type == AuditEventType.AUTH_FAILURE and event.ip_address:
            self.failed_auth_by_ip[event.ip_address].append(now)
            self._check_auth_brute_force(event.ip_address)

        if event.event_type == AuditEventType.POLICY_VIOLATION and event.user_id:
            self.violation_burst[event.user_id].append(now)
            self._check_violation_burst(event.user_id)

    def _check_auth_brute_force(self, ip: str):
        recent = [
            t
            for t in self.failed_auth_by_ip[ip]
            if datetime.utcnow() - t < timedelta(minutes=5)
        ]
        self.failed_auth_by_ip[ip] = recent

        if len(recent) >= 10:
            alert = BreachAlert(
                type="brute_force",
                severity=Severity.CRITICAL,
                users_affected=[],
                timestamp=datetime.utcnow(),
                description=f"10+ failed auth attempts from IP {ip} in 5 minutes",
                recommended_action="Block IP immediately, review logs",
            )
            self.alerts.append(alert)

    def _check_violation_burst(self, user_id: str):
        recent = [
            t
            for t in self.violation_burst[user_id]
            if datetime.utcnow() - t < timedelta(minutes=1)
        ]
        self.violation_burst[user_id] = recent

        if len(recent) >= 5:
            alert = BreachAlert(
                type="violation_burst",
                severity=Severity.WARNING,
                users_affected=[user_id],
                timestamp=datetime.utcnow(),
                description=f"5+ policy violations from user {user_id} in 1 minute",
                recommended_action="Temporarily suspend user, investigate",
            )
            self.alerts.append(alert)


async def main():
    logger = AuditLogger()
    await logger.init_db()

    await logger.log(
        event_type=AuditEventType.API_REQUEST,
        action="POST /governance/analyze",
        severity=Severity.INFO,
        user_id="user123",
        success=True,
        duration_ms=145.2,
    )

    await logger.log_gdpr_request(
        user_id="user456",
        request_type=GDPRRequestType.ACCESS,
    )

    print("=== Audit System Demo ===")
    print(f"Events logged: {len(logger.events)}")
    print(f"Breach alerts: {len(logger.get_breach_alerts())}")

    await logger.close()


if __name__ == "__main__":
    asyncio.run(main())
