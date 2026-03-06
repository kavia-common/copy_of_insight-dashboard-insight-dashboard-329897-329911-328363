from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    """Optional date range filter."""

    start: Optional[date] = Field(None, description="Start date (inclusive)")
    end: Optional[date] = Field(None, description="End date (inclusive)")


class KPIItem(BaseModel):
    """A single KPI card item."""

    id: str = Field(..., description="KPI identifier")
    label: str = Field(..., description="Display label")
    value: float = Field(..., description="KPI numeric value")
    unit: str = Field("", description="Optional unit (e.g. '%', '$')")
    delta: float = Field(0, description="Change vs previous period (positive/negative)")
    trend: Literal["up", "down", "flat"] = Field("flat", description="Trend indicator")


class KPIResponse(BaseModel):
    """KPI list response."""

    items: list[KPIItem] = Field(..., description="KPI items")


class ChartPoint(BaseModel):
    """A point for time-series charts."""

    ts: datetime = Field(..., description="Timestamp (UTC)")
    value: float = Field(..., description="Point value")


class ChartSeries(BaseModel):
    """Chart series."""

    id: str = Field(..., description="Series id")
    label: str = Field(..., description="Series label")
    points: list[ChartPoint] = Field(..., description="Series points")


class ChartResponse(BaseModel):
    """Chart response containing one or more series."""

    chart_id: str = Field(..., description="Chart identifier")
    series: list[ChartSeries] = Field(..., description="Series list")
    meta: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TableRow(BaseModel):
    """Generic table row payload.

    Using dict payload keeps table extensible for mock service.
    """

    id: str = Field(..., description="Row identifier")
    data: dict[str, Any] = Field(..., description="Row data (column -> value)")


class PageMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(..., ge=1, description="Current page (1-indexed)")
    page_size: int = Field(..., ge=1, le=200, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total matching items")
    total_pages: int = Field(..., ge=0, description="Total pages")


class TableResponse(BaseModel):
    """Table response with rows and pagination."""

    rows: list[TableRow] = Field(..., description="Rows in this page")
    meta: PageMeta = Field(..., description="Pagination metadata")
