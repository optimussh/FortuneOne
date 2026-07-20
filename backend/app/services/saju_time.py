"""Saju 2-hour time branches (시) and form helpers."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

# (key, label_ko, representative_hour for engine)
# 시 = 2-hour units; mid-point hour used for pillar calculation
SAJU_HOURS: list[dict[str, Any]] = [
    {"key": "unknown", "label": "모름 (태어난 시간)", "hour": None},
    {"key": "zi", "label": "자시 (23:00–01:00)", "hour": 0},
    {"key": "chou", "label": "축시 (01:00–03:00)", "hour": 2},
    {"key": "yin", "label": "인시 (03:00–05:00)", "hour": 4},
    {"key": "mao", "label": "묘시 (05:00–07:00)", "hour": 6},
    {"key": "chen", "label": "진시 (07:00–09:00)", "hour": 8},
    {"key": "si", "label": "사시 (09:00–11:00)", "hour": 10},
    {"key": "wu", "label": "오시 (11:00–13:00)", "hour": 12},
    {"key": "wei", "label": "미시 (13:00–15:00)", "hour": 14},
    {"key": "shen", "label": "신시 (15:00–17:00)", "hour": 16},
    {"key": "you", "label": "유시 (17:00–19:00)", "hour": 18},
    {"key": "xu", "label": "술시 (19:00–21:00)", "hour": 20},
    {"key": "hai", "label": "해시 (21:00–23:00)", "hour": 22},
]

RELATION_LABELS = [
    "본인",
    "엄마",
    "아빠",
    "배우자",
    "애인",
    "자녀",
    "친구",
    "기타",
]


def hour_from_slot(time_slot: str) -> tuple[Optional[int], bool]:
    """Return (hour, time_unknown)."""
    for item in SAJU_HOURS:
        if item["key"] == time_slot:
            if item["hour"] is None:
                return None, True
            return int(item["hour"]), False
    return None, True


def slot_from_hour(hour: Optional[int], time_unknown: bool) -> str:
    if time_unknown or hour is None:
        return "unknown"
    # map to nearest even 2h branch
    for item in SAJU_HOURS:
        if item["hour"] is not None and abs(item["hour"] - hour) <= 1:
            return item["key"]
    # exact match on even hours
    for item in SAJU_HOURS:
        if item["hour"] == hour:
            return item["key"]
    return "unknown"


def ymd_to_date(year: int, month: int, day: int) -> date:
    return date(year, month, day)
