"""
Merge commercially-safe engines into one fact chart.

Policy:
- Primary: sajupy (MIT) when available
- Cross-check: lunar_python / 6tail (MIT)
- On disagreement: keep primary, attach warnings (never silent overwrite)
- Only MIT/Apache/BSD-class adapters may be registered here
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.engines.base import ChartFacts, EngineChart, PillarFact
from app.services.engines.lunar_python_adapter import (
    ENGINE_META as LUNAR_META,
)
from app.services.engines.lunar_python_adapter import compute_lunar_python
from app.services.engines.sajupy_adapter import ENGINE_META as SAJUPY_META
from app.services.engines.sajupy_adapter import compute_sajupy

# Registry of allowed commercial-safe engines (document in LICENSES)
COMMERCIAL_SAFE_ENGINES = [
    {
        **SAJUPY_META,
        "role": "primary",
        "notes": "Korean manseryeok-style pillars; primary for FO product.",
    },
    {
        **LUNAR_META,
        "role": "cross_check",
        "notes": "6tail lunar-python eight characters; cross-check only.",
    },
]


def compute_chart_facts(
    solar_date: date,
    hour: int,
    minute: int,
    *,
    utc_offset: int = 9,
    time_unknown: bool = False,
) -> ChartFacts:
    """Run all safe engines and merge."""
    h = 12 if time_unknown else hour
    m = 0 if time_unknown else minute

    charts: list[EngineChart] = [
        compute_sajupy(solar_date, h, m, utc_offset=utc_offset),
        compute_lunar_python(solar_date, h, m),
    ]

    ok_charts = [c for c in charts if c.ok]
    warnings: list[str] = []
    for c in charts:
        if not c.ok:
            warnings.append(f"{c.engine_id} unavailable: {c.error}")

    if not ok_charts:
        raise RuntimeError(
            "No commercial-safe saju engine available. Install sajupy and/or lunar_python."
        )

    # Prefer sajupy as primary if ok
    primary = next((c for c in ok_charts if c.engine_id == "sajupy"), ok_charts[0])

    agreement = True
    if len(ok_charts) >= 2:
        sig0 = ok_charts[0].signature()
        for c in ok_charts[1:]:
            if c.signature() != sig0:
                agreement = False
                warnings.append(
                    f"Pillar mismatch: {ok_charts[0].engine_id}={ok_charts[0].signature()} "
                    f"vs {c.engine_id}={c.signature()} — using primary={primary.engine_id}"
                )

    # Hour pillar may be None when time unknown — strip hour compare noise
    hour_fact = primary.hour
    if time_unknown:
        hour_fact = None
        # if engines still returned hour, note assumed noon
        warnings.append("time_unknown: hour pillar assumed noon for calculation; hour display may be hidden")

    licenses = [
        {
            "engine_id": e["engine_id"],
            "license": e["license"],
            "package": e["package"],
            "homepage": e.get("homepage", ""),
            "commercial_use": str(e.get("commercial_use", True)),
            "role": e.get("role", ""),
        }
        for e in COMMERCIAL_SAFE_ENGINES
    ]

    return ChartFacts(
        primary_engine=primary.engine_id,
        year=primary.year,
        month=primary.month,
        day=primary.day,
        hour=hour_fact if not time_unknown else primary.hour,
        day_master=primary.day.stem,
        engines=charts,
        agreement=agreement,
        warnings=warnings,
        licenses=licenses,
    )


def facts_to_raw_dict(facts: ChartFacts) -> dict[str, Any]:
    """Shape compatible with legacy SajuEngine._calculate_pillars output."""
    h_stem = facts.hour.stem if facts.hour else "戊"
    h_branch = facts.hour.branch if facts.hour else "午"
    return {
        "year_stem": facts.year.stem,
        "year_branch": facts.year.branch,
        "month_stem": facts.month.stem,
        "month_branch": facts.month.branch,
        "day_stem": facts.day.stem,
        "day_branch": facts.day.branch,
        "hour_stem": h_stem,
        "hour_branch": h_branch,
        "chart_facts": facts.as_dict(),
    }
