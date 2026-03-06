from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext

from src.api.core.settings import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plaintext password for storage."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def create_access_token(
    *,
    subject: str,
    role: str,
    settings: Settings,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    Contract:
      - Inputs:
          subject: unique user identifier (string).
          role: 'admin' | 'user' (string).
          settings: Settings containing signing config.
          expires_delta: optional timedelta; defaults to settings value.
      - Output: encoded JWT string
      - Errors: none expected
      - Side effects: none
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expires_minutes))
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# PUBLIC_INTERFACE
def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    """Decode and validate a JWT token.

    Errors:
      - jose.JWTError if invalid/expired.
    """
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
