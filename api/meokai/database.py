"""
MEOK AI Labs - Database
"""

import asyncpg
from typing import Optional

_pool: Optional[asyncpg.Pool] = None


async def init_db(database_url: Optional[str] = None):
    """Initialize database connection pool"""
    global _pool

    url = database_url or "postgresql://meok:password@localhost:5432/meokai"

    _pool = await asyncpg.create_pool(
        url,
        min_size=5,
        max_size=20,
    )

    return _pool


async def get_db() -> asyncpg.Pool:
    """Get database connection pool"""
    global _pool

    if _pool is None:
        await init_db()

    return _pool


async def close_db():
    """Close database connection pool"""
    global _pool

    if _pool:
        await _pool.close()
        _pool = None
