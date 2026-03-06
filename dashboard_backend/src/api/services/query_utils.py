from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Sequence


@dataclass(frozen=True)
class PageRequest:
    """Pagination request (1-indexed)."""

    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class SortRequest:
    """Sorting request."""

    sort_by: Optional[str] = None
    sort_dir: str = "desc"  # 'asc' | 'desc'


def apply_sort(
    items: Sequence[dict[str, Any]],
    sort: SortRequest,
    key_fn: Optional[Callable[[dict[str, Any]], Any]] = None,
) -> list[dict[str, Any]]:
    """Sort a list of dict items by a key.

    Contract:
      - items: list of dicts
      - sort_by: dict key to sort by (if None -> no sorting)
      - sort_dir: asc|desc
      - key_fn: optional override mapping item->value (if provided, sort_by is ignored)
    """
    if not sort.sort_by and key_fn is None:
        return list(items)

    reverse = sort.sort_dir.lower() != "asc"

    def _key(item: dict[str, Any]) -> Any:
        if key_fn:
            return key_fn(item)
        return item.get(sort.sort_by or "")

    return sorted(list(items), key=_key, reverse=reverse)


def apply_contains_filter(
    items: Iterable[dict[str, Any]],
    *,
    field: Optional[str],
    contains: Optional[str],
) -> list[dict[str, Any]]:
    """Filter items where field contains substring (case-insensitive)."""
    if not field or not contains:
        return list(items)
    needle = contains.lower()

    out: list[dict[str, Any]] = []
    for it in items:
        val = it.get(field)
        if val is None:
            continue
        if needle in str(val).lower():
            out.append(it)
    return out


def paginate(items: Sequence[dict[str, Any]], page_req: PageRequest) -> tuple[list[dict[str, Any]], int, int]:
    """Paginate items.

    Returns: (page_items, total_items, total_pages)
    """
    total_items = len(items)
    if total_items == 0:
        return [], 0, 0

    page = max(1, page_req.page)
    page_size = max(1, min(200, page_req.page_size))
    total_pages = (total_items + page_size - 1) // page_size

    start = (page - 1) * page_size
    end = start + page_size
    return list(items[start:end]), total_items, total_pages
