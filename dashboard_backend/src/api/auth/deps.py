from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, Header
from jose import JWTError

from src.api.auth.security import decode_token
from src.api.auth.user_store import InMemoryUserStore, User
from src.api.core.errors import AuthError, ForbiddenError
from src.api.core.settings import Settings


def get_settings() -> Settings:
    """Dependency provider for Settings (boundary-normalized)."""
    return Settings.from_env()


def get_user_store() -> InMemoryUserStore:
    """Dependency provider for the (mock) user store."""
    return InMemoryUserStore()


# PUBLIC_INTERFACE
def get_current_user(
    authorization: Annotated[Optional[str], Header()] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,  # type: ignore[assignment]
    store: Annotated[InMemoryUserStore, Depends(get_user_store)] = None,  # type: ignore[assignment]
) -> User:
    """Resolve the current authenticated user from Authorization: Bearer <token>.

    Contract:
      - Input: Authorization header.
      - Output: User record.
      - Errors: AuthError if missing/invalid token or unknown subject.
      - Side effects: none.
    """
    if not authorization:
        raise AuthError("Missing Authorization header")
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("Invalid Authorization header format (expected Bearer token)")
    token = parts[1].strip()
    if not token:
        raise AuthError("Missing bearer token")

    try:
        payload = decode_token(token, settings)
    except JWTError as e:
        raise AuthError("Invalid or expired token") from e

    username = payload.get("sub")
    if not isinstance(username, str) or not username:
        raise AuthError("Invalid token subject")
    user = store.get_user(username)
    if not user:
        raise AuthError("User not found")
    return user


# PUBLIC_INTERFACE
def require_role(required_role: str):
    """Factory for RBAC dependency.

    Contract:
      - Input: required_role ('admin' or 'user')
      - Output: dependency that returns User
      - Errors: ForbiddenError if role mismatch, AuthError if not logged in
    """

    def _checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role != required_role:
            raise ForbiddenError(f"Requires role: {required_role}")
        return user

    return _checker
