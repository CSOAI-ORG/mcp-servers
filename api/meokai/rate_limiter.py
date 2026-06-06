"""
MEOK AI Labs - Rate Limiter
"""

import time
from typing import Dict, Optional
from collections import defaultdict


class RateLimiter:
    """Token bucket rate limiter with Redis support"""

    def __init__(
        self,
        requests_per_minute: int = 100,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day

        self.buckets: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                "minute": 0,
                "hour": 0,
                "day": 0,
                "last_minute": time.time(),
                "last_hour": time.time(),
                "last_day": time.time(),
            }
        )

    def _reset_if_needed(self, api_key: str, bucket: Dict) -> None:
        """Reset counters if time window has passed"""
        now = time.time()

        if now - bucket["last_minute"] >= 60:
            bucket["minute"] = 0
            bucket["last_minute"] = now

        if now - bucket["last_hour"] >= 3600:
            bucket["hour"] = 0
            bucket["last_hour"] = now

        if now - bucket["last_day"] >= 86400:
            bucket["day"] = 0
            bucket["last_day"] = now

    async def check(self, api_key: str) -> bool:
        """Check if request is allowed"""
        bucket = self.buckets[api_key]
        self._reset_if_needed(api_key, bucket)

        if bucket["minute"] >= self.requests_per_minute:
            raise RateLimitExceeded("Minute limit exceeded")

        if bucket["hour"] >= self.requests_per_hour:
            raise RateLimitExceeded("Hour limit exceeded")

        if bucket["day"] >= self.requests_per_day:
            raise RateLimitExceeded("Day limit exceeded")

        bucket["minute"] += 1
        bucket["hour"] += 1
        bucket["day"] += 1

        return True

    def get_limits(self, api_key: str) -> Dict[str, int]:
        """Get current rate limit status"""
        bucket = self.buckets[api_key]
        self._reset_if_needed(api_key, bucket)

        return {
            "minute_remaining": self.requests_per_minute - bucket["minute"],
            "minute_limit": self.requests_per_minute,
            "hour_remaining": self.requests_per_hour - bucket["hour"],
            "hour_limit": self.requests_per_hour,
            "day_remaining": self.requests_per_day - bucket["day"],
            "day_limit": self.requests_per_day,
        }

    def reset(self, api_key: str) -> None:
        """Reset rate limits for an API key"""
        if api_key in self.buckets:
            del self.buckets[api_key]


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""

    def __init__(self, message: str = "Rate limit exceeded"):
        self.message = message
        super().__init__(self.message)
