"""
토정비결 스타일 연간 리포트 (형식 참고 · 자체 생성 문장).
동일 사주 + 동일 연도 → 동일 결과 (고정 시드).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_engine import ELEMENT_KO, STEM_ELEMENT, SajuResult
from app.services.saju_report import STEM_NATURE, _elems, _pillars_line, _strong, _t, _weak
from app.services.sipsung import mingshi_table
from app.services.saju_time import SAJU_HOURS

MONTH_NAMES = [
    "1월",
    "2월",
    "3월",
    "4월",
    "5월",
    "6월",
    "7월",
    "8월",
    "9월",
    "10월",
    "11월",
    "12월",
]


def _seed(*parts: Any) -> int:
    s = 2166136261
    for p in parts:
        for ch in str(p):
            s ^= ord(ch)
            s = (s * 16777619) & 0x7FFFFFFF
    return s


def _stable(result: SajuResult, birth: date, year: int) -> int:
    return _seed(
        result.day_master,
        _pillars_line(result),
        birth.isoformat(),
        f"tojeong_{year}_v4",
    )


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)]


def _slot_label(time_slot: str | None, hour: int | None, time_unknown: bool) -> str:
    if time_unknown or not time_slot or time_slot == "unknown":
        return "모름"
    for item in SAJU_HOURS:
        if item["key"] == time_slot:
            return f"{item.get('label_short', item['key'])} ({item.get('range', '')})"
    if hour is not None:
        return f"{hour:02d}시"
    return "모름"


# Month tone templates — 12 unique styles, selected by seed+month (not recycled same text)
_MONTH_TEMPLATES = [
    "앞이 트이는 달입니다. 다만 원하는 만큼은 아니어도 흐름이 긍정으로 기울 수 있으니 감사히 받아들이세요. 작은 성취를 기록해 두면 다음 달 동력이 됩니다.",
    "하늘이 흐린 듯 결실이 더딜 수 있습니다. 조급함보다 과정에 의미를 두면 마음이 편해집니다. 준비와 정리가 결실로 이어지는 정상적인 단계로 보세요.",
    "말과 소문에 예민해질 수 있습니다. 가까운 이와의 다툼을 피하고, 운전·보행 등 안전에 유의하세요. 귀는 열되 모든 말을 사실로 받아들이진 마세요.",
    "출세·인정 운이 강해질 수 있는 달입니다. 직장인이면 평가·연봉, 사업이면 확장 논의가 유리합니다. 다만 자만하지 말고 실적으로 말하세요.",
    "사람과 조직의 불화가 있어도 존중으로 풀면 안정됩니다. 관계를 고치는 달이 재물보다 먼저일 수 있습니다. 사소한 예의가 큰 신뢰를 만듭니다.",
    "가정·가까운 울타리에 온기가 돌 수 있습니다. 금전·정이 함께 들어오는 흐름이니 나눔을 아끼지 마세요. 집안 대소사에 마음을 쓰면 길합니다.",
    "아직은 인내의 달입니다. 온기가 돌기 시작해도 과한 욕심은 금물입니다. 성실히 씨앗을 심고 수확 시기를 기다리세요.",
    "건강 관리가 특히 중요합니다. 소화·더위·불규칙 생활을 조심하고, 정기 체크가 예방이 됩니다. 지난달과 맞물리면 뜻밖의 행운도 있습니다.",
    "새 마음으로 시작하기 좋습니다. 지인 도움·시험·도전이 잘 맞을 수 있습니다. 망설이던 일을 실행에 옮기세요.",
    "하는 일마다 형통할 수 있는 길운의 달입니다. 묵은 문제도 풀릴 수 있으니 미뤄 둔 일을 꺼내 보세요. 다만 게으름만 경계하면 됩니다.",
    "마무리를 대충 하면 용두사미가 됩니다. 끝까지 집중하면 재물·성과로 이어질 수 있습니다. 끝맺음이 복입니다.",
    "노력의 결실이 보이는 달입니다. 운이 길 위에 놓여 있으니 지금 자리에서 충실히 임하세요. 성실함이 막힘을 없앱니다.",
]


def build_tojeong(
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
) -> dict[str, Any]:
    t = _t(result)
    seed = _stable(result, birth, year)
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    age = year - birth.year
    cal = "양력" if calendar_type != "lunar" else "음력"
    time_lab = _slot_label(time_slot, hour, time_unknown)
    name = display_name or "회원"

    # 종합운 — unique long prose, no shared filler blocks
    overall = (
        f"【{year}년 종합운】 {name}님, {birth.year}년 {birth.month:02d}월 {birth.day:02d}일 ({cal}) "
        f"{time_lab} 기준 원국은 {_pillars_line(result)}이며 일간은 {result.day_master}({nature})입니다. "
        f"오행은 {_elems(result)}로, 강 {_strong(result)} · 약 {_weak(result)}의 결이 올해에도 이어집니다. "
        f"{age}세 전후의 {year}년은 ‘{t['mood']}’ 기운이 강한 해로 읽힙니다. "
        f"마른 가지에도 때가 되면 새순이 나듯, 부족함이 있어도 마음 중심을 지키면 스스로 편안해질 수 있습니다. "
        f"재물은 손에 들어와도 쓰기 쉬운 흐름이니 들어오면 지키려는 습관이 필요합니다. "
        f"벗이 적어 고독을 느낄 수 있으나, 긍정은 사람을 불러들입니다. "
        f"시비와 구설을 멀리하고, 치료보다 예방—정기 검진과 생활 리듬—이 우선입니다. "
        f"새 시도는 {t['dir']} 방향·{t['color']} 기운과 맞추면 순조로울 수 있습니다. "
        f"역량 밖의 영역만 탐하면 하룻강아지 범 무서운 줄 모르는 격이 될 수 있으니 분수를 지키세요. "
        f"모함·시기에 과민하면 스스로 길을 막을 수 있습니다. 슬럼프에는 물러서 때를 기다리는 지혜가 필요합니다. "
        f"사랑에 이유를 달기보다 진심을 지키는 태도가 인연을 깊게 합니다. "
        f"같은 사주·같은 연도로 다시 보아도 이 종합운의 골격은 동일합니다."
    )

    # 월별 12 — each month unique template rotated by seed
    months = []
    for m in range(1, 13):
        idx = (seed + m * 7) % len(_MONTH_TEMPLATES)
        body = (
            f"{year}년 {m}월: {_MONTH_TEMPLATES[idx]} "
            f"일간 {result.day_master}의 {t['adj']} 성향을 의식하면 과한 승부보다 페이스 조절이 길합니다. "
            f"이 달의 핵심 과제 한 가지는 "
            f"{_pick(seed + m, ['관계 정리', '재정 점검', '건강 루틴', '실력 보강', '기회 포착', '인내와 준비'])}입니다."
        )
        months.append({"month": m, "title": f"{m}월", "body": body})

    domains = {
        "love": (
            "연애운",
            f"갑작스러운 환경 변화(이직·이사 등)가 새 인연의 문이 될 수 있습니다. "
            f"{t['love']}을 살리면 관계가 깊어지고, 이유를 과도하게 따지면 마음이 식습니다. "
            f"적극적으로 움직이되 상대의 속도도 존중하세요.",
        ),
        "work": (
            "직장운",
            f"내면 스트레스가 쌓이면 언젠가 표출됩니다. {t['career']} 환경에서 경쟁 압박이 있을 수 있으니 "
            f"삭히기만 하지 말고 건설적으로 푸는 방법을 찾으세요. 조급함은 화를 부르니 조율이 필요합니다.",
        ),
        "health": (
            "건강운",
            f"중대 질환보다 생활습관이 쌓이는 시기입니다. {t['body']} 관련 관리와 규칙적 식사·수면이 우선입니다. "
            f"정기 검진으로 보이지 않는 위험을 줄이세요. 예방이 치료보다 중요합니다.",
        ),
        "wish": (
            "소망운",
            f"복잡할수록 한 가지에 몰두하십시오. 두 마리 토끼를 다 잡으려다 모두 놓칠 수 있습니다. "
            f"명예와 재물 중 우선순위를 정하고, 해외·원거리 일정은 신중히 준비하세요.",
        ),
        "social": (
            "대인운",
            f"기존 관계는 깊어질 수 있으나 새 인연에는 경계가 먼저일 수 있습니다. "
            f"{t['social']} 포지션을 살리되, 악한 접근은 드물더라도 수용과 경계의 균형이 필요합니다.",
        ),
        "manner": (
            "처세운",
            f"매뉴얼·원칙에 충실한 편이라 유연한 대처가 필요할 때 답답해 보일 수 있습니다. "
            f"유머와 여유를 더하면 신용이 살아납니다. 가족·자녀와 한 걸음 더 가까워지는 노력도 길합니다.",
        ),
    }
    domain_list = []
    for i, (key, (title, body)) in enumerate(domains.items()):
        domain_list.append(
            {
                "id": key,
                "title": title,
                "body": body
                + f" (일간 {result.day_master} · {year}년 고정 해석 {_pick(seed + i, ['가', '나', '다'])}형)",
            }
        )

    lucky_num = 1 + (seed % 9)
    unlucky_num = 1 + ((seed // 3) % 9)
    if unlucky_num == lucky_num:
        unlucky_num = (lucky_num % 9) + 1

    lucky_color = _pick(seed, ["검정색", "하얀색", "청색", "붉은색", "녹색"])
    unlucky_color = _pick(seed + 2, ["노란색", "회색", "갈색", "보라색"])

    lucky_block = (
        f"【행운의 숫자 {lucky_num}】 시작과 중심의 기운으로 읽힙니다. "
        f"시험·계약·새 프로젝트의 첫 걸음에 이 숫자를 의식하면 심리적 중심이 잡힙니다. "
        f"【주의 숫자 {unlucky_num}】 겹치는 날의 큰 결정은 한 번 더 미루는 편이 낫습니다. "
        f"【행운 색 {lucky_color}】 옷·소품·문서 포인트로 가까이 두세요. "
        f"【주의 색 {unlucky_color}】 중요한 날 과한 사용은 피하세요. "
        f"이사·사업·가전 등 큰 선택에는 {lucky_color} 기운을 소량 배치하는 정도가 현실적입니다."
    )

    return {
        "year": year,
        "title": f"나의 {year}년 명품 토정 결과",
        "subtitle": "토정 형식 참고 · 자체 생성 풀이 (동일 사주·연도 고정)",
        "header": {
            "display_name": name,
            "birth_text": f"{birth.year}년 {birth.month:02d}월 {birth.day:02d}일 ({cal})",
            "time_text": time_lab,
            "pillars_line": _pillars_line(result),
            "day_master": result.day_master,
            "elements_line": _elems(result),
        },
        "mingshi": mingshi_table(result),
        "elements": result.elements,
        "overall": {"title": "올해의 종합운", "body": overall},
        "months": months,
        "domains": domain_list,
        "lucky": {
            "lucky_number": lucky_num,
            "unlucky_number": unlucky_num,
            "lucky_color": lucky_color,
            "unlucky_color": unlucky_color,
            "body": lucky_block,
        },
    }
