"""
lunar_python (6tail) adapter — MIT
https://github.com/6tail/lunar-python
Package: lunar_python on PyPI
"""

from __future__ import annotations

from datetime import date

from app.services.engines.base import EngineChart, PillarFact, split_pair


ENGINE_META = {
    "engine_id": "lunar_python",
    "license": "MIT",
    "package": "lunar_python>=1.3.0",
    "homepage": "https://github.com/6tail/lunar-python",
    "commercial_use": True,
}


def compute_lunar_python(
    solar_date: date,
    hour: int,
    minute: int,
) -> EngineChart:
    try:
        from lunar_python import Solar
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
            error=f"lunar_python not installed: {exc}",
        )

    try:
        solar = Solar.fromYmdHms(
            solar_date.year,
            solar_date.month,
            solar_date.day,
            int(hour),
            int(minute),
            0,
        )
        lunar = solar.getLunar()
        ec = lunar.getEightChar()
        year = split_pair(ec.getYear())
        month = split_pair(ec.getMonth())
        day = split_pair(ec.getDay())
        hour_p = split_pair(ec.getTime())
        return EngineChart(
            engine_id=ENGINE_META["engine_id"],
            license=ENGINE_META["license"],
            package=ENGINE_META["package"],
            year=year,
            month=month,
            day=day,
            hour=hour_p,
            extra={
                "homepage": ENGINE_META["homepage"],
                "lunar": str(lunar),
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
