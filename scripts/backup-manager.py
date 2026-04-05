#!/usr/bin/env python3
"""
MEOK AI Labs - Backup and Recovery System
Automated backups for PostgreSQL, Redis, and file storage
"""

import os
import sys
import json
import gzip
import shutil
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    import asyncpg
    import redis
except ImportError:
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "asyncpg", "redis"])
    import asyncpg
    import redis


@dataclass
class BackupConfig:
    """Backup configuration"""

    backup_dir: str = "/backups/meok"
    postgres_url: str = "postgresql://postgres:password@localhost:5432/meok"
    redis_url: str = "redis://localhost:6379"
    retention_days: int = 30
    compress: bool = True
    s3_bucket: Optional[str] = None


class BackupManager:
    """
    Manages automated backups for MEOK AI Labs
    """

    def __init__(self, config: Optional[BackupConfig] = None):
        self.config = config or BackupConfig()
        self.backup_path = Path(self.config.backup_dir)
        self.backup_path.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_backup_name(self, backup_type: str) -> str:
        """Generate backup filename"""
        return f"meok_{backup_type}_{self.timestamp}"

    def _checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def backup_postgres(self) -> Dict[str, str]:
        """
        Backup PostgreSQL database

        Returns:
            Dict with backup file path and checksum
        """
        print(f"📦 Starting PostgreSQL backup...")

        backup_name = self._get_backup_name("postgres")
        backup_file = self.backup_path / f"{backup_name}.sql"

        # Parse connection URL
        db_url = self.config.postgres_url
        parts = db_url.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")

        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        host_port = host_db[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"
        db_name = host_db[1] if len(host_db) > 1 else "meok"

        # Run pg_dump
        env = os.environ.copy()
        env["PGPASSWORD"] = password

        cmd = [
            "pg_dump",
            "-h",
            host,
            "-p",
            port,
            "-U",
            user,
            "-d",
            db_name,
            "-Fc",  # Custom format
            "-f",
            str(backup_file),
        ]

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ PostgreSQL backup failed: {result.stderr}")
            raise Exception(f"pg_dump failed: {result.stderr}")

        checksum = self._checksum(backup_file)

        # Compress if enabled
        if self.config.compress:
            compressed = backup_file.with_suffix(".sql.gz")
            with gzip.open(compressed, "wb") as f_out:
                with open(backup_file, "rb") as f_in:
                    shutil.copyfileobj(f_in, f_out)
            compressed.unlink()  # Remove uncompressed
            backup_file = compressed

        print(f"✅ PostgreSQL backup complete: {backup_file.name}")

        return {
            "type": "postgres",
            "file": str(backup_file),
            "checksum": checksum,
            "size_bytes": backup_file.stat().st_size,
            "timestamp": self.timestamp,
        }

    def backup_redis(self) -> Dict[str, str]:
        """
        Backup Redis data

        Returns:
            Dict with backup file path and checksum
        """
        print(f"📦 Starting Redis backup...")

        r = redis.from_url(self.config.redis_url)

        # Save Redis data
        backup_name = self._get_backup_name("redis")
        backup_file = self.backup_path / f"{backup_name}.rdb"

        # Trigger BGSAVE
        r.bgsave()

        # Wait for save to complete
        while r.lastsave() < datetime.now().timestamp() - 5:
            import time

            time.sleep(0.5)

        # Copy the dump file
        dump_files = list(Path("/var/lib/redis").glob("dump.rdb"))
        if not dump_files:
            dump_files = list(Path.home().glob("*.rdb"))

        if dump_files:
            shutil.copy(dump_files[0], backup_file)
        else:
            # Fallback: use SAVE command output
            keys = r.keys("*")
            data = {}
            for key in keys:
                key_type = r.type(key)
                if key_type == "string":
                    data[key] = r.get(key)
                elif key_type == "hash":
                    data[key] = r.hgetall(key)
                elif key_type == "list":
                    data[key] = r.lrange(key, 0, -1)

            with gzip.open(backup_file.with_suffix(".json.gz"), "wt") as f:
                json.dump(data, f)
            backup_file.unlink()
            backup_file = backup_file.with_suffix(".json.gz")

        checksum = self._checksum(backup_file)

        print(f"✅ Redis backup complete: {backup_file.name}")

        return {
            "type": "redis",
            "file": str(backup_file),
            "checksum": checksum,
            "size_bytes": backup_file.stat().st_size,
            "timestamp": self.timestamp,
        }

    def backup_files(self, directories: List[str]) -> List[Dict[str, str]]:
        """
        Backup specified directories

        Args:
            directories: List of directory paths to backup

        Returns:
            List of backup info dicts
        """
        print(f"📦 Starting file backup...")

        backups = []

        for directory in directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                print(f"⚠️ Directory not found: {directory}")
                continue

            backup_name = self._get_backup_name(f"files_{dir_path.name}")
            backup_file = self.backup_path / f"{backup_name}.tar.gz"

            # Create archive
            result = subprocess.run(
                [
                    "tar",
                    "-czf",
                    str(backup_file),
                    "-C",
                    str(dir_path.parent),
                    dir_path.name,
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"❌ File backup failed for {directory}: {result.stderr}")
                continue

            checksum = self._checksum(backup_file)

            backups.append(
                {
                    "type": "files",
                    "source": directory,
                    "file": str(backup_file),
                    "checksum": checksum,
                    "size_bytes": backup_file.stat().st_size,
                    "timestamp": self.timestamp,
                }
            )

            print(f"✅ File backup complete: {backup_file.name}")

        return backups

    async def run_full_backup(self, file_dirs: List[str] = None) -> Dict:
        """
        Run full backup of all systems

        Args:
            file_dirs: Optional list of directories to backup
        """
        print(f"\n{'=' * 60}")
        print(f"MEOK AI Labs - Full Backup")
        print(f"{'=' * 60}\n")

        results = {"timestamp": self.timestamp, "backups": []}

        # PostgreSQL
        try:
            pg_result = await self.backup_postgres()
            results["backups"].append(pg_result)
        except Exception as e:
            results["backups"].append({"type": "postgres", "error": str(e)})

        # Redis
        try:
            redis_result = self.backup_redis()
            results["backups"].append(redis_result)
        except Exception as e:
            results["backups"].append({"type": "redis", "error": str(e)})

        # Files
        if file_dirs:
            try:
                file_backups = self.backup_files(file_dirs)
                results["backups"].extend(file_backups)
            except Exception as e:
                results["backups"].append({"type": "files", "error": str(e)})

        # Save backup manifest
        manifest_file = self.backup_path / f"backup_manifest_{self.timestamp}.json"
        with open(manifest_file, "w") as f:
            json.dump(results, f, indent=2)

        # Cleanup old backups
        self.cleanup_old_backups()

        print(f"\n✅ Full backup complete!")
        print(f"📋 Manifest: {manifest_file}")

        return results

    def cleanup_old_backups(self) -> int:
        """
        Remove backups older than retention period

        Returns:
            Number of backups removed
        """
        print(f"\n🧹 Cleaning up old backups (>{self.config.retention_days} days)...")

        cutoff = datetime.now() - timedelta(days=self.config.retention_days)
        removed = 0

        for backup_file in self.backup_path.glob("meok_*"):
            if backup_file.is_file():
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if mtime < cutoff:
                    backup_file.unlink()
                    removed += 1

        # Also clean manifest files
        for manifest in self.backup_path.glob("backup_manifest_*"):
            mtime = datetime.fromtimestamp(manifest.stat().st_mtime)
            if mtime < cutoff:
                manifest.unlink()
                removed += 1

        print(f"✅ Removed {removed} old backups")
        return removed

    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []

        for backup_file in self.backup_path.glob("meok_*"):
            if backup_file.is_file():
                backups.append(
                    {
                        "file": backup_file.name,
                        "size_mb": round(backup_file.stat().st_size / 1024 / 1024, 2),
                        "created": datetime.fromtimestamp(
                            backup_file.stat().st_mtime
                        ).isoformat(),
                    }
                )

        return sorted(backups, key=lambda x: x["created"], reverse=True)


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="MEOK AI Labs Backup Manager")
    parser.add_argument("--full", action="store_true", help="Run full backup")
    parser.add_argument("--postgres", action="store_true", help="Backup PostgreSQL")
    parser.add_argument("--redis", action="store_true", help="Backup Redis")
    parser.add_argument("--files", nargs="+", help="Backup file directories")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup old backups")
    parser.add_argument("--list", action="store_true", help="List backups")

    args = parser.parse_args()

    manager = BackupManager()

    if args.list:
        backups = manager.list_backups()
        print("\n📦 Available Backups:")
        for b in backups:
            print(f"  {b['file']} - {b['size_mb']} MB")

    elif args.cleanup:
        manager.cleanup_old_backups()

    elif args.full:
        await manager.run_full_backup(args.files)

    elif args.postgres:
        await manager.backup_postgres()

    elif args.redis:
        manager.backup_redis()

    elif args.files:
        manager.backup_files(args.files)

    else:
        # Default: run full backup
        await manager.run_full_backup()


if __name__ == "__main__":
    asyncio.run(main())
