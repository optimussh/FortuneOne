"""
2026 부자되기 — 재물 전용 연간 리포트.

P1: 총론 · 재물운 · 월별 12 + 활용등급
P2: 월별 일자 캘린더 (점수 + 짧은 문장)
P3: 음력 · 신살 태그 · 대운 스트립 · 오행 비율 · 신강/신약
P4: 일자 장문(body_long) · 인쇄/PDF용 text_export · 수익화 미리보기 메타

문장은 자체 생성(시드). 상용 카피 복제 금지.
"""

from __future__ import annotations

import calendar
from datetime import date
from typing import Any

from app.services.saju_engine import ELEMENT_KO, STEM_ELEMENT, SajuResult
from app.services.saju_report import STEM_NATURE, _elems, _pillars_line, _strong, _t, _weak
from app.services.saju_time import SAJU_HOURS
from app.services.sipsung import mingshi_table

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

GRADES = [
    {"id": "active", "label": "적극활용", "rank": 5, "color": "#16a34a"},
    {"id": "use", "label": "활용", "rank": 4, "color": "#65a30d"},
    {"id": "normal", "label": "보통", "rank": 3, "color": "#ca8a04"},
    {"id": "caution", "label": "주의", "rank": 2, "color": "#ea580c"},
    {"id": "alert", "label": "경계", "rank": 1, "color": "#dc2626"},
]

SHINSAL = ["천을", "역마", "양인", "월덕", "천덕", "도화", "화개", "홍염"]

SCORE_BUCKETS = [30, 40, 50, 60, 70, 80, 90]

_DAY_SHORT = [
    "수익보다 손실 위험이 큰 날입니다. 재정 관련 큰 결정은 미루세요.",
    "흐름이 약합니다. 규모를 줄이고 중요한 계약은 피하세요.",
    "평이한 하루입니다. 무리한 수익 목표만 피하면 됩니다.",
    "작은 수익·정리에는 괜찮은 날입니다. 큰 베팅은 금물입니다.",
    "비교적 좋은 흐름입니다. 가벼운 규모로 활용해 보세요.",
    "감각이 살아나는 날입니다. 소규모 운용·협의에 유리합니다.",
    "재물 흐름이 중심을 잡는 날입니다. 계획된 실행에 적합합니다.",
    "책임 있는 재정 결정에 도움이 됩니다. 단, 욕심은 절제하세요.",
    "도움을 받기 쉬운 날입니다. 큰 욕심보다 실리를 챙기세요.",
    "약속·문서에 민감합니다. 서명·보증은 한 번 더 확인하세요.",
    "지출 관리가 핵심입니다. 들어오는 것보다 나가는 쪽을 보세요.",
    "투자·동업 유혹을 멀리하세요. 손안의 현금이 가장 안전합니다.",
]

_DAY_LONG_EXTRA = [
    "오전에는 정보 수집, 오후에는 실행 여부를 가르는 편이 낫습니다. "
    "가족·동료와의 금전 대화는 감정적으로 번지지 않게 사실 위주로 하세요.",
    "충동 이체·충동 결제를 차단하는 규칙을 하루만이라도 지켜 보세요. "
    "기록이 남으면 다음 판단이 쉬워집니다.",
    "수입이 보여도 ‘확정’ 전까지는 쓰지 않는 습관이 올해 방어선입니다. "
    "문서·영수증·계좌 이력을 정리해 두면 리스크가 줄습니다.",
    "사람과 돈이 함께 움직이는 날이면 관계 비용을 먼저 계산하세요. "
    "호의와 거래를 섞으면 뒷맛이 남을 수 있습니다.",
    "작은 성과를 인정하고 끝내면 길하고, 욕심으로 한 판 더 가면 흐려집니다. "
    "목표 수익을 짧게 잡는 것이 원칙입니다.",
]

_MONTH_BODIES = [
    "흐름에 막힘이 있어도 해결책이 따라올 수 있습니다. 약속을 지키면 전화위복이 됩니다. 보수적으로 움직이되 기회는 놓치지 마세요.",
    "새로운 제안은 한 템포 거르는 것이 안전합니다. 움직이지 않으면 손실도 적습니다. 공연한 제안에 마음 두지 마세요.",
    "무리한 수익 추구는 금물입니다. 약속 어긋남·실수·손실 대체가 어려울 수 있습니다. 자금 운용은 최소로 하세요.",
    "제도권 밖·모호한 계약은 피하세요. 예상 밖 지출이 생기기 쉽고, 나간 돈이 돌아오기 어렵습니다.",
    "대비해도 지출이 커질 수 있습니다. 수익보다 관리·절약이 우선인 달입니다.",
    "약속·신용 이슈에 주의하세요. 수익이 난 뒤 지출하는 순서를 지키면 사고가 줍니다.",
    "계약·실익이 구체화될 수 있는 달입니다. 현실적인 수익 흐름을 점검하고 실행하세요.",
    "지출 민감 구간입니다. 수익은 전만 못하고 나가는 돈이 늘 수 있어 투자는 미루세요.",
    "계획이 어긋나더라도 수습 가능합니다. 들어온 돈이 곧 나갈 수 있으니 순익만 계산하세요.",
    "금전적 실익이 있는 협의·계약이 열릴 수 있습니다. 돕는 인연과 일·수익이 맞물릴 수 있습니다.",
    "막힘이 와도 조력·해결책이 따르는 편입니다. 실수해도 수습 여지가 있습니다.",
    "제안 거절이 미덕인 구간입니다. 정지가 곧 방어입니다.",
]


def _seed(*parts: Any) -> int:
    s = 2166136261
    for p in parts:
        for ch in str(p):
            s ^= ord(ch)
            s = (s * 16777619) & 0x7FFFFFFF
    return s


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)]


def _slot_label(time_slot: str | None, hour: int | None, time_unknown: bool) -> str:
    if time_unknown or not time_slot or time_slot == "unknown":
        return "모름"
    for item in SAJU_HOURS:
        if item["key"] == time_slot:
            lab = item.get("label_short", item["key"])
            rng = item.get("range") or ""
            return f"{lab}({rng})" if rng else lab
    if hour is not None:
        return f"{hour:02d}시"
    return "모름"


def _lunar_text(birth: date) -> str:
    try:
        from sajupy import solar_to_lunar

        lu = solar_to_lunar(birth.year, birth.month, birth.day)
        leap = " (윤달)" if lu.get("is_leap_month") else ""
        return (
            f"{lu['lunar_year']}.{lu['lunar_month']}.{lu['lunar_day']}{leap}"
        )
    except Exception:
        return "—"


def _element_weights(result: SajuResult) -> dict[str, Any]:
    raw = {k: int(result.elements.get(k, 0)) for k in ("wood", "fire", "earth", "metal", "water")}
    total = sum(raw.values()) or 1
    # scale to ~150 like commercial-ish display, keep proportions
    scaled = {k: max(1, round(v / total * 150)) for k, v in raw.items()}
    # fix rounding drift
    drift = 150 - sum(scaled.values())
    if drift != 0:
        key = max(scaled, key=scaled.get)
        scaled[key] = max(1, scaled[key] + drift)
    dm_el = STEM_ELEMENT.get(result.day_master, "earth")
    support = scaled.get(dm_el, 0)
    oppose = 150 - support
    strength = "신강" if support >= oppose * 0.55 else "신약"
    return {
        "counts": raw,
        "scaled": scaled,
        "labels": {k: ELEMENT_KO[k] for k in scaled},
        "day_master_element": dm_el,
        "day_master_element_ko": ELEMENT_KO[dm_el],
        "strength_ratio": f"{support} : {oppose}",
        "strength": strength,
        "display_line": "  ".join(
            f"{ELEMENT_KO[k].split('(')[0] if '(' in ELEMENT_KO[k] else ELEMENT_KO[k]} {scaled[k]}"
            for k in ("wood", "fire", "earth", "metal", "water")
        ),
    }


def _daeun_strip(result: SajuResult, birth: date, gender: str, year: int) -> dict[str, Any]:
    """Product daeun strip: ages + synthetic 간지 labels (MVP, not classical 대운 정밀)."""
    periods = result.daeun or []
    y_stem = result.pillars.year.stem
    y_br = result.pillars.year.branch
    si = STEMS.index(y_stem) if y_stem in STEMS else 0
    bi = BRANCHES.index(y_br) if y_br in BRANCHES else 0
    # start age ~4 to match commercial display flavor
    start_age = 4
    age_now = year - birth.year
    rows = []
    for i in range(10):
        s = start_age + i * 10
        e = s + 9
        # alternate stem/branch steps
        st = STEMS[(si + (i + 1) * (1 if gender == "male" else -1)) % 10]
        br = BRANCHES[(bi + (i + 1) * (1 if gender == "male" else -1)) % 12]
        el_s = ELEMENT_KO[STEM_ELEMENT[st]]
        el_b = ELEMENT_KO[
            {
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
            }[br]
        ]
        note = periods[i].note if i < len(periods) else ""
        rows.append(
            {
                "index": i,
                "start_age": s,
                "end_age": e,
                "age_label": f"{s}세~",
                "stem": st,
                "branch": br,
                "label": f"{st}{el_s[0] if el_s else ''}\n{br}{el_b[0] if el_b else ''}",
                "stem_branch": f"{st}{br}",
                "stem_line": f"{st} {el_s}",
                "branch_line": f"{br} {el_b}",
                "note": note,
                "is_current": s <= age_now <= e,
            }
        )
    return {
        "start_base_age": start_age,
        "intro": (
            f"대운(십년 단위 흐름, 간략 표시): {start_age}세를 기준으로 큰 운의 흐름이 바뀝니다. "
            f"정밀 대운·세운은 추후 보강 예정입니다."
        ),
        "periods": rows,
    }


def _year_ganzhi(year: int) -> str:
    # 1984 = 甲子
    si = (year - 1984) % 10
    bi = (year - 1984) % 12
    return f"{STEMS[si]}{BRANCHES[bi]}"


def _month_ganzhi(year: int, month: int) -> str:
    # rough: not classical 절기 month pillar; product label only
    base = (year - 1984) * 12 + (month - 1)
    return f"{STEMS[base % 10]}{BRANCHES[base % 12]}"


def _score_label(score: int, seed: int) -> str:
    if score <= 30 and seed % 5 == 0:
        return "최악"
    if score == 50 and seed % 7 == 0:
        return "대립·나쁜쪽"
    if score == 70 and seed % 11 == 0:
        return "대립·좋은쪽"
    mapping = {
        90: "아주좋음",
        80: "좋음",
        70: "비교적좋음",
        60: "보통",
        50: "비교적 좋지않음",
        40: "좋지않음",
        30: "나쁨",
    }
    return mapping.get(score, "보통")


def _day_shinsal(seed: int) -> list[str]:
    n = seed % 5  # 0..4 tags likelihood
    if n == 0:
        return []
    tags = []
    for i in range(min(n, 2)):
        tags.append(SHINSAL[(seed // (3 + i)) % len(SHINSAL)])
    # unique preserve order
    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _grade_for(seed: int, month: int, year_bias: int) -> dict[str, Any]:
    # year_bias 0=hard year ... 2=easy — pull grades down/up
    raw = (seed + month * 13 + year_bias * 3) % 100
    if raw < 12 + year_bias * 4:
        g = GRADES[0]  # active rarer in hard years
    elif raw < 28 + year_bias * 5:
        g = GRADES[1]
    elif raw < 52:
        g = GRADES[2]
    elif raw < 78 - year_bias * 3:
        g = GRADES[3]
    else:
        g = GRADES[4]
    return dict(g)


def build_wealth_year(
    result: SajuResult,
    birth: date,
    gender: str,
    *,
    year: int = 2026,
    display_name: str = "",
    calendar_type: str = "solar",
    time_slot: str | None = None,
    hour: int | None = None,
    time_unknown: bool = True,
    include_calendar: bool = True,
    include_long_days: bool = True,
) -> dict[str, Any]:
    t = _t(result)
    seed = _seed(result.day_master, _pillars_line(result), birth.isoformat(), f"wealth_{year}")
    name = display_name or "회원"
    gender_ko = "남자" if gender == "male" else "여자"
    age = year - birth.year
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    time_lab = _slot_label(time_slot, hour, time_unknown)
    lunar = _lunar_text(birth)
    weights = _element_weights(result)
    daeun = _daeun_strip(result, birth, gender, year)
    year_gz = _year_ganzhi(year)

    # harder year bias from seed (0 hard .. 2 mild)
    year_bias = seed % 3
    year_tone = ["수비·절약", "선택과 집중", "완만한 기회"][year_bias]

    overview = (
        f"【{year}년 부자되기 총론】 {name}님은 일간 {result.day_master}({nature}) 성향으로, "
        f"고집이 강하면 손실도 보지만 한 번 궤도에 오르면 성과 폭이 큰 편으로 읽힙니다. "
        f"성공과 실패의 결이 분명해, ‘작은 부’보다 ‘굵은 결실’ 쪽 시나리오가 어울립니다. "
        f"업종 힌트: {t['career']} 계열, 특히 {t['color']}·{t['dir']} 기운과 맞닿은 일이 잘 맞을 수 있습니다. "
        f"나무·종이·공간 연출·요식에서 목재·천연 소재를 활용하는 장사도 궁합이 나을 수 있습니다. "
        f"재물 운용은 처음엔 적극적이다가, 감당 범위를 넘으면 급히 축소하는 패턴이 나타날 수 있습니다. "
        f"사업 치밀함보다 장사·현금흐름형 실익이 더 안전합니다. "
        f"올해 키워드는 ‘{year_tone}’입니다. 부동산 공격 투자보다 주식 등 단기 목표 수익이 상대적으로 덜 부담일 수 있으나, "
        f"장기 큰 수익을 올해에 몰아넣기엔 {year_tone} 기운이 강합니다. "
        f"도박·복권·과한 레버리지는 소탐대실 위험이 큽니다. "
        f"부자는 때를 기다립니다. 규모를 줄이고 작은 수익에 만족하며 다음 기회를 준비하세요. "
        f"(오행 {_elems(result)} · 강 {_strong(result)} · 약 {_weak(result)})"
    )

    year_money = (
        f"【{year}년 재물운】 일의 진행과 현금 흐름에 제동이 걸리기 쉬운 해로 읽힙니다. "
        f"투자·보증·본인 명의 문서 계약은 낭패로 이어질 수 있어, 불려 먹기보다 지키기·정리가 우선입니다. "
        f"큰 제안·규모 투자는 미루고, 노동·본업 수익 외 ‘들어와도 나갈 돈’을 경계하세요. "
        f"키워드는 {t['wealth']}이지만, 올해는 수익 창출보다 지출 통제·예비비·자기 몫 확보가 핵심입니다. "
        f"외부 투자·동업은 자신 있는 분야라도 기회가 화가 될 수 있습니다. "
        f"금전 약속을 과신하지 말고, 손안의 현금 범위에서만 계획을 세우세요. "
        f"관리만 잘해도 운용의 어려움 상당 부분을 피할 수 있습니다."
    )

    month_guide_intro = (
        f"【{year}년 부자되기 월별 활용법】 소득이 커 보여도 운용은 자제하는 해가 될 수 있습니다. "
        f"년운·재물 흐름이 모두 강한 공격 구간은 아닙니다. 규모를 줄이고, 아래 월별 활용등급을 참고하세요. "
        f"‘적극활용’ 달에도 과신은 금물—안정·보수 운용이 기본입니다."
    )

    months: list[dict[str, Any]] = []
    calendar_months: list[dict[str, Any]] = []

    for m in range(1, 13):
        g = _grade_for(seed, m, year_bias)
        body_idx = (seed + m * 7) % len(_MONTH_BODIES)
        m_body = (
            f"{year}년 {m}월: {_MONTH_BODIES[body_idx]} "
            f"활용등급 【{g['label']}】. 일간 {result.day_master}의 {t['adj']} 성향을 의식해 "
            f"{_pick(seed + m, ['현금 비중 확대', '고정비 점검', '계약 일정 분산', '비상금 확충', '매출 회수 우선'])}에 집중하세요."
        )
        months.append(
            {
                "month": m,
                "title": f"{m}월",
                "body": m_body,
                "grade": g["id"],
                "grade_label": g["label"],
                "grade_rank": g["rank"],
                "grade_color": g["color"],
                "ganzhi": _month_ganzhi(year, m),
            }
        )

        if include_calendar:
            n_days = calendar.monthrange(year, m)[1]
            days = []
            for d in range(1, n_days + 1):
                dseed = _seed(seed, year, m, d, result.day_master)
                score = SCORE_BUCKETS[dseed % len(SCORE_BUCKETS)]
                # pull scores down slightly in alert months
                if g["rank"] <= 2:
                    score = min(score, 70) if dseed % 3 else max(30, score - 10)
                if g["rank"] >= 5:
                    score = max(score, 60) if dseed % 2 else score
                short = _DAY_SHORT[dseed % len(_DAY_SHORT)]
                tags = _day_shinsal(dseed)
                wd = date(year, m, d).weekday()  # mon=0
                day_obj: dict[str, Any] = {
                    "day": d,
                    "date": f"{year}-{m:02d}-{d:02d}",
                    "weekday": WEEKDAYS[wd],
                    "weekday_index": wd,
                    "score": score,
                    "score_label": _score_label(score, dseed),
                    "shinsal": tags,
                    "body": short,
                }
                if include_long_days:
                    day_obj["body_long"] = (
                        f"{year}년 {m}월 {d}일({WEEKDAYS[wd]}): {short} "
                        f"{_DAY_LONG_EXTRA[dseed % len(_DAY_LONG_EXTRA)]} "
                        f"점수 {score}({_score_label(score, dseed)}). "
                        f"{'신살: ' + ', '.join(tags) + '. ' if tags else ''}"
                        f"일간 {result.day_master} 기준으로 규모를 조절하세요."
                    )
                days.append(day_obj)
            calendar_months.append(
                {
                    "month": m,
                    "year": year,
                    "title": f"{year}년({year_gz}) {m}월({_month_ganzhi(year, m)})",
                    "ganzhi": _month_ganzhi(year, m),
                    "grade_label": g["label"],
                    "days": days,
                }
            )

    # monetization preview meta (no real paywall yet)
    monetization = {
        "enabled": False,
        "mode": "preview",
        "message": (
            "지금은 전 구간 무료 체험입니다. 이후 수익화 시 "
            "‘미리보기(총론·이번 달 일부)’ 후 구슬/소액 결제로 월별·일자·장문 해금 방식을 검토 중입니다."
        ),
        "concepts": [
            {
                "id": "beads",
                "name": "구슬",
                "unit_price_krw": 100,
                "packs": [
                    {"count": 100, "bonus_pct": 0, "price_krw": 10000},
                    {"count": 200, "bonus_pct": 10, "price_krw": 20000, "bonus_count": 20},
                    {"count": 500, "bonus_pct": 15, "price_krw": 50000, "bonus_count": 75},
                ],
                "spend_hints": {
                    "month_unlock": 5,
                    "day_long": 1,
                    "full_year_calendar": 30,
                    "pdf_export": 10,
                },
            },
            {
                "id": "one_time",
                "name": "리포트 단건",
                "price_krw": 3900,
                "covers": "해당 연도 부자되기 전체(월·일자·장문)",
            },
        ],
        "free_preview": {
            "overview": True,
            "year_money": True,
            "months_grades_only": True,
            "calendar_days_free": 7,
            "long_days": False,
        },
    }

    # text export for print/PDF (client can print)
    lines = [
        f"{year} 부자되기 — {name}님({gender_ko}, {age}세)",
        f"양력: {birth.year}.{birth.month}.{birth.day}  음력: {lunar}  시간: {time_lab}",
        f"명식: {_pillars_line(result)}  일간: {result.day_master}",
        f"오행: {weights['display_line']}  {weights['strength']} ({weights['strength_ratio']})",
        "",
        overview,
        "",
        year_money,
        "",
        month_guide_intro,
    ]
    for mo in months:
        lines.append(f"{mo['month']}월 [{mo['grade_label']}] {mo['body']}")
    lines.append("")
    lines.append(f"— 생성 기준 연도 {year} · 동일 사주·연도 고정 시드 —")
    text_export = "\n".join(lines)

    return {
        "year": year,
        "title": f"{year} 부자되기",
        "subtitle": "재물 전용 연간 리포트 · 자체 생성 (동일 사주·연도 고정)",
        "header": {
            "display_name": name,
            "gender": gender,
            "gender_ko": gender_ko,
            "age": age,
            "age_text": f"{name}님({gender_ko}, {age}세)",
            "solar_text": f"{birth.year}.{birth.month}.{birth.day}",
            "lunar_text": lunar,
            "time_text": time_lab,
            "calendar_type": calendar_type,
            "pillars_line": _pillars_line(result),
            "day_master": result.day_master,
            "year_ganzhi": year_gz,
        },
        "mingshi": mingshi_table(result),
        "elements": weights,
        "daeun": daeun,
        "overview": {"title": f"{year}년 부자되기 총론", "body": overview},
        "year_money": {"title": f"{year}년 재물운", "body": year_money},
        "month_guide": {
            "title": f"{year}년 부자되기 월별 활용법",
            "intro": month_guide_intro,
            "grades_legend": GRADES,
            "months": months,
        },
        "calendar": {
            "title": f"{year}년 재물 캘린더",
            "note": "날짜는 양력 기준입니다. 점수·신살은 참고 지표이며 투자 권유가 아닙니다.",
            "score_legend": [
                {"score": 90, "label": "아주좋음"},
                {"score": 80, "label": "좋음"},
                {"score": 70, "label": "비교적좋음"},
                {"score": 60, "label": "보통"},
                {"score": 50, "label": "비교적 좋지않음"},
                {"score": 40, "label": "좋지않음"},
                {"score": 30, "label": "나쁨"},
            ],
            "months": calendar_months if include_calendar else [],
        },
        "monetization": monetization,
        "export": {
            "format": "text",
            "filename_hint": f"fortuneone-wealth-{year}.txt",
            "body": text_export,
        },
        "disclaimer": (
            "본 리포트는 엔터테인먼트·자기성찰 목적의 규칙 기반 해석입니다. "
            "투자·대출·계약 등 중요한 금전 결정은 전문가 상담을 권합니다."
        ),
    }
