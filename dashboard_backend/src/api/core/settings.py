from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings normalized at the boundary.

    Contract:
      - Inputs: environment variables (strings).
      - Outputs: typed settings values.
      - Errors: raises ValueError for invalid numeric values.
      - Side effects: none.
    """

    app_name: str = "Insight Dashboard Backend"
    app_version: str = "0.2.0"

    cors_allow_origins: tuple[str, ...] = ("*",)

    # JWT / Auth
    jwt_secret_key: str = "dev-insecure-secret"  # override in production
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 60

    # Basic behavior flags
    environment: str = "development"

    @staticmethod
    def from_env() -> "Settings":
        """Create Settings from environment variables.

        NOTE: The orchestrator should set these in `.env` for real deployments.
        """
        cors_origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "*").strip()
        cors_origins = tuple(
            [o.strip() for o in cors_origins_raw.split(",") if o.strip()]
        ) or ("*",)

        expires_raw = os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60")
        try:
            expires = int(expires_raw)
        except ValueError as e:
            raise ValueError(
                f"Invalid JWT_ACCESS_TOKEN_EXPIRES_MINUTES: {expires_raw}"
            ) from e

        return Settings(
            cors_allow_origins=cors_origins,
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "dev-insecure-secret"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expires_minutes=expires,
            environment=os.getenv("NODE_ENV", os.getenv("ENV", "development")),
        )
