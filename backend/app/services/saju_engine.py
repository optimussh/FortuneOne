"""Saju (four pillars) engine — wraps sajupy; daily fortune is rule-based."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


STEM_ELEMENT: dict[str, str] = {
    "甲": "wood",
    "乙": "wood",
    "丙": "fire",
    "丁": "fire",
    "戊": "earth",
    "己": "earth",
    "庚": "metal",
    "辛": "metal",
    "壬": "water",
    "癸": "water",
}

BRANCH_ELEMENT: dict[str, str] = {
    "子": "water",
    "丑": "earth",
    "寅": "wood",
    "卯": "wood",
    "辰": "earth",
    "巳": "fire",
    "午": "fire",
    "未": "earth",
    "申": "metal",
    "酉": "metal",
    "戌": "earth",
    "亥": "water",
}

ELEMENT_KEYS = ("wood", "fire", "earth", "metal", "water")

# day_master → lucky defaults
_DAY_MASTER_LUCKY: dict[str, dict[str, str]] = {
    "甲": {"color": "청색", "direction": "동"},
    "乙": {"color": "녹색", "direction": "동남"},
    "丙": {"color": "적색", "direction": "남"},
    "丁": {"color": "자색", "direction": "남"},
    "戊": {"color": "황색", "direction": "중앙"},
    "己": {"color": "갈색", "direction": "서남"},
    "庚": {"color": "백색", "direction": "서"},
    "辛": {"color": "은색", "direction": "서북"},
    "壬": {"color": "흑색", "direction": "북"},
    "癸": {"color": "남색", "direction": "북"},
}

_SUMMARIES = [
    "안정 속에 기회가 스며드는 하루입니다. 무리한 추진보다 정리와 조율이 성과로 이어집니다.",
    "대인 관계에서 좋은 기운이 돕습니다. 솔직한 대화가 오해를 풀고 협력을 만듭니다.",
    "재물·계약 관련 결정에 신중함이 필요합니다. 작은 지출 점검은 도움이 됩니다.",
    "활력이 올라가는 날입니다. 운동이나 산책으로 몸과 마음을 가볍게 하세요.",
    "집중력이 빛나는 하루입니다. 미뤄 둔 일을 끝내기 좋습니다.",
    "감정의 파고가 있을 수 있습니다. 휴식과 호흡으로 리듬을 되찾으세요.",
    "새로운 아이디어가 떠오르기 쉽습니다. 메모해 두고 저녁에 다시 검토하세요.",
    "주변의 조언을 열린 마음으로 들으면 길이 보입니다. 겸손이 운을 키웁니다.",
]


@dataclass
class StemBranch:
    stem: str
    branch: str


@dataclass
class Pillars:
    year: StemBranch
    month: StemBranch
    day: StemBranch
    hour: StemBranch | None


@dataclass
class DailyFortune:
    date: date
    summary: str
    scores: dict[str, int]
    lucky: dict[str, str]


@dataclass
class SajuResult:
    pillars: Pillars
    day_master: str
    elements: dict[str, int]
    daily: DailyFortune
    time_assumed: bool = False


def _count_elements(pillars: Pillars) -> dict[str, int]:
    counts = {k: 0 for k in ELEMENT_KEYS}
    pairs: list[StemBranch] = [pillars.year, pillars.month, pillars.day]
    if pillars.hour is not None:
        pairs.append(pillars.hour)
    for p in pairs:
        se = STEM_ELEMENT.get(p.stem)
        be = BRANCH_ELEMENT.get(p.branch)
        if se:
            counts[se] += 1
        if be:
            counts[be] += 1
    return counts


def _seed(day_master: str, as_of: date) -> int:
    """Deterministic non-crypto seed from day master + calendar day."""
    base = as_of.toordinal() * 31
    for ch in day_master:
        base = (base * 131 + ord(ch)) & 0x7FFFFFFF
    return base


def daily_fortune(day_master: str, as_of: date) -> DailyFortune:
    seed = _seed(day_master, as_of)
    summary = _SUMMARIES[seed % len(_SUMMARIES)]
    # Spread scores in a readable 40–95 band, deterministic per category
    overall = 40 + (seed % 56)
    love = 40 + ((seed // 3) % 56)
    money = 40 + ((seed // 7) % 56)
    health = 40 + ((seed // 11) % 56)
    # Slight daily rotation of lucky color/direction; fallback uses day_master table
    colors = ["청색", "적색", "황색", "백색", "흑색", "녹색", "자색", "금색"]
    directions = ["동", "서", "남", "북", "동남", "서북", "서남", "동북"]
    base_lucky = _DAY_MASTER_LUCKY.get(day_master, {"color": "청색", "direction": "동"})
    lucky = {
        "color": colors[(seed + ord(day_master[0])) % len(colors)] if day_master else base_lucky["color"],
        "direction": directions[(seed // 5) % len(directions)],
    }
    return DailyFortune(
        date=as_of,
        summary=summary,
        scores={
            "overall": overall,
            "love": love,
            "money": money,
            "health": health,
        },
        lucky=lucky,
    )


class SajuEngine:
    """Public engine interface. Library imports stay inside this module."""

    def calculate(
        self,
        solar_date: date,
        hour: int,
        minute: int,
        gender: str,
        *,
        as_of: date | None = None,
        time_assumed: bool = False,
    ) -> SajuResult:
        # gender reserved for future 대운 direction; unused in MVP daily rules
        _ = gender

        raw = self._calculate_pillars(solar_date, hour, minute)
        pillars = Pillars(
            year=StemBranch(stem=raw["year_stem"], branch=raw["year_branch"]),
            month=StemBranch(stem=raw["month_stem"], branch=raw["month_branch"]),
            day=StemBranch(stem=raw["day_stem"], branch=raw["day_branch"]),
            hour=StemBranch(stem=raw["hour_stem"], branch=raw["hour_branch"]),
        )
        day_master = pillars.day.stem
        elements = _count_elements(pillars)
        target = as_of or date.today()
        daily = daily_fortune(day_master, target)
        return SajuResult(
            pillars=pillars,
            day_master=day_master,
            elements=elements,
            daily=daily,
            time_assumed=time_assumed,
        )

    def _calculate_pillars(
        self, solar_date: date, hour: int, minute: int
    ) -> dict[str, Any]:
        try:
            from sajupy import calculate_saju
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("sajupy is not installed") from exc

        try:
            return calculate_saju(
                solar_date.year,
                solar_date.month,
                solar_date.day,
                hour,
                minute,
                utc_offset=9,
            )
        except Exception as exc:
            raise ValueError(f"사주 계산 실패: {exc}") from exc
