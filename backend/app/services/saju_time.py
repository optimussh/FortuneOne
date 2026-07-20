"""Saju 12-시진 (2-hour) table — KST common practice (30-min offset style)."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

# key, short label, full range label, representative hour for sajupy engine
# Ranges: 자시 23:30–01:29 … (widely used KST table; not true solar time correction)
SAJU_HOURS: list[dict[str, Any]] = [
    {
        "key": "unknown",
        "label": "모름 (태어난 시간)",
        "label_short": "모름",
        "range": None,
        "hour": None,
        "meaning": "시주 미상 — 정오(오시) 가정으로 계산할 수 있음",
    },
    {
        "key": "zi",
        "label": "자시 (子) 23:30–01:29",
        "label_short": "자시",
        "range": "23:30–01:29",
        "hour": 0,
        "meaning": "하루가 시작되는 기운, 음이 극에 달하고 양이 싹트는 시간",
    },
    {
        "key": "chou",
        "label": "축시 (丑) 01:30–03:29",
        "label_short": "축시",
        "range": "01:30–03:29",
        "hour": 2,
        "meaning": "만물이 숨을 죽이고 내면 에너지를 기르는 깊은 밤",
    },
    {
        "key": "yin",
        "label": "인시 (寅) 03:30–05:29",
        "label_short": "인시",
        "range": "03:30–05:29",
        "hour": 4,
        "meaning": "동이 틀 무렵, 만물이 깨어나는 시간",
    },
    {
        "key": "mao",
        "label": "묘시 (卯) 05:30–07:29",
        "label_short": "묘시",
        "range": "05:30–07:29",
        "hour": 6,
        "meaning": "해가 떠오르는 아침, 활력이 도는 시간",
    },
    {
        "key": "chen",
        "label": "진시 (辰) 07:30–09:29",
        "label_short": "진시",
        "range": "07:30–09:29",
        "hour": 8,
        "meaning": "오전 활기, 활동이 본격화되는 때",
    },
    {
        "key": "si",
        "label": "사시 (巳) 09:30–11:29",
        "label_short": "사시",
        "range": "09:30–11:29",
        "hour": 10,
        "meaning": "햇살이 뜨거워지기 시작하는 오전",
    },
    {
        "key": "wu",
        "label": "오시 (午) 11:30–13:29",
        "label_short": "오시",
        "range": "11:30–13:29",
        "hour": 12,
        "meaning": "해가 가장 높은 정오, 양의 기운이 극에 달함",
    },
    {
        "key": "wei",
        "label": "미시 (未) 13:30–15:29",
        "label_short": "미시",
        "range": "13:30–15:29",
        "hour": 14,
        "meaning": "해가 서서히 기울기 시작하는 오후",
    },
    {
        "key": "shen",
        "label": "신시 (申) 15:30–17:29",
        "label_short": "신시",
        "range": "15:30–17:29",
        "hour": 16,
        "meaning": "기운이 수렴하기 시작하는 때",
    },
    {
        "key": "you",
        "label": "유시 (酉) 17:30–19:29",
        "label_short": "유시",
        "range": "17:30–19:29",
        "hour": 18,
        "meaning": "해가 지고 노을이 지는 저녁",
    },
    {
        "key": "xu",
        "label": "술시 (戌) 19:30–21:29",
        "label_short": "술시",
        "range": "19:30–21:29",
        "hour": 20,
        "meaning": "어둠이 내리고 하루를 마무리하는 시간",
    },
    {
        "key": "hai",
        "label": "해시 (亥) 21:30–23:29",
        "label_short": "해시",
        "range": "21:30–23:29",
        "hour": 22,
        "meaning": "하루가 끝나고 휴식·잠에 드는 밤",
    },
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
    """Return (representative_hour, time_unknown)."""
    for item in SAJU_HOURS:
        if item["key"] == time_slot:
            if item["hour"] is None:
                return None, True
            return int(item["hour"]), False
    return None, True


def slot_from_hour(hour: Optional[int], time_unknown: bool) -> str:
    if time_unknown or hour is None:
        return "unknown"
    for item in SAJU_HOURS:
        if item["hour"] is not None and abs(item["hour"] - hour) <= 1:
            return item["key"]
    for item in SAJU_HOURS:
        if item["hour"] == hour:
            return item["key"]
    return "unknown"


def ymd_to_date(year: int, month: int, day: int) -> date:
    return date(year, month, day)
