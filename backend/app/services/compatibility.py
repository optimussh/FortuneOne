"""
Detailed saju compatibility report (self-generated text).

Uses day master + five elements + pillars; hour pillar when time known.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_engine import ELEMENT_KO, GENERATES, STEM_ELEMENT, SajuResult
from app.services.saju_report import STEM_NATURE, _elems, _pillars_line, _strong, _weak
from app.services.sipsung import ten_god

BRANCH_ELEM = {
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

# 지지 육합 (simplified pairs)
BRANCH_HAP = {
    "子": "丑",
    "丑": "子",
    "寅": "亥",
    "亥": "寅",
    "卯": "戌",
    "戌": "卯",
    "辰": "酉",
    "酉": "辰",
    "巳": "申",
    "申": "巳",
    "午": "未",
    "未": "午",
}

# 충 (opposite branches)
BRANCH_CHONG = {
    "子": "午",
    "午": "子",
    "丑": "未",
    "未": "丑",
    "寅": "申",
    "申": "寅",
    "卯": "酉",
    "酉": "卯",
    "辰": "戌",
    "戌": "辰",
    "巳": "亥",
    "亥": "巳",
}


def _rel_day_masters(a_dm: str, b_dm: str) -> tuple[str, int, str]:
    """Return (label, score_delta, explanation)."""
    ae = STEM_ELEMENT.get(a_dm, "earth")
    be = STEM_ELEMENT.get(b_dm, "earth")
    if ae == be:
        return (
            "비화(같은 오행)",
            6,
            f"일간 {a_dm}·{b_dm}은 같은 {ELEMENT_KO[ae]} 기운이라 공감은 쉽지만, "
            f"같은 약점이 겹칠 수 있어 역할 분담이 중요합니다.",
        )
    if GENERATES.get(ae) == be:
        return (
            "A가 B를 생(生)",
            16,
            f"{a_dm}({ELEMENT_KO[ae]})이 {b_dm}({ELEMENT_KO[be]})을 돕는 흐름입니다. "
            f"A가 에너지를 주고 B가 받는 구조라, 배려와 감사의 균형이 길합니다.",
        )
    if GENERATES.get(be) == ae:
        return (
            "B가 A를 생(生)",
            16,
            f"{b_dm}({ELEMENT_KO[be]})이 {a_dm}({ELEMENT_KO[ae]})을 돕는 흐름입니다. "
            f"B의 지지가 A의 성장으로 이어지기 쉽습니다.",
        )
    # control
    CTRL = {"wood": "earth", "earth": "water", "water": "fire", "fire": "metal", "metal": "wood"}
    if CTRL.get(ae) == be:
        return (
            "A가 B를 극(克)",
            4,
            f"{a_dm} 쪽이 {b_dm} 쪽을 누르는 기운이 있어 주도권 다툼이 날 수 있습니다. "
            f"지시보다 제안·합의 방식이 관계를 살립니다.",
        )
    if CTRL.get(be) == ae:
        return (
            "B가 A를 극(克)",
            4,
            f"{b_dm} 쪽이 {a_dm} 쪽을 누르는 기운이 있습니다. "
            f"존중 언어와 경계가 있으면 오히려 성장 동력이 됩니다.",
        )
    return (
        "간접 관계",
        8,
        f"일간 {a_dm}·{b_dm}은 직접 생극보다 환경·시기로 맞춰 가는 타입입니다.",
    )


def _branch_note(ba: str, bb: str, label: str) -> tuple[int, str]:
    if not ba or not bb or ba == "—" or bb == "—":
        return 0, f"{label}: 시주 미상으로 지지 비교를 생략합니다."
    if ba == bb:
        return 5, f"{label}: 같은 지지({ba})로 생활 리듬이 닮을 수 있습니다."
    if BRANCH_HAP.get(ba) == bb:
        return 10, f"{label}: {ba}–{bb} 합(合)에 가까워 정이 붙기 쉽습니다."
    if BRANCH_CHONG.get(ba) == bb:
        return -6, f"{label}: {ba}–{bb} 충(沖) 기운 — 충돌 후 재합의가 필요합니다."
    ea, eb = BRANCH_ELEM.get(ba), BRANCH_ELEM.get(bb)
    if ea and eb and ea == eb:
        return 4, f"{label}: 지지 오행이 같아 취향·환경 선호가 비슷할 수 있습니다."
    if ea and eb and GENERATES.get(ea) == eb:
        return 6, f"{label}: 지지상 생하는 흐름이 있어 실생활 협력이 수월할 수 있습니다."
    return 2, f"{label}: {ba}·{bb} — 큰 충돌보다 조율이 필요한 조합입니다."


def _person_block(
    result: SajuResult,
    *,
    name: str,
    gender: str,
    calendar_type: str,
    birth_input: str,
    solar_used: str,
    time_text: str,
    time_unknown: bool,
) -> dict[str, Any]:
    g = "남" if gender == "male" else "여"
    cal = "양력" if calendar_type != "lunar" else "음력"
    return {
        "display_name": name or "상대",
        "gender": gender,
        "gender_ko": g,
        "calendar_type": calendar_type,
        "calendar_label": cal,
        "birth_input": birth_input,
        "solar_used": solar_used,
        "time_text": time_text,
        "time_unknown": time_unknown,
        "day_master": result.day_master,
        "day_master_nature": STEM_NATURE.get(result.day_master, ""),
        "pillars_line": _pillars_line(result),
        "elements": result.elements,
        "elements_line": _elems(result),
        "strong": _strong(result),
        "weak": _weak(result),
        "pillars": {
            "year": {"stem": result.pillars.year.stem, "branch": result.pillars.year.branch},
            "month": {"stem": result.pillars.month.stem, "branch": result.pillars.month.branch},
            "day": {"stem": result.pillars.day.stem, "branch": result.pillars.day.branch},
            "hour": (
                {
                    "stem": result.pillars.hour.stem,
                    "branch": result.pillars.hour.branch,
                }
                if result.pillars.hour
                else None
            ),
        },
    }


def build_compatibility(
    a: SajuResult,
    b: SajuResult,
    *,
    a_meta: dict[str, Any],
    b_meta: dict[str, Any],
) -> dict[str, Any]:
    rel_label, dm_delta, dm_explain = _rel_day_masters(a.day_master, b.day_master)

    # element complement
    el_delta = 0
    el_notes = []
    if set(a.weak_elements) & set(b.strong_elements):
        el_delta += 10
        el_notes.append(
            f"A의 약한 오행({', '.join(ELEMENT_KO.get(x, x) for x in a.weak_elements)})을 "
            f"B의 강한 기운이 보완할 수 있습니다."
        )
    if set(b.weak_elements) & set(a.strong_elements):
        el_delta += 10
        el_notes.append(
            f"B의 약한 오행을 A가 메워 주는 구조입니다."
        )
    if not el_notes:
        el_notes.append("오행 보완은 중간 수준입니다. 생활 습관·역할 분담으로 균형을 만드세요.")
        el_delta += 4

    # pillar branches
    d_delta, d_note = _branch_note(a.pillars.day.branch, b.pillars.day.branch, "일지")
    y_delta, y_note = _branch_note(a.pillars.year.branch, b.pillars.year.branch, "년지")
    m_delta, m_note = _branch_note(a.pillars.month.branch, b.pillars.month.branch, "월지")
    h_delta, h_note = 0, "시지: 한쪽 이상 시간 모름 — 시주 비교 생략."
    if a.pillars.hour and b.pillars.hour:
        h_delta, h_note = _branch_note(
            a.pillars.hour.branch, b.pillars.hour.branch, "시지"
        )
    elif a.pillars.hour or b.pillars.hour:
        h_note = "시지: 한 쪽만 시주가 있어 부분 참고만 가능합니다."

    # mutual ten gods flavor (B as seen from A day master)
    god_ab = ten_god(a.day_master, b.day_master)
    god_ba = ten_god(b.day_master, a.day_master)

    raw = 48 + dm_delta + el_delta + d_delta + y_delta + m_delta // 2 + h_delta
    # same day master slight
    if a.day_master == b.day_master:
        raw += 4
    score = max(28, min(97, raw))

    if score >= 85:
        grade = "매우 좋음"
        tone = "서로 밀어 주는 힘이 큰 편"
    elif score >= 72:
        grade = "좋음"
        tone = "신뢰와 성장이 기대되는 편"
    elif score >= 58:
        grade = "무난·보완"
        tone = "노력하면 시너지가 나는 편"
    elif score >= 45:
        grade = "조율 필요"
        tone = "차이와 합의를 배워야 하는 편"
    else:
        grade = "신중"
        tone = "기질 차이가 커 의식적 배려가 필요한 편"

    a_name = a_meta.get("name") or a_meta.get("display_name") or "A"
    b_name = b_meta.get("name") or b_meta.get("display_name") or "B"

    summary = (
        f"{a_name}님({a.day_master})과 {b_name}님({b.day_master})의 종합 궁합은 "
        f"{score}점 · {grade}입니다. {tone}입니다. "
        f"일간 관계: {rel_label}. "
        f"(점수는 참고 지표이며 절대적 운명이 아닙니다.)"
    )

    love_body = (
        f"연애·애정 면에서 {rel_label} 구조가 기본 톤을 만듭니다. {dm_explain} "
        f"A 입장에서 B 일간은 십성상 ‘{god_ab}’에 가깝고, "
        f"B 입장에서 A는 ‘{god_ba}’로 느껴질 수 있습니다. "
        f"표현 방식: {a_name}은 {STEM_NATURE.get(a.day_master, '균형')} 성향, "
        f"{b_name}은 {STEM_NATURE.get(b.day_master, '균형')} 성향이니 "
        f"말의 속도와 온도를 맞추는 것이 호감 유지에 중요합니다. "
        f"{d_note} "
        f"함께 있을 때 작은 루틴(식사, 산책, 주 1회 대화)을 정해 두면 정이 쌓입니다."
    )

    comm_body = (
        f"소통: {y_note} {m_note} "
        f"의견 충돌 시 ‘사실 → 감정 → 요청’ 순으로 말하면 오해가 줍니다. "
        f"오행상 A 강점 {_strong(a)}, B 강점 {_strong(b)}이므로 "
        f"결정은 강점이 있는 쪽이 초안을 잡고, 약한 영역({_weak(a)} / {_weak(b)})은 "
        f"상대 의견을 먼저 듣는 편이 효율적입니다."
    )

    daily_body = (
        f"생활·가정: {h_note} "
        f"시간 리듬이 다르면 수면·식사 시간 합의가 관계를 좌우합니다. "
        f"금전은 공동 목표 1개(여행, 저축 등)만 공유하고 나머지는 자율로 두면 마찰이 적습니다. "
        f"공간 배치·색은 서로의 용신·선호를 존중하되, 한쪽 취향으로 방을 독점하지 마세요."
    )

    caution_body = (
        f"주의: 점수 {score}점이라도 갈등 없는 관계는 없습니다. "
        f"특히 일간 극·지지 충이 있으면 말투·속도 차이가 자존심 문제로 번질 수 있습니다. "
        f"큰 결정(동거, 결혼, 동업, 대출) 전에는 3일 이상 숙고 규칙을 두세요. "
        f"이 리포트는 엔터테인먼트·자기 성찰용이며 법적·의학적 조언이 아닙니다."
    )

    practice_body = (
        f"실천 제안\n"
        f"1) 주 1회 30분 ‘감정보다 일정·역할’ 대화\n"
        f"2) 서로의 약한 오행을 보완하는 활동 1가지 "
        f"(A 약: {_weak(a)} / B 약: {_weak(b)})\n"
        f"3) 칭찬 비율 3:1 유지 (지적 1회당 인정 3회)\n"
        f"4) 다툴 때 24시간 내 재대화 약속\n"
        f"5) 공동 추억 만들기(짧은 여행·취미) 분기 1회"
    )

    sections = [
        {"id": "overall", "title": "종합 한 줄", "body": summary},
        {"id": "day_master", "title": "일간 관계", "body": f"【{rel_label}】 {dm_explain}"},
        {
            "id": "elements",
            "title": "오행 보완",
            "body": " ".join(el_notes)
            + f" A 오행 {_elems(a)}. B 오행 {_elems(b)}.",
        },
        {"id": "love", "title": "연애·애정", "body": love_body},
        {"id": "communication", "title": "소통·갈등", "body": comm_body},
        {"id": "daily", "title": "생활·가정", "body": daily_body},
        {"id": "caution", "title": "주의·한계", "body": caution_body},
        {"id": "practice", "title": "실천 제안", "body": practice_body},
    ]

    return {
        "score": score,
        "grade": grade,
        "summary": summary,
        "a_day_master": a.day_master,
        "b_day_master": b.day_master,
        "relation": {
            "label": rel_label,
            "a_sees_b": god_ab,
            "b_sees_a": god_ba,
        },
        "breakdown": {
            "day_master": max(0, min(100, 50 + dm_delta * 2)),
            "five_elements": max(0, min(100, 50 + el_delta * 2)),
            "day_branch": max(0, min(100, 55 + d_delta * 3)),
            "year_month": max(0, min(100, 55 + y_delta * 2 + m_delta)),
            "hour": max(0, min(100, 50 + h_delta * 3)) if a.pillars.hour and b.pillars.hour else None,
        },
        "a": _person_block(a, **a_meta),
        "b": _person_block(b, **b_meta),
        "sections": sections,
        "notes": [
            d_note,
            y_note,
            m_note,
            h_note,
        ],
        "disclaimer": (
            "본 궁합은 규칙 기반 참고 해석입니다. 생년월일·시진 정확도에 따라 결과가 달라지며, "
            "양력 환산(음력 선택 시) 후 사주를 계산합니다. 투자·결혼 등 중대 결정은 당사자 합의와 "
            "전문가 상담을 권합니다."
        ),
    }
