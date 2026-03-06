from __future__ import annotations

import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.auth.deps import get_current_user, get_settings, get_user_store
from src.api.auth.security import create_access_token
from src.api.auth.user_store import InMemoryUserStore, User
from src.api.core.errors import AuthError
from src.api.core.logging import get_logger, log_kv
from src.api.core.settings import Settings
from src.api.models.auth import LoginRequest, TokenResponse, UserProfile

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT access token",
    description="Authenticates against a mock user store and returns a JWT token. "
    "Mock users: admin/admin123 (role=admin) and user/user123 (role=user).",
    operation_id="auth_login",
)
def login(
    body: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[InMemoryUserStore, Depends(get_user_store)],
):
    """Login endpoint.

    Contract:
      - Inputs: JSON {username, password}
      - Outputs: {access_token, token_type, role, username}
      - Errors: 401 on invalid credentials
    """
    log_kv(logger, logging.INFO, "AuthLogin.start", username=body.username)
    try:
        user = store.authenticate(body.username, body.password)
        token = create_access_token(
            subject=user.username,
            role=user.role,
            settings=settings,
            expires_delta=timedelta(minutes=settings.access_token_expires_minutes),
        )
        log_kv(logger, logging.INFO, "AuthLogin.success", username=user.username, role=user.role)
        return TokenResponse(access_token=token, token_type="bearer", role=user.role, username=user.username)
    except AuthError as e:
        log_kv(logger, logging.WARNING, "AuthLogin.failed", username=body.username, error=str(e))
        return JSONResponse(status_code=401, content={"detail": str(e)})


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user profile",
    description="Returns the current authenticated user's profile based on the JWT bearer token.",
    operation_id="auth_me",
)
def me(user: Annotated[User, Depends(get_current_user)]):
    """Return authenticated user's profile."""
    return UserProfile(username=user.username, full_name=user.full_name, role=user.role)
