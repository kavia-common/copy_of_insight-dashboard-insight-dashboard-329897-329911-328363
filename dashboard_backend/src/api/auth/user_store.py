from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.api.auth.security import get_password_hash, verify_password
from src.api.core.errors import AuthError


@dataclass(frozen=True)
class User:
    """User record used by the mock auth service."""

    username: str
    full_name: str
    role: str  # 'admin' | 'user'
    hashed_password: str


class InMemoryUserStore:
    """A tiny user store for mock authentication.

    Contract:
      - Inputs: username strings.
      - Outputs: User or None.
      - Errors: none.
      - Side effects: none (static data).
    """

    def __init__(self) -> None:
        # Pre-hashed to keep auth realistic. Passwords: admin123 / user123
        self._users: dict[str, User] = {
            "admin": User(
                username="admin",
                full_name="Admin User",
                role="admin",
                hashed_password=get_password_hash("admin123"),
            ),
            "user": User(
                username="user",
                full_name="Standard User",
                role="user",
                hashed_password=get_password_hash("user123"),
            ),
        }

    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def authenticate(self, username: str, password: str) -> User:
        user = self.get_user(username)
        if not user:
            raise AuthError("Invalid username or password")
        if not verify_password(password, user.hashed_password):
            raise AuthError("Invalid username or password")
        return user
