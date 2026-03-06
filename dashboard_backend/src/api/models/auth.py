from __future__ import annotations

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")
    role: str = Field(..., description="User role included for convenience")
    username: str = Field(..., description="Username (subject)")


class LoginRequest(BaseModel):
    """Login request payload."""

    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class UserProfile(BaseModel):
    """Current user profile response."""

    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    role: str = Field(..., description="Role: admin|user")
