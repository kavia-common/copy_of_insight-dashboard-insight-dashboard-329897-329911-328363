from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from src.api.core.logging import get_logger, log_kv
from src.api.services.query_utils import (
    PageRequest,
    SortRequest,
    apply_contains_filter,
    apply_sort,
    paginate,
)

logger = get_logger(__name__)


@dataclass(frozen=True)
class DashboardQuery:
    """Normalized dashboard query.

    Contract:
      - Inputs: optional date range and free-text filter.
      - Outputs: used to drive mock data selection.
      - Side effects: none.
    """

    search_field: Optional[str] = None
    search_contains: Optional[str] = None

    page: int = 1
    page_size: int = 20
    sort_by: Optional[str] = None
    sort_dir: str = "desc"


class MockDashboardDataService:
    """Service providing deterministic-ish mock data for the dashboard.

    This is intentionally in-memory and free of external dependencies so
    the frontend can integrate end-to-end without a database.
    """

    def __init__(self, seed: int = 42) -> None:
        self._rand = random.Random(seed)

    # PUBLIC_INTERFACE
    def get_kpis(self) -> list[dict[str, Any]]:
        """Return mock KPI items."""
        items = [
            {"id": "revenue", "label": "Revenue", "value": 128430.5, "unit": "$", "delta": 4.2, "trend": "up"},
            {"id": "users", "label": "Active Users", "value": 8421, "unit": "", "delta": -1.1, "trend": "down"},
            {"id": "conversion", "label": "Conversion", "value": 3.42, "unit": "%", "delta": 0.3, "trend": "up"},
            {"id": "uptime", "label": "Uptime", "value": 99.95, "unit": "%", "delta": 0.0, "trend": "flat"},
        ]
        return items

    # PUBLIC_INTERFACE
    def get_chart(self, chart_id: str, days: int = 14) -> dict[str, Any]:
        """Return mock chart series data for a given chart_id."""
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        base = self._rand.uniform(50, 120)

        def mk_points(mult: float) -> list[dict[str, Any]]:
            pts: list[dict[str, Any]] = []
            for i in range(days):
                ts = now - timedelta(days=(days - 1 - i))
                noise = self._rand.uniform(-8, 8)
                pts.append({"ts": ts, "value": max(0, base * mult + noise + i * self._rand.uniform(-0.8, 1.4))})
            return pts

        if chart_id == "traffic":
            series = [
                {"id": "sessions", "label": "Sessions", "points": mk_points(1.0)},
                {"id": "pageviews", "label": "Pageviews", "points": mk_points(1.6)},
            ]
        elif chart_id == "sales":
            series = [{"id": "orders", "label": "Orders", "points": mk_points(0.7)}]
        else:
            series = [{"id": "metric", "label": "Metric", "points": mk_points(1.0)}]

        return {"chart_id": chart_id, "series": series, "meta": {"days": days}}

    def _all_table_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        # Stable-but-varied data
        statuses = ["New", "In Progress", "Blocked", "Done"]
        owners = ["Alex", "Sam", "Jordan", "Taylor", "Morgan"]
        for i in range(1, 151):
            rows.append(
                {
                    "id": f"row_{i}",
                    "name": f"Item {i}",
                    "status": statuses[i % len(statuses)],
                    "owner": owners[i % len(owners)],
                    "score": round(50 + (i % 50) + self._rand.uniform(-5, 5), 2),
                    "updated_at": (datetime.now(timezone.utc) - timedelta(days=i % 30)).isoformat(),
                }
            )
        return rows

    # PUBLIC_INTERFACE
    def get_table(self, query: DashboardQuery) -> dict[str, Any]:
        """Return a table response with filter/sort/pagination applied.

        Contract:
          - Inputs: DashboardQuery with page/page_size/sort/filter.
          - Outputs: dict {rows:[...], meta:{...}}
          - Errors: none (inputs are normalized at API boundary)
        """
        log_kv(
            logger,
            level=20,
            message="MockDashboardDataService.get_table",
            page=query.page,
            page_size=query.page_size,
            sort_by=query.sort_by,
            sort_dir=query.sort_dir,
            search_field=query.search_field,
            search_contains=query.search_contains,
        )

        all_rows = self._all_table_rows()
        filtered = apply_contains_filter(
            all_rows, field=query.search_field, contains=query.search_contains
        )

        sorted_rows = apply_sort(filtered, SortRequest(sort_by=query.sort_by, sort_dir=query.sort_dir))
        page_rows, total_items, total_pages = paginate(sorted_rows, PageRequest(page=query.page, page_size=query.page_size))

        return {
            "rows": [{"id": r["id"], "data": r} for r in page_rows],
            "meta": {
                "page": max(1, query.page),
                "page_size": max(1, min(200, query.page_size)),
                "total_items": total_items,
                "total_pages": total_pages,
            },
        }
