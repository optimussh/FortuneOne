"""sajupy adapter — MIT (https://github.com/0ssw1/sajupy)."""

from __future__ import annotations

from datetime import date

from app.services.engines.base import EngineChart, PillarFact


ENGINE_META = {
    "engine_id": "sajupy",
    "license": "MIT",
    "package": "sajupy>=0.2.0",
    "homepage": "https://github.com/0ssw1/sajupy",
    "commercial_use": True,
}


def compute_sajupy(
    solar_date: date,
    hour: int,
    minute: int,
    *,
    utc_offset: int = 9,
) -> EngineChart:
    try:
        from sajupy import calculate_saju
    except ImportError as exc:
        return EngineChart(
            engine_id=ENGINE_META["engine_id"],
            license=ENGINE_META["license"],
            package=ENGINE_META["package"],
            year=PillarFact("—", "—"),
            month=PillarFact("—", "—"),
            day=PillarFact("—", "—"),
            hour=None,
            ok=False,
            error=f"sajupy not installed: {exc}",
        )

    try:
        raw = calculate_saju(
            solar_date.year,
            solar_date.month,
            solar_date.day,
            hour,
            minute,
            utc_offset=utc_offset,
        )
        hour_p = None
        if raw.get("hour_stem") and raw.get("hour_branch"):
            hour_p = PillarFact(stem=raw["hour_stem"], branch=raw["hour_branch"])
        return EngineChart(
            engine_id=ENGINE_META["engine_id"],
            license=ENGINE_META["license"],
            package=ENGINE_META["package"],
            year=PillarFact(raw["year_stem"], raw["year_branch"]),
            month=PillarFact(raw["month_stem"], raw["month_branch"]),
            day=PillarFact(raw["day_stem"], raw["day_branch"]),
            hour=hour_p,
            extra={
                "homepage": ENGINE_META["homepage"],
                "birth_date": raw.get("birth_date"),
                "zi_time_type": raw.get("zi_time_type"),
            },
            ok=True,
        )
    except Exception as exc:
        return EngineChart(
            engine_id=ENGINE_META["engine_id"],
            license=ENGINE_META["license"],
            package=ENGINE_META["package"],
            year=PillarFact("—", "—"),
            month=PillarFact("—", "—"),
            day=PillarFact("—", "—"),
            hour=None,
            ok=False,
            error=str(exc),
        )
