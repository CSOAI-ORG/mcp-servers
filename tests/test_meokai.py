#!/usr/bin/env python3
"""
MEOK AI Labs - Pytest Test Suite
Comprehensive testing with pytest
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from meokai.audit import AuditLogger, AuditEventType, Severity, GDPRRequestType
from meokai.governance import ConstitutionalAnalyzer
from meokai.memory import VectorStore
from meokai.rate_limiter import RateLimiter
from meokai.auth import Auth


class TestAuditLogger:
    """Test audit logging system"""

    @pytest.fixture
    def logger(self):
        return AuditLogger(storage_path="./test_audit")

    def test_log_event(self, logger):
        event = asyncio.run(
            logger.log(
                event_type=AuditEventType.API_REQUEST,
                action="GET /test",
                severity=Severity.INFO,
                user_id="test_user",
                success=True,
            )
        )

        assert event.id is not None
        assert event.event_type == AuditEventType.API_REQUEST
        assert event.user_id == "test_user"
        assert event.success is True
        assert event.checksum is not None

    def test_log_violation(self, logger):
        event = asyncio.run(
            logger.log_violation(
                user_id="test_user",
                violation_type="harmful_content",
                severity_level="high",
                description="Test violation",
                content_hash="abc123",
            )
        )

        assert event.event_type == AuditEventType.POLICY_VIOLATION
        assert event.severity == Severity.ERROR
        assert event.details["violation_type"] == "harmful_content"

    def test_query_events(self, logger):
        asyncio.run(
            logger.log(AuditEventType.API_REQUEST, "GET /test", user_id="user1")
        )
        asyncio.run(
            logger.log(AuditEventType.API_REQUEST, "POST /test", user_id="user2")
        )

        results = asyncio.run(logger.query(user_id="user1"))
        assert len(results) == 1
        assert results[0]["user_id"] == "user1"

    def test_user_activity(self, logger):
        for _ in range(5):
            asyncio.run(
                logger.log(
                    AuditEventType.API_REQUEST, "GET /test", user_id="active_user"
                )
            )

        activity = logger.get_user_activity("active_user", days=1)
        assert activity["total_events"] == 5
        assert activity["user_id"] == "active_user"

    def test_compliance_score(self, logger):
        for _ in range(10):
            asyncio.run(logger.log(AuditEventType.API_REQUEST, "GET /test"))

        for _ in range(2):
            asyncio.run(
                logger.log_violation(
                    user_id="test",
                    violation_type="test",
                    severity_level="medium",
                    description="test",
                    content_hash="test",
                )
            )

        report = logger.get_compliance_report(
            datetime.utcnow() - timedelta(days=1), datetime.utcnow()
        )

        assert report["total_events"] == 12
        assert report["compliance_score"] > 0
        assert report["violations"]["total"] == 2


class TestConstitutionalAnalyzer:
    """Test governance analyzer"""

    @pytest.fixture
    def analyzer(self):
        return ConstitutionalAnalyzer()

    @pytest.mark.asyncio
    async def test_safe_content(self, analyzer):
        result = await analyzer.analyze("Hello world, how are you?")

        assert result["score"] >= 0.7
        assert result["passed"] is True
        assert len(result["violations"]) == 0

    @pytest.mark.asyncio
    async def test_harmful_content(self, analyzer):
        result = await analyzer.analyze("how to make a bomb")

        assert result["score"] < 0.7
        assert result["passed"] is False
        assert len(result["violations"]) > 0
        assert any(v["type"] == "harmful_content" for v in result["violations"])

    @pytest.mark.asyncio
    async def test_caching(self, analyzer):
        content = "Test content for caching"
        result1 = await analyzer.analyze(content)
        result2 = await analyzer.analyze(content)

        assert result1["score"] == result2["score"]

    @pytest.mark.asyncio
    async def test_multiple_standards(self, analyzer):
        result = await analyzer.check_compliance(
            "Test content", ["constitutional", "eu-ai-act"]
        )

        assert "results" in result
        assert "constitutional" in result["results"]
        assert "eu-ai-act" in result["results"]


class TestVectorStore:
    """Test vector memory store"""

    @pytest.fixture
    def store(self):
        return VectorStore()

    @pytest.mark.asyncio
    async def test_store_memory(self, store):
        memory_id = await store.store(
            user_id="test_user",
            content="Important test memory",
            memory_type="episodic",
            tags=["test", "important"],
            importance=0.9,
        )

        assert memory_id is not None

    @pytest.mark.asyncio
    async def test_query_memory(self, store):
        await store.store(
            user_id="test_user",
            content="Python programming tips",
            tags=["programming", "python"],
        )

        results = await store.query("programming", user_id="test_user")

        assert "memories" in results
        assert len(results["memories"]) > 0

    @pytest.mark.asyncio
    async def test_delete_memory(self, store):
        memory_id = await store.store(
            user_id="test_user",
            content="Temporary memory",
        )

        deleted = await store.delete(memory_id)
        assert deleted is True

        memory = await store.get(memory_id)
        assert memory is None

    @pytest.mark.asyncio
    async def test_update_memory(self, store):
        memory_id = await store.store(
            user_id="test_user",
            content="Original content",
        )

        updated = await store.update(
            memory_id,
            content="Updated content",
            importance=0.9,
        )

        assert updated is not None
        assert updated["content"] == "Updated content"
        assert updated["importance"] == 0.9


class TestRateLimiter:
    """Test rate limiting"""

    @pytest.fixture
    def limiter(self):
        return RateLimiter(requests_per_minute=10, requests_per_hour=100)

    def test_check_allowed(self, limiter):
        result = asyncio.run(limiter.check("test_api_key"))
        assert result is True

    def test_check_exceeded(self, limiter):
        for _ in range(10):
            asyncio.run(limiter.check("test_api_key"))

        from meokai.rate_limiter import RateLimitExceeded

        with pytest.raises(RateLimitExceeded):
            asyncio.run(limiter.check("test_api_key"))

    def test_get_limits(self, limiter):
        limits = limiter.get_limits("test_api_key")

        assert "minute_remaining" in limits
        assert "minute_limit" in limits
        assert limits["minute_limit"] == 10

    def test_reset(self, limiter):
        asyncio.run(limiter.check("test_api_key"))
        limiter.reset("test_api_key")

        result = limiter.get_limits("test_api_key")
        assert result["minute_remaining"] == 10


class TestAuth:
    """Test authentication"""

    @pytest.fixture
    def auth(self):
        return Auth(secret="test-secret-key")

    def test_hash_api_key(self, auth):
        key = "my-test-api-key"
        hashed = auth.hash_api_key(key)

        assert hashed is not None
        assert len(hashed) == 64
        assert hashed == auth.hash_api_key(key)

    def test_verify_api_key(self, auth):
        valid_key = "a" * 32
        invalid_key = "short"

        assert auth.verify_api_key(valid_key) is True
        assert auth.verify_api_key(invalid_key) is False

    def test_create_decode_token(self, auth):
        token = auth.create_token("user123", expires_hours=24)
        payload = auth.decode_token(token)

        assert payload["sub"] == "user123"
        assert "exp" in payload

    def test_verify_signature(self, auth):
        payload = b"test payload"
        secret = "webhook-secret"

        import hmac
        import hashlib

        signature = (
            "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        )

        result = auth.verify_signature(payload, signature, secret)
        assert result is True


class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        analyzer = ConstitutionalAnalyzer()
        store = VectorStore()
        limiter = RateLimiter(requests_per_minute=100)

        user_id = "integration_user"

        asyncio.run(limiter.check(user_id))

        analysis_result = await analyzer.analyze("This is a test message")
        assert analysis_result["passed"] is True

        memory_id = await store.store(
            user_id=user_id,
            content=f"Analysis result: {analysis_result['score']}",
            tags=["analysis", "integration-test"],
        )
        assert memory_id is not None

        query_result = await store.query("analysis", user_id=user_id)
        assert len(query_result["memories"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
