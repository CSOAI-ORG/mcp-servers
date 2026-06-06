"""
MEOK AI Labs - Configuration
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    API_VERSION: str = "2.0.0"
    LOG_LEVEL: str = "info"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://meok:password@localhost:5432/meokai"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    CORS_ORIGINS: str = "https://meok.ai,https://www.meok.ai"

    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000

    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
