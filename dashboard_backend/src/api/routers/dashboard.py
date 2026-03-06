from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from src.api.auth.deps import get_current_user, require_role
from src.api.auth.user_store import User

from src.api.models.dashboard import ChartResponse, KPIResponse, TableResponse
from src.api.services.mock_data import DashboardQuery, MockDashboardDataService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_data_service() -> MockDashboardDataService:
    """Dependency provider for mock data service."""
    return MockDashboardDataService()


@router.get(
    "/kpis",
    response_model=KPIResponse,
    summary="Get KPI cards",
    description="Returns KPI card data for the overview page.",
    operation_id="dashboard_get_kpis",
)
def get_kpis(
    user: Annotated[User, Depends(get_current_user)],
    svc: Annotated[MockDashboardDataService, Depends(get_data_service)],
):
    """Get KPIs for any authenticated user."""
    _ = user
    return {"items": svc.get_kpis()}


@router.get(
    "/charts/{chart_id}",
    response_model=ChartResponse,
    summary="Get chart data",
    description="Returns chart series data for the requested chart id.",
    operation_id="dashboard_get_chart",
)
def get_chart(
    chart_id: str,
    user: Annotated[User, Depends(get_current_user)],
    svc: Annotated[MockDashboardDataService, Depends(get_data_service)],
    days: int = Query(14, ge=3, le=90, description="Number of days to return"),
):
    """Get chart series for any authenticated user."""
    _ = user
    return svc.get_chart(chart_id=chart_id, days=days)


@router.get(
    "/table",
    response_model=TableResponse,
    summary="Get table rows",
    description="Returns a paginated table dataset with optional contains-filter and sorting.",
    operation_id="dashboard_get_table",
)
def get_table(
    user: Annotated[User, Depends(get_current_user)],
    svc: Annotated[MockDashboardDataService, Depends(get_data_service)],
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=200, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field name to sort by"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    search_field: Optional[str] = Query(None, description="Field to apply contains-filter on (e.g. name, status, owner)"),
    search_contains: Optional[str] = Query(None, description="Substring to search for (case-insensitive)"),
):
    """Get table rows for any authenticated user."""
    _ = user
    query = DashboardQuery(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        search_field=search_field,
        search_contains=search_contains,
    )
    return svc.get_table(query)


@router.get(
    "/admin/sample",
    summary="Admin-only sample endpoint",
    description="Demonstrates role-based access control (admin only).",
    operation_id="dashboard_admin_sample",
)
def admin_sample(
    user: Annotated[User, Depends(require_role("admin"))],
):
    """Admin-only sample endpoint."""
    return JSONResponse(content={"message": "Hello admin!", "user": {"username": user.username, "role": user.role}})


@router.get(
    "/user/sample",
    summary="User-only sample endpoint",
    description="Demonstrates role-based access control (user only).",
    operation_id="dashboard_user_sample",
)
def user_sample(
    user: Annotated[User, Depends(require_role("user"))],
):
    """User-only sample endpoint."""
    return JSONResponse(content={"message": "Hello user!", "user": {"username": user.username, "role": user.role}})
