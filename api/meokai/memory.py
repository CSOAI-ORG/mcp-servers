"""
MEOK AI Labs - Vector Memory Store
"""

from typing import Dict, List, Any, Optional
import uuid
import hashlib
from datetime import datetime


class VectorStore:
    """Vector memory storage with semantic search"""

    def __init__(self):
        self.memories: Dict[str, Dict] = {}
        self.vectors: Dict[str, List[float]] = {}

    def _generate_embedding(self, content: str) -> List[float]:
        """Generate simple embedding (placeholder - use actual embedding model)"""
        words = content.lower().split()
        vector = [0.0] * 128

        for i, word in enumerate(words[:128]):
            char_sum = sum(ord(c) for c in word)
            vector[i % 128] = (char_sum % 100) / 100.0

        return vector

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    async def store(
        self,
        user_id: str,
        content: str,
        memory_type: str = "episodic",
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
    ) -> str:
        """Store a memory"""
        memory_id = str(uuid.uuid4())
        vector = self._generate_embedding(content)

        memory = {
            "id": memory_id,
            "user_id": user_id,
            "content": content,
            "type": memory_type,
            "tags": tags or [],
            "importance": importance,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self.memories[memory_id] = memory
        self.vectors[memory_id] = vector

        return memory_id

    async def query(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Query memories semantically"""
        query_vector = self._generate_embedding(query)

        results = []
        for memory_id, memory in self.memories.items():
            if user_id and memory.get("user_id") != user_id:
                continue

            vector = self.vectors.get(memory_id, [])
            similarity = self._cosine_similarity(query_vector, vector)

            results.append(
                {
                    "id": memory_id,
                    "content": memory["content"],
                    "type": memory["type"],
                    "tags": memory["tags"],
                    "importance": memory["importance"],
                    "similarity": similarity,
                    "created_at": memory["created_at"],
                }
            )

        results.sort(key=lambda x: (x["similarity"], x["importance"]), reverse=True)

        return {
            "query": query,
            "count": len(results[:limit]),
            "memories": results[:limit],
        }

    async def get(self, memory_id: str) -> Optional[Dict]:
        """Get a specific memory"""
        return self.memories.get(memory_id)

    async def delete(self, memory_id: str) -> bool:
        """Delete a memory"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            if memory_id in self.vectors:
                del self.vectors[memory_id]
            return True
        return False

    async def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: Optional[float] = None,
    ) -> Optional[Dict]:
        """Update a memory"""
        if memory_id not in self.memories:
            return None

        memory = self.memories[memory_id]

        if content is not None:
            memory["content"] = content
            self.vectors[memory_id] = self._generate_embedding(content)

        if tags is not None:
            memory["tags"] = tags

        if importance is not None:
            memory["importance"] = importance

        memory["updated_at"] = datetime.utcnow().isoformat()

        return memory
