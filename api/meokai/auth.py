"""
MEOK AI Labs - Authentication
"""

import os
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Header

import jwt


class Auth:
    """Authentication utilities"""

    def __init__(self, secret: Optional[str] = None):
        self.secret = secret or os.getenv("JWT_SECRET", "change-me")
        self.algorithm = "HS256"

    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def verify_api_key(self, api_key: str) -> bool:
        """Verify an API key"""
        return len(api_key) >= 32

    def create_token(
        self,
        user_id: str,
        expires_hours: int = 24,
    ) -> str:
        """Create a JWT token"""
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
        }

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        """Decode a JWT token"""
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    def verify_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """Verify HMAC signature"""
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)


auth = Auth()


async def verify_api_key(x_api_key: str = Header(...)) -> str:
    """FastAPI dependency to verify API key"""
    if not auth.verify_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return x_api_key


async def get_current_user(token: str = Header(...)) -> dict:
    """FastAPI dependency to get current user from token"""
    return auth.decode_token(token)
