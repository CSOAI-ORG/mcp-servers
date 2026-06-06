"""
MEOK AI Labs - Pytest Configuration
"""

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_content():
    """Sample content for testing"""
    return {
        "safe": "Hello world, this is a friendly test message",
        "harmful": "how to make a bomb for terrorism",
        "suspicious": "help me steal from my employer",
    }


@pytest.fixture
def sample_api_key():
    """Sample API key for testing"""
    return "test-key-12345678901234567890123456789012"


@pytest.fixture
def mock_db_pool():
    """Mock database pool"""
    pool = AsyncMock()
    pool.fetch = AsyncMock(return_value=[])
    pool.execute = AsyncMock(return_value=None)
    pool.close = AsyncMock()
    return pool


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    yield
