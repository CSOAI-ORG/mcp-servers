"""
MEOK AI Labs - Python SDK Client
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import httpx


@dataclass
class MEOKConfig:
    api_key: str
    base_url: str = "https://meok.ai/api/v1"
    timeout: int = 60
    max_retries: int = 3


class MEOKClient:
    """
    Main client for MEOK AI Labs API

    Usage:
        from meokai import MEOKClient

        client = MEOKClient(api_key="your-api-key")

        # Analyze content
        result = client.governance.analyze("Hello world")

        # Store memory
        client.memory.store("User prefers email")

        # Run agent task
        task = client.agents.create_task("researcher", "Find AI news")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://meok.ai/api/v1",
        timeout: int = 60,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.environ.get("MEOK_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "API key required. Set MEOK_API_KEY env var or pass api_key."
            )

        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

        # Initialize sub-clients
        self.governance = GovernanceClient(self)
        self.memory = MemoryClient(self)
        self.agents = AgentClient(self)
        self.consciousness = ConsciousnessClient(self)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make API request with retry logic"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(self._client.timeout.__class__.__name__ or 3):
            try:
                if method.upper() == "GET":
                    response = self._client.get(url, params=params)
                elif method.upper() == "POST":
                    response = self._client.post(url, json=data)
                elif method.upper() == "PUT":
                    response = self._client.put(url, json=data)
                elif method.upper() == "DELETE":
                    response = self._client.delete(url)
                else:
                    raise ValueError(f"Unknown method: {method}")

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    import time

                    time.sleep(2**attempt)
                    continue
                raise
            except httpx.RequestError:
                if attempt < max_retries - 1:
                    import time

                    time.sleep(2**attempt)
                    continue
                raise

        return {}

    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        response = self._client.get(f"{self.base_url}/auth/rate-limit")
        return response.json()

    def close(self):
        """Close the HTTP client"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class GovernanceClient:
    """Client for AI Governance endpoints"""

    def __init__(self, client: MEOKClient):
        self._client = client

    def analyze(
        self,
        content: str,
        content_type: str = "text",
        framework: str = "constitutional",
    ) -> Dict[str, Any]:
        """
        Analyze content against Constitutional AI principles

        Args:
            content: Text, code, or document to analyze
            content_type: Type of content (text, code, document)
            framework: Governance framework (constitutional, eu-ai-act, etc.)

        Returns:
            Analysis result with score, violations, recommendations
        """
        return self._client._request(
            "POST",
            "/governance/analyze",
            data={
                "content": content,
                "type": content_type,
                "framework": framework,
            },
        )

    def check_compliance(
        self,
        content: str,
        standards: List[str],
    ) -> Dict[str, Any]:
        """Check compliance against specific standards"""
        return self._client._request(
            "POST",
            "/governance/compliance",
            data={
                "content": content,
                "standards": standards,
            },
        )


class MemoryClient:
    """Client for Memory endpoints"""

    def __init__(self, client: MEOKClient):
        self._client = client

    def store(
        self,
        content: str,
        memory_type: str = "episodic",
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Store a memory

        Args:
            content: Memory content
            memory_type: Type (episodic, semantic, procedural)
            tags: Optional tags for organization
            importance: Importance score 0-1
        """
        return self._client._request(
            "POST",
            "/memory",
            data={
                "content": content,
                "type": memory_type,
                "tags": tags or [],
                "importance": importance,
            },
        )

    def query(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Query memories semantically"""
        return self._client._request(
            "GET", "/memory", params={"q": query, "limit": limit}
        )


class AgentClient:
    """Client for Agent endpoints"""

    def __init__(self, client: MEOKClient):
        self._client = client

    def create_task(
        self,
        agent_id: str,
        instruction: str,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """Create an agent task"""
        return self._client._request(
            "POST",
            f"/agents/{agent_id}/tasks",
            data={
                "instruction": instruction,
                "priority": priority,
            },
        )

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task status and result"""
        return self._client._request("GET", f"/agents/tasks/{task_id}")


class ConsciousnessClient:
    """Client for Consciousness endpoints"""

    def __init__(self, client: MEOKClient):
        self._client = client

    def get_state(self) -> Dict[str, Any]:
        """Get current consciousness state"""
        return self._client._request("GET", "/consciousness/state")

    def enter_dream_mode(self) -> Dict[str, Any]:
        """Enter dream mode for reflection"""
        return self._client._request("POST", "/consciousness/dream")
