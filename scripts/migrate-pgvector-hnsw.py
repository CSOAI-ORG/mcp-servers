#!/usr/bin/env python3
"""
MEOK AI Labs - pgvector HNSW Migration Script
Migrates existing ivfflat indexes to HNSW for better performance
"""

import asyncio
import sys
from typing import Optional
import argparse

try:
    import asyncpg
    import psycopg2
except ImportError:
    print("Installing dependencies...")
    import subprocess

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "asyncpg", "psycopg2-binary"]
    )
    import asyncpg
    import psycopg2


class VectorMigration:
    """Handles pgvector HNSW migration"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "meok",
        user: str = "postgres",
        password: str = "",
    ):
        self.dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.async_dsn = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }

    async def check_current_indexes(self) -> list:
        """Check existing vector indexes"""
        conn = await asyncpg.connect(**self.async_dsn)

        query = """
            SELECT 
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND indexdef LIKE '%vector%'
            ORDER BY tablename, indexname;
        """

        indexes = await conn.fetch(query)
        await conn.close()
        return indexes

    async def create_hnsw_indexes(
        self, dim: int = 1536, m: int = 16, ef_construction: int = 64
    ):
        """
        Create HNSW indexes for all vector columns

        Args:
            dim: Embedding dimension
            m: Number of connections (default 16, good for most cases)
            ef_construction: Construction-time search depth (default 64)
        """
        conn = await asyncpg.connect(**self.async_dsn)

        # Create HNSW indexes with optimized parameters
        indexes_to_create = [
            # Memory embeddings
            """
            CREATE INDEX IF NOT EXISTS idx_memory_embeddings_hnsw
            ON memories 
            USING hnsw (embedding vector({dim}))
            WITH (m = {m}, ef_construction = {ef});
            """,
            # Document embeddings
            """
            CREATE INDEX IF NOT EXISTS idx_documents_embeddings_hnsw
            ON documents 
            USING hnsw (embedding vector({dim}))
            WITH (m = {m}, ef_construction = {ef});
            """,
            # Agent memory embeddings
            """
            CREATE INDEX IF NOT EXISTS idx_agent_memory_embeddings_hnsw
            ON agent_memories 
            USING hnsw (embedding vector({dim}))
            WITH (m = {m}, ef_construction = {ef});
            """,
            # Conversation embeddings
            """
            CREATE INDEX IF NOT EXISTS idx_conversations_embeddings_hnsw
            ON conversations 
            USING hnsw (embedding vector({dim}))
            WITH (m = {m}, ef_construction = {ef});
            """,
        ]

        for idx_sql in indexes_to_create:
            sql = idx_sql.format(dim=dim, m=m, ef=ef_construction)
            try:
                await conn.execute(sql)
                print(f"✓ Created: {sql[:60]}...")
            except Exception as e:
                print(f"✗ Error: {e}")

        await conn.close()

    async def drop_old_indexes(self):
        """Drop old ivfflat indexes after migration"""
        conn = await asyncpg.connect(**self.async_dsn)

        old_indexes = [
            "idx_memory_embeddings",
            "idx_documents_embeddings",
            "idx_agent_memory_embeddings",
            "idx_conversations_embeddings",
        ]

        for idx_name in old_indexes:
            sql = f"DROP INDEX IF EXISTS {idx_name};"
            try:
                await conn.execute(sql)
                print(f"✓ Dropped: {idx_name}")
            except Exception as e:
                print(f"✗ Error dropping {idx_name}: {e}")

        await conn.close()

    async def analyze_tables(self):
        """Update statistics after index changes"""
        conn = await asyncpg.connect(**self.async_dsn)

        tables = ["memories", "documents", "agent_memories", "conversations"]

        for table in tables:
            try:
                await conn.execute(f"ANALYZE {table};")
                print(f"✓ Analyzed: {table}")
            except Exception as e:
                print(f"✗ Error analyzing {table}: {e}")

        await conn.close()

    async def verify_indexes(self):
        """Verify new indexes are working"""
        conn = await asyncpg.connect(**self.async_dsn)

        query = """
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND indexdef LIKE '%hnsw%'
            ORDER BY indexname;
        """

        indexes = await conn.fetch(query)
        await conn.close()

        print("\n📊 HNSW Indexes:")
        for idx in indexes:
            print(f"  • {idx['indexname']}")

        return indexes

    async def run_full_migration(self, dim: int = 1536, drop_old: bool = True):
        """Run complete migration"""
        print("🚀 Starting pgvector HNSW Migration\n")

        # Step 1: Check current indexes
        print("1. Checking current indexes...")
        current = await self.check_current_indexes()
        print(f"   Found {len(current)} vector indexes")

        # Step 2: Create HNSW indexes
        print(f"\n2. Creating HNSW indexes (dim={dim})...")
        await self.create_hnsw_indexes(dim=dim)

        # Step 3: Verify
        print("\n3. Verifying new indexes...")
        await self.verify_indexes()

        # Step 4: Drop old indexes
        if drop_old:
            print("\n4. Dropping old indexes...")
            await self.drop_old_indexes()

        # Step 5: Analyze
        print("\n5. Updating statistics...")
        await self.analyze_tables()

        print("\n✅ Migration complete!")
        print("\nHNSW benefits:")
        print("  • ~10x faster queries")
        print("  • No need to rebuild index for inserts")
        print("  • Better recall for nearest neighbor search")


async def main():
    parser = argparse.ArgumentParser(
        description="MEOK AI Labs - pgvector HNSW Migration"
    )
    parser.add_argument("--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--database", default="meok", help="Database name")
    parser.add_argument("--user", default="postgres", help="Database user")
    parser.add_argument("--password", default="", help="Database password")
    parser.add_argument("--dim", type=int, default=1536, help="Embedding dimension")
    parser.add_argument(
        "--skip-drop", action="store_true", help="Skip dropping old indexes"
    )

    args = parser.parse_args()

    migration = VectorMigration(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password,
    )

    await migration.run_full_migration(dim=args.dim, drop_old=not args.skip_drop)


if __name__ == "__main__":
    asyncio.run(main())
