"""Load benchmark product catalog (structure from sample site, FO titles)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data" / "product_catalog.json"


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    if not _DATA.exists():
        return {
            "version": 0,
            "menu": [],
            "categories": [],
            "products": [],
            "payment_module": {},
        }
    return json.loads(_DATA.read_text(encoding="utf-8"))


def list_products(category_id: str | None = None) -> list[dict[str, Any]]:
    items = load_catalog().get("products") or []
    if category_id:
        items = [p for p in items if p.get("category_id") == category_id]
    return items


def get_product(product_id: str) -> dict[str, Any] | None:
    for p in load_catalog().get("products") or []:
        if p.get("id") == product_id:
            return p
    return None


def product_unlock_key(product_id: str) -> str:
    return f"product:{product_id}"
