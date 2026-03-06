from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.core.errors import AuthError, ForbiddenError, NotFoundError, ValidationAppError
from src.api.core.logging import get_logger, log_kv
from src.api.core.settings import Settings
from src.api.routers.auth import router as auth_router
from src.api.routers.dashboard import router as dashboard_router

logger = get_logger(__name__)

openapi_tags = [
    {"name": "health", "description": "Health and diagnostics endpoints"},
    {"name": "auth", "description": "Authentication endpoints (JWT)"},
    {"name": "dashboard", "description": "Dashboard data endpoints (KPIs, charts, tables)"},
]


def create_app() -> FastAPI:
    """Create the FastAPI application.

    Contract:
      - Inputs: environment variables (via Settings.from_env()).
      - Outputs: FastAPI app instance.
      - Errors: may raise ValueError for invalid settings.
      - Side effects: registers middleware, routers, exception handlers.
    """
    settings = Settings.from_env()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Backend API for the Insight Dashboard.\n\n"
            "Auth:\n"
            "- POST /auth/login with mock users: admin/admin123, user/user123\n"
            "- Use `Authorization: Bearer <token>` for protected endpoints.\n\n"
            "RBAC:\n"
            "- /dashboard/admin/sample requires role=admin\n"
            "- /dashboard/user/sample requires role=user\n"
        ),
        version=settings.app_version,
        openapi_tags=openapi_tags,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allow_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AuthError)
    async def auth_error_handler(_: Request, exc: AuthError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(ForbiddenError)
    async def forbidden_error_handler(_: Request, exc: ForbiddenError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(_: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValidationAppError)
    async def validation_error_handler(_: Request, exc: ValidationAppError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.get(
        "/",
        tags=["health"],
        summary="Health check",
        description="Simple health endpoint for uptime checks.",
        operation_id="health_check",
    )
    def health_check() -> dict[str, Any]:
        """Health check endpoint."""
        return {"message": "Healthy"}

    @app.get(
        "/docs/ws-help",
        tags=["health"],
        summary="WebSocket usage help",
        description="This project currently exposes REST endpoints only (no WebSocket).",
        operation_id="docs_ws_help",
    )
    def ws_help() -> dict[str, str]:
        """Explicit doc endpoint for websocket usage (none configured)."""
        return {"websocket": "Not implemented in this backend. Use REST API endpoints under /auth and /dashboard."}

    app.include_router(auth_router)
    app.include_router(dashboard_router)

    log_kv(logger, logging.INFO, "AppCreated", version=settings.app_version, env=settings.environment)
    return app


app = create_app()
