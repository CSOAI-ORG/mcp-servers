"""
Memory webhook handlers
"""

from typing import Any, Callable, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MemoryWebhookHandler:
    """
    Handle memory-related webhooks

    Events:
        - memory.stored: Memory successfully stored
        - memory.queried: Memory query executed
    """

    def __init__(
        self,
        on_stored: Optional[Callable] = None,
        on_queried: Optional[Callable] = None,
    ):
        self.on_stored = on_stored
        self.on_queried = on_queried

    async def handle_stored(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle memory stored event

        Data expected:
            - memory_id: str
            - content_preview: str (first 100 chars)
            - memory_type: str
            - importance: float
            - tags: list
        """
        logger.debug(f"Memory stored: {data.get('memory_id')}")

        if self.on_stored:
            return await self.on_stored(data)

        return {"processed": True}

    async def handle_queried(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle memory query event

        Data expected:
            - query: str
            - results_count: int
            - results: list
            - query_time_ms: float
        """
        logger.info(
            f"Query executed: '{data.get('query')}' "
            f"returned {data.get('results_count')} results"
        )

        if self.on_queried:
            return await self.on_queried(data)

        return {"processed": True}


def filter_memories_by_tags(memories: List[Dict], tags: List[str]) -> List[Dict]:
    """Filter memories containing any of the specified tags"""
    return [m for m in memories if any(tag in m.get("tags", []) for tag in tags)]


def deduplicate_memories(memories: List[Dict], threshold: float = 0.9) -> List[Dict]:
    """
    Remove duplicate memories based on content similarity

    Args:
        memories: List of memory dicts
        threshold: Similarity threshold (0-1)

    Returns:
        Deduplicated list of memories
    """
    from difflib import SequenceMatcher

    seen = []
    result = []

    for memory in memories:
        content = memory.get("content", "")
        is_duplicate = False

        for existing in seen:
            similarity = SequenceMatcher(None, content, existing).ratio()
            if similarity >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            seen.append(content)
            result.append(memory)

    return result


def create_memory_archive(
    memories: List[Dict], archive_format: str = "json"
) -> Dict[str, Any]:
    """
    Create archive payload from memories

    Args:
        memories: List of memory dicts
        archive_format: Format (json, csv)

    Returns:
        Archive payload
    """
    import json
    from datetime import datetime

    if archive_format == "json":
        return {
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "count": len(memories),
            "memories": memories,
        }
    elif archive_format == "csv":
        import csv
        import io

        output = io.StringIO()
        if memories:
            writer = csv.DictWriter(output, fieldnames=memories[0].keys())
            writer.writeheader()
            writer.writerows(memories)

        return {
            "format": "csv",
            "content": output.getvalue(),
            "count": len(memories),
        }

    return {"error": f"Unknown format: {archive_format}"}
