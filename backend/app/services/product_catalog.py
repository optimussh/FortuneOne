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


def reload_catalog() -> dict[str, Any]:
    """Clear cache after polish/regenerate."""
    load_catalog.cache_clear()
    return load_catalog()


def _enrich(p: dict[str, Any]) -> dict[str, Any]:
    try:
        from app.data.hit_product_copy import apply_hit_copy

        return apply_hit_copy(p)
    except Exception:
        return p


def list_products(
    category_id: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    items = [_enrich(dict(p)) for p in (load_catalog().get("products") or [])]
    if category_id:
        items = [p for p in items if p.get("category_id") == category_id]
    if q:
        ql = q.strip().lower()
        if ql:
            def _match(p: dict[str, Any]) -> bool:
                blob = " ".join(
                    [
                        str(p.get("title") or ""),
                        str(p.get("subtitle") or ""),
                        str(p.get("category_label") or ""),
                        " ".join(p.get("for_whom") or []),
                        " ".join(p.get("intro_blurbs") or [])[:400],
                    ]
                ).lower()
                return ql in blob

            items = [p for p in items if _match(p)]
    return items


def get_product(product_id: str) -> dict[str, Any] | None:
    for p in load_catalog().get("products") or []:
        if p.get("id") == product_id:
            return _enrich(dict(p))
    return None


def recommend_products(limit: int = 8) -> list[dict[str, Any]]:
    """Hit products first, then one per major category."""
    from app.data.hit_product_copy import HIT_IDS

    all_p = list_products()
    by_id = {p["id"]: p for p in all_p}
    out: list[dict[str, Any]] = []
    for hid in HIT_IDS:
        if hid in by_id and by_id[hid] not in out:
            out.append(by_id[hid])
        if len(out) >= limit:
            return out[:limit]
    # fill by category diversity
    seen_cat: set[str] = {p.get("category_id") or "" for p in out}
    for p in all_p:
        if p.get("is_free"):
            continue
        cat = p.get("category_id") or ""
        if cat in seen_cat and len(out) >= limit // 2:
            continue
        if p["id"] in {x["id"] for x in out}:
            continue
        out.append(p)
        seen_cat.add(cat)
        if len(out) >= limit:
            break
    return out[:limit]


def product_unlock_key(product_id: str) -> str:
    return f"product:{product_id}"
