"""Saju engine — sajupy pillars + product analysis (용신/대운/오행 처방)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

STEM_ELEMENT: dict[str, str] = {
    "甲": "wood", "乙": "wood", "丙": "fire", "丁": "fire", "戊": "earth",
    "己": "earth", "庚": "metal", "辛": "metal", "壬": "water", "癸": "water",
}

BRANCH_ELEMENT: dict[str, str] = {
    "子": "water", "丑": "earth", "寅": "wood", "卯": "wood", "辰": "earth",
    "巳": "fire", "午": "fire", "未": "earth", "申": "metal", "酉": "metal",
    "戌": "earth", "亥": "water",
}

ELEMENT_KEYS = ("wood", "fire", "earth", "metal", "water")

ELEMENT_KO: dict[str, str] = {
    "wood": "목(木)", "fire": "화(火)", "earth": "토(土)",
    "metal": "금(金)", "water": "수(水)",
}

# Generates (생) relationships for simple 용신 hint
GENERATES: dict[str, str] = {
    "wood": "fire", "fire": "earth", "earth": "metal",
    "metal": "water", "water": "wood",
}

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

_YANG_STEMS = set("甲丙戊庚壬")

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

_DAEUN_NOTES = [
    "기반을 다지는 시기. 학습·자격·인맥에 투자하면 이후 10년이 수월해집니다.",
    "확장과 도전의 기운. 이직·사업·관계 모두 움직임이 커질 수 있습니다.",
    "수확과 정리의 흐름. 불필요한 것을 덜어내고 핵심에 집중하세요.",
    "변화와 전환의 문. 환경이 바뀌어도 중심을 지키면 득이 됩니다.",
    "안정과 회복. 건강·가정·재정 방어선을 보강하기 좋은 때입니다.",
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
class YongsinAdvice:
    element: str
    element_ko: str
    reason: str
    lifestyle: list[str] = field(default_factory=list)


@dataclass
class DaeunPeriod:
    start_age: int
    end_age: int
    label: str
    note: str
    is_current: bool = False


@dataclass
class SajuResult:
    pillars: Pillars
    day_master: str
    elements: dict[str, int]
    daily: DailyFortune
    time_assumed: bool = False
    weak_elements: list[str] = field(default_factory=list)
    strong_elements: list[str] = field(default_factory=list)
    yongsin: YongsinAdvice | None = None
    daeun: list[DaeunPeriod] = field(default_factory=list)
    # Multi-engine commercial-safe fact verification (optional)
    chart_facts: dict | None = None


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
    base = as_of.toordinal() * 31
    for ch in day_master:
        base = (base * 131 + ord(ch)) & 0x7FFFFFFF
    return base


def daily_fortune(day_master: str, as_of: date) -> DailyFortune:
    seed = _seed(day_master, as_of)
    summary = _SUMMARIES[seed % len(_SUMMARIES)]
    overall = 40 + (seed % 56)
    love = 40 + ((seed // 3) % 56)
    money = 40 + ((seed // 7) % 56)
    health = 40 + ((seed // 11) % 56)
    base_lucky = _DAY_MASTER_LUCKY.get(day_master, {"color": "청색", "direction": "동"})
    return DailyFortune(
        date=as_of,
        summary=summary,
        scores={"overall": overall, "love": love, "money": money, "health": health},
        lucky={
            "color": base_lucky["color"],
            "direction": base_lucky["direction"],
            "number": str(1 + (seed % 9)),
        },
    )


def analyze_elements(elements: dict[str, int]) -> tuple[list[str], list[str], YongsinAdvice]:
    """Simplified balancing: weakest elements need support (용신 힌트)."""
    ordered = sorted(ELEMENT_KEYS, key=lambda k: (elements.get(k, 0), k))
    weak = [e for e in ordered if elements.get(e, 0) == elements.get(ordered[0], 0)][:2]
    strong = sorted(ELEMENT_KEYS, key=lambda k: (-elements.get(k, 0), k))[:2]
    yong = weak[0]
    # lifestyle tips by element
    tips = {
        "wood": ["동쪽 방향 활동", "초록·청색 소품", "아침 산책·스트레칭"],
        "fire": ["남향 자리", "빨강·주황 포인트", "사교·발표 일정"],
        "earth": ["중앙·안정된 루틴", "노랑·베이지 인테리어", "규칙적 식사"],
        "metal": ["서쪽·정리 정돈", "흰색·메탈 소품", "결단이 필요한 일 처리"],
        "water": ["북쪽·휴식", "검정·남색 아이템", "수분·명상·독서"],
    }
    reason = (
        f"{ELEMENT_KO[yong]} 기운이 상대적으로 약합니다. "
        f"일간 균형을 위해 {ELEMENT_KO[yong]}을(를) 보강하는 선택이 도움이 됩니다."
    )
    advice = YongsinAdvice(
        element=yong,
        element_ko=ELEMENT_KO[yong],
        reason=reason,
        lifestyle=tips.get(yong, []),
    )
    return weak, strong, advice


def compute_daeun(
    solar_date: date,
    gender: str,
    year_stem: str,
    as_of: date | None = None,
) -> list[DaeunPeriod]:
    """Simplified 대운: 10-year blocks from ~age 3 (entertainment / product MVP)."""
    today = as_of or date.today()
    age = today.year - solar_date.year - (
        (today.month, today.day) < (solar_date.month, solar_date.day)
    )
    year_yang = year_stem in _YANG_STEMS
    # classic: 양남/음녀 순행, 음남/양녀 역행 — used only for label flavor
    forward = (gender == "male" and year_yang) or (gender == "female" and not year_yang)
    direction = "순행" if forward else "역행"
    periods: list[DaeunPeriod] = []
    start = 3
    for i in range(8):
        s = start + i * 10
        e = s + 9
        note = _DAEUN_NOTES[(i + (0 if forward else 3)) % len(_DAEUN_NOTES)]
        periods.append(
            DaeunPeriod(
                start_age=s,
                end_age=e,
                label=f"{s}~{e}세 ({direction})",
                note=note,
                is_current=s <= age <= e,
            )
        )
    return periods


class SajuEngine:
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
        raw = self._calculate_pillars(
            solar_date, hour, minute, time_assumed=time_assumed
        )
        pillars = Pillars(
            year=StemBranch(stem=raw["year_stem"], branch=raw["year_branch"]),
            month=StemBranch(stem=raw["month_stem"], branch=raw["month_branch"]),
            day=StemBranch(stem=raw["day_stem"], branch=raw["day_branch"]),
            hour=(
                StemBranch(stem=raw["hour_stem"], branch=raw["hour_branch"])
                if raw.get("hour_stem") and raw.get("hour_branch")
                else None
            ),
        )
        # When time assumed, still keep hour pillar for engine completeness
        if pillars.hour is None and raw.get("hour_stem"):
            pillars = Pillars(
                year=pillars.year,
                month=pillars.month,
                day=pillars.day,
                hour=StemBranch(stem=raw["hour_stem"], branch=raw["hour_branch"]),
            )
        day_master = pillars.day.stem
        elements = _count_elements(pillars)
        target = as_of or date.today()
        daily = daily_fortune(day_master, target)
        weak, strong, yongsin = analyze_elements(elements)
        daeun = compute_daeun(solar_date, gender, pillars.year.stem, target)
        return SajuResult(
            pillars=pillars,
            day_master=day_master,
            elements=elements,
            daily=daily,
            time_assumed=time_assumed,
            weak_elements=weak,
            strong_elements=strong,
            yongsin=yongsin,
            daeun=daeun,
            chart_facts=raw.get("chart_facts"),
        )

    def _calculate_pillars(
        self,
        solar_date: date,
        hour: int,
        minute: int,
        *,
        time_assumed: bool = False,
    ) -> dict[str, Any]:
        """Multi-engine commercial-safe pillars (sajupy primary + lunar_python check)."""
        try:
            from app.services.engines.merge import compute_chart_facts, facts_to_raw_dict

            facts = compute_chart_facts(
                solar_date,
                hour,
                minute,
                utc_offset=9,
                time_unknown=time_assumed,
            )
            return facts_to_raw_dict(facts)
        except Exception:
            # Fallback: sajupy only (still MIT)
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


def compatibility_score(
    a: SajuResult,
    b: SajuResult,
) -> dict[str, Any]:
    """Simple day-master + element complementarity score (0–100)."""
    score = 55
    if STEM_ELEMENT.get(a.day_master) == GENERATES.get(STEM_ELEMENT.get(b.day_master, "")):
        score += 18
    if STEM_ELEMENT.get(b.day_master) == GENERATES.get(STEM_ELEMENT.get(a.day_master, "")):
        score += 18
    # complementary weak/strong
    if set(a.weak_elements) & set(b.strong_elements):
        score += 8
    if set(b.weak_elements) & set(a.strong_elements):
        score += 8
    if a.day_master == b.day_master:
        score += 5
    score = max(35, min(98, score))
    if score >= 80:
        summary = "서로를 북돋우는 흐름이 강합니다. 신뢰를 쌓기 좋은 궁합입니다."
    elif score >= 65:
        summary = "무난하고 보완적인 관계. 소통 노력 시 시너지가 커집니다."
    elif score >= 50:
        summary = "차이에서 성장이 생깁니다. 존중과 경계 설정이 중요합니다."
    else:
        summary = "기질 차이가 큽니다. 합의와 배려로 균형을 맞춰 가세요."
    return {
        "score": score,
        "summary": summary,
        "a_day_master": a.day_master,
        "b_day_master": b.day_master,
    }
