from __future__ import annotations


class AuthError(Exception):
    """Raised when authentication fails."""


class ForbiddenError(Exception):
    """Raised when authorization (RBAC) fails."""


class NotFoundError(Exception):
    """Raised when a requested resource cannot be found."""


class ValidationAppError(Exception):
    """Raised for domain validation errors."""
