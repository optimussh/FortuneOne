"""
Long-form Korean saju reports.

- Stable (same birth/day_master → same text): 신년 연도 운세, 오행 심층, 인생풀이/평생
- Variable (date-dependent): 오늘의 운세, (확장 시) 주/월 운세
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_engine import (
    ELEMENT_KO,
    STEM_ELEMENT,
    SajuResult,
)

ELEMENT_TONE: dict[str, dict[str, str]] = {
    "wood": {
        "adj": "생장·확장",
        "mood": "시작과 성장",
        "career": "기획, 교육, 의료, 콘텐츠, 환경, 스타트업, 브랜딩",
        "love": "솔직하고 따뜻한 표현, 성장하는 관계",
        "wealth": "씨앗형 투자와 장기 복리",
        "social": "네트워킹과 아이디어 공유",
        "body": "간·담·눈·근육의 긴장 완화",
        "virtue": "인(仁)과 추진력",
    },
    "fire": {
        "adj": "열정·표현",
        "mood": "가시성과 영향력",
        "career": "마케팅, 공연, 영업, 미디어, 브랜드, 교육 강의",
        "love": "설렘과 적극적 어필, 따뜻한 관심",
        "wealth": "단기 성과와 가시적 수익 사이클",
        "social": "리더십·분위기 메이킹",
        "body": "심장·소장·혈압·수면 리듬",
        "virtue": "예(禮)와 표현력",
    },
    "earth": {
        "adj": "안정·신뢰",
        "mood": "기반과 지속",
        "career": "운영, 재무, 부동산, 행정, HR, 품질, 물류",
        "love": "신뢰와 책임감 있는 동반",
        "wealth": "저축·자산 축적·리스크 완충",
        "social": "중재자·버팀목 역할",
        "body": "비위·소화·습관적 과식 주의",
        "virtue": "신(信)과 꾸준함",
    },
    "metal": {
        "adj": "결단·정리",
        "mood": "구조와 완성",
        "career": "법률, 엔지니어링, 감사, 전략, 전문직, 분석",
        "love": "원칙과 진정성, 경계가 있는 애정",
        "wealth": "효율·구조화·고부가 가치 포지션",
        "social": "명확한 기준과 약속 이행",
        "body": "폐·호흡·피부·건조함 관리",
        "virtue": "의(義)와 절제",
    },
    "water": {
        "adj": "흐름·직관",
        "mood": "유연과 성찰",
        "career": "연구, 상담, 데이터, 해외, 예술, 전략 기획",
        "love": "깊이 있는 공감과 경청",
        "wealth": "현금흐름·정보 우위·순환 투자",
        "social": "조용한 영향력과 조율",
        "body": "신장·수분·과로성 피로",
        "virtue": "지(智)와 유연성",
    },
}

STEM_NATURE: dict[str, str] = {
    "甲": "큰 나무처럼 곧고 개척적인",
    "乙": "꽃과 덩굴처럼 유연하고 섬세한",
    "丙": "태양처럼 밝고 확산적인",
    "丁": "촛불처럼 섬세하고 집중적인",
    "戊": "산처럼 든든하고 포용적인",
    "己": "밭처럼 실용적이고 돌보는",
    "庚": "쇠처럼 단호하고 결단력 있는",
    "辛": "보석처럼 예민하고 정교한",
    "壬": "강물처럼 지혜롭고 넓은",
    "癸": "이슬처럼 섬세하고 흡수력 있는",
}

# Deterministic filler paragraphs keyed by stem index (stable)
_EXTRA_BLOCKS = [
    "일상에서는 ‘속도와 방향’을 동시에 점검하는 습관이 중요합니다. 아침에 오늘 꼭 끝낼 일 한 가지를 정하고, 저녁에 실행 여부를 짧게 기록해 두면 운의 흐름을 스스로 다스리는 힘이 생깁니다. 주변의 평가에 흔들리기보다, 자신의 기준표를 만들어 두는 편이 장기적으로 유리합니다.",
    "인간관계에서는 과한 설명보다 정확한 한 문장이 오해를 줄입니다. 상대의 의도를 추측하기 전에 사실 확인을 한 번 거치면, 불필요한 감정 소모를 막을 수 있습니다. 특히 가까운 사람일수록 ‘당연한 마음’을 말로 표현하는 연습이 관계를 단단하게 합니다.",
    "재물과 커리어는 한 번의 도약보다 계단식 상승이 안전합니다. 준비된 시기에 움직이는 것과 조급한 시기에 움직이는 것은 겉보기에 비슷해 보여도 결과가 다릅니다. 문서화·기록·피드백 루프를 갖추면 같은 노력으로도 성과의 재현성이 높아집니다.",
    "몸과 마음은 분리되지 않습니다. 수면, 수분, 가벼운 움직임이 무너지면 판단력도 함께 흐려집니다. 바쁜 시기일수록 의도적으로 쉬는 시간을 캘린더에 넣는 것이 오히려 생산성을 지킵니다. 작은 루틴이 큰 운의 받침이 됩니다.",
    "인생의 전환점에서는 ‘무엇을 더할지’보다 ‘무엇을 멈출지’가 더 중요한 질문이 됩니다. 익숙하지만 소진되는 패턴을 내려놓을 때 새로운 기회가 들어올 자리가 생깁니다. 용신에 해당하는 생활 요소를 공간·일정·인간관계에 조금씩 배치해 보세요.",
]


def _seed(*parts: Any) -> int:
    """Stable hash — same parts always same int (no Python hash randomization)."""
    s = 2166136261
    for p in parts:
        for ch in str(p):
            s ^= ord(ch)
            s = (s * 16777619) & 0x7FFFFFFF
    return s


def _stable_seed_from_chart(result: SajuResult, birth: date, *extra: Any) -> int:
    """Identity-stable: day_master + pillars + birth + extras (no 'today')."""
    pillars = (
        f"{result.pillars.year.stem}{result.pillars.year.branch}"
        f"{result.pillars.month.stem}{result.pillars.month.branch}"
        f"{result.pillars.day.stem}{result.pillars.day.branch}"
    )
    return _seed(result.day_master, pillars, birth.isoformat(), *extra)


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)] if options else ""


def _expand(base: str, seed: int, target_min: int = 520, target_max: int = 980) -> str:
    """Pad narrative to ~500–1000 chars deterministically."""
    text = base.strip()
    i = 0
    while len(text) < target_min and i < 12:
        block = _EXTRA_BLOCKS[(seed + i * 3) % len(_EXTRA_BLOCKS)]
        text = text + "\n\n" + block
        i += 1
    if len(text) > target_max:
        # cut at sentence boundary near target_max
        cut = text[:target_max]
        for sep in ("。", ".", "다.", "요.", "\n"):
            pos = cut.rfind(sep)
            if pos > target_min - 80:
                return cut[: pos + len(sep)].strip()
        return cut.strip()
    return text


def _el(result: SajuResult) -> str:
    return STEM_ELEMENT.get(result.day_master, "earth")


def _tone(result: SajuResult) -> dict[str, str]:
    return ELEMENT_TONE[_el(result)]


def _weak_ko(result: SajuResult) -> str:
    if not result.weak_elements:
        return "비교적 고른 균형"
    return ", ".join(ELEMENT_KO.get(e, e) for e in result.weak_elements)


def _strong_ko(result: SajuResult) -> str:
    if not result.strong_elements:
        return "고른 분포"
    return ", ".join(ELEMENT_KO.get(e, e) for e in result.strong_elements)


def _elems_line(result: SajuResult) -> str:
    parts = [f"{ELEMENT_KO[k]} {result.elements.get(k, 0)}" for k in ("wood", "fire", "earth", "metal", "water")]
    return " / ".join(parts)


# ── Variable: daily (date-dependent) ──────────────────────────────────────


def build_daily_long(result: SajuResult, as_of: date | None = None) -> dict[str, Any]:
    d = as_of or date.today()
    t = _tone(result)
    seed = _seed(result.day_master, d.isoformat(), "daily_v2")
    scores = result.daily.scores
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")

    overview = _expand(
        f"【{d.year}년 {d.month}월 {d.day}일 총운】 일간 {result.day_master}({nature} 기질)을 중심으로 보면, "
        f"오늘은 {t['mood']}의 결이 하루의 바탕을 이룹니다. 원국에서 강한 기운은 {_strong_ko(result)}, "
        f"보완이 필요한 쪽은 {_weak_ko(result)}입니다. 오행 분포는 {_elems_line(result)}로 나타납니다. "
        f"총운 {scores.get('overall', 70)}점을 기준으로, 오전에는 집중·정리, 오후에는 대인·조율 리듬이 잘 맞을 수 있습니다. "
        f"{t['adj']}의 강점을 쓰되, 부족한 기운은 생활 루틴(색·방향·휴식)으로 메우는 하루가 유리합니다. "
        f"작은 약속도 명확히 하고, 감정 소모가 큰 논쟁은 하루 미루는 편이 득이 됩니다.",
        seed,
        480,
        900,
    )
    wealth = _expand(
        f"【재물·실속】 금전 운 {scores.get('money', 65)}점. {t['wealth']} 관점이 오늘의 키워드입니다. "
        f"큰 지출·계약은 자료를 한 번 더 검토한 뒤 진행하고, ‘새는 돈’(구독·수수료·미사용 서비스) 점검이 "
        f"실질 점수를 올립니다. 오후 숫자 업무(정산·견적·예산) 배치를 권합니다.",
        seed + 1,
        480,
        900,
    )
    love = _expand(
        f"【애정·관계】 관계 운 {scores.get('love', 65)}점. {t['love']}이 핵심입니다. "
        f"가까운 사람에게는 짧은 안부라도 진심을 담아 전하면 오해가 풀리기 쉽습니다. "
        f"솔로는 공통 관심사 대화가, 커플은 ‘옳고 그름’보다 서로의 피로도를 먼저 살피는 태도가 유리합니다. "
        f"밤 시간대 중요 결정은 피하고 휴식을 우선하세요.",
        seed + 2,
        480,
        900,
    )
    work = _expand(
        f"【일·건강】 건강 {scores.get('health', 65)}점. {t['career']} 계열 업무 방식이 잘 맞습니다. "
        f"완성도보다 ‘한 칸 전진’이 중요하고, 회의 전 결론 문장을 적어 두면 영향력이 커집니다. "
        f"수분·스트레칭으로 컨디션을 유지하고, {t['body']} 관련 무리는 줄이세요. "
        f"행운 색 {result.daily.lucky.get('color', '청색')}, 방향 {result.daily.lucky.get('direction', '동')}을 "
        f"동선·소품에 살짝 반영해 보세요.",
        seed + 3,
        480,
        900,
    )
    advice = (
        f"【오늘 가이드】 {t['adj']} 강점 활용 + {_weak_ko(result)} 보강. "
        f"피하기: 감정 큰 결정·검증 없는 금전 약속. "
        f"실천: 아침 10분 계획 + 저녁 감사 한 가지. "
        f"일간 {result.day_master}의 {nature} 성향을 존중하며 페이스를 조절하세요."
    )
    advice = _expand(advice, seed + 4, 400, 700)

    return {
        "date": d.isoformat(),
        "title": f"{d.month}월 {d.day}일 오늘의 운세",
        "scores": scores,
        "lucky": result.daily.lucky,
        "sections": [
            {"id": "overview", "title": "총운 해설", "body": overview},
            {"id": "wealth", "title": "재물·실속", "body": wealth},
            {"id": "love", "title": "애정·인간관계", "body": love},
            {"id": "work_health", "title": "일·건강·실천", "body": work},
            {"id": "advice", "title": "오늘 가이드", "body": advice},
        ],
    }


# ── Stable: new year / five element / life ────────────────────────────────


def build_new_year_2026(result: SajuResult, birth: date) -> dict[str, Any]:
    return build_year_fortune(result, birth, year=2026)


def build_year_fortune(result: SajuResult, birth: date, year: int = 2026) -> dict[str, Any]:
    """Deterministic yearly fortune — same chart+year → same text forever."""
    t = _tone(result)
    seed = _stable_seed_from_chart(result, birth, f"year_{year}")
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    age = year - birth.year
    yong = result.yongsin.element_ko if result.yongsin else "균형"

    h1 = _expand(
        f"【{year}년 한 해의 주제 · 정통 사주 관점】 "
        f"일간 {result.day_master}—{nature} 기질—을 가진 당신에게 {year}년은 ‘{t['mood']}’가 "
        f"핵심 테마로 작동하는 해입니다. 만 나이 약 {age}세 전후, 원국의 강한 기운({_strong_ko(result)})은 "
        f"성과의 엔진이 되고, 약한 기운({_weak_ko(result)})은 보완 과제로 반복 등장할 수 있습니다. "
        f"오행 분포 {_elems_line(result)}를 기준으로 보면, {t['virtue']}를 의식한 선택이 "
        f"한 해의 마찰을 줄입니다. 상반기는 기반·관계 정리, 하반기는 선택과 확장의 결이 두드러질 수 있으니 "
        f"연초에 ‘올해 꼭 끝낼 일 3가지 / 내려놓을 일 3가지’를 문서로 남겨 두십시오. "
        f"용신 힌트({yong})를 공간·옷·일정·만남에 꾸준히 배치하면 심리적 안정과 판단력이 함께 올라갑니다. "
        f"{year}년의 키워드는 속도보다 방향, 과시보다 지속 가능한 루틴입니다. "
        f"같은 사주 원국과 동일 연도 기준으로 이 해석은 항상 동일하게 유지되도록 설계되어 있습니다.",
        seed,
        700,
        1000,
    )
    h2 = _expand(
        f"【{year}년 상·하반기 흐름】 "
        f"상반기(1–6월)에는 학습, 재정 점검, 건강 베이스라인, 인간관계 경계 설정에 힘을 주세요. "
        f"{t['wealth']} 관점의 재설계가 연말 안정감으로 이어집니다. 충동 이직·무리한 확장은 "
        f"상반기보다 하반기 검증 후가 낫습니다. "
        f"하반기(7–12월)에는 준비해 둔 프로젝트가 가시화되기 쉽고, {t['career']} 분야에서 "
        f"이름·포트폴리오·실적을 드러내면 기회가 붙습니다. 다만 과로는 말년 피로로 누적되므로 "
        f"휴식 일정을 캘린더에 선점하세요. 분기마다 목표를 재분류하면 대운 흐름과도 맞물리기 쉽습니다. "
        f"일간 {result.day_master}의 {nature} 성향은 ‘한 번에 끝내기’보다 ‘방향 고정 후 반복 개선’에서 "
        f"진가를 발휘합니다.",
        seed + 11,
        700,
        1000,
    )
    h3 = _expand(
        f"【{year}년 재물·애정·사회】 "
        f"재물은 ‘한 번에 크게’보다 ‘매월 규칙적으로’가 정답에 가깝습니다. "
        f"고정비 재협상, 비상금 3–6개월 치, 소득원 분산을 목표로 잡으세요. "
        f"애정·가족에서는 {t['love']}이 관계를 살리는 열쇠이며, 결혼·동거·이사 등 고관여 결정은 "
        f"감정 고조기보다 한 템포 쉬어 조율하는 편이 안전합니다. "
        f"사회적 평판은 {t['social']} 역할에서 쌓이니, 모임·협업에서 약속을 지키는 태도가 "
        f"연말 평판 자산이 됩니다. 약한 오행({_weak_ko(result)})을 상징하는 생활 요소를 "
        f"보강하면 결정 피로가 줄어 재물·관계 판단이 맑아지는 경우가 많습니다.",
        seed + 22,
        700,
        1000,
    )
    h4 = _expand(
        f"【{year}년 실천 로드맵 · 평생 운세와의 연결】 "
        f"1월: 목표·예산·건강 측정. 3–4월: 스킬·자격·포트폴리오 보강({t['career']}). "
        f"6월: 중간 점검—버린 일/키울 일. 9–10월: 가시적 성과·협상·계약. "
        f"12월: 감사 정리와 다음 해 씨앗. "
        f"이 로드맵은 초년·중년·말년의 큰 흐름 위에서 {year}년만의 ‘한 계단’을 오르는 설계입니다. "
        f"평생 운세의 기질({nature})과 모순되지 않게, {t['adj']}의 강점은 드러내고 "
        f"약점은 시스템(루틴·사람·도구)으로 보완하십시오. "
        f"동일 생년월일시·동일 연도 입력 시 본 신년 해설의 핵심 문장은 변하지 않습니다.",
        seed + 33,
        700,
        1000,
    )

    return {
        "year": year,
        "title": f"{year} 신년 운세 심층 해설",
        "subtitle": f"일간 {result.day_master} · {t['mood']} · 고정 해석",
        "sections": [
            {"id": "theme", "title": "한 해의 주제 (정통 사주)", "body": h1},
            {"id": "half", "title": "상·하반기 흐름", "body": h2},
            {"id": "life", "title": "재물·애정·사회운", "body": h3},
            {"id": "roadmap", "title": "실천 로드맵·평생과의 연결", "body": h4},
        ],
    }


def build_five_element_themes(result: SajuResult, birth: date | None = None) -> dict[str, Any]:
    """Stable traditional five-element deep dive."""
    birth = birth or date(1990, 1, 1)
    t = _tone(result)
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    seed = _stable_seed_from_chart(result, birth, "five_v2")
    yong = result.yongsin.element_ko if result.yongsin else "균형"
    yong_reason = result.yongsin.reason if result.yongsin else "오행 균형을 맞추는 방향이 유익합니다."

    g1 = _expand(
        f"【총평 · 정통 사주 원국】 당신의 일간은 {result.day_master}으로, {nature} 성향이 사주의 중심축입니다. "
        f"년·월·일·시 네 기둥의 기운이 모여 고유한 패턴을 이루며, 오행 분포는 {_elems_line(result)}입니다. "
        f"두드러지는 기운은 {_strong_ko(result)}, 비어 있거나 약한 쪽은 {_weak_ko(result)}로 읽힙니다. "
        f"전체 톤은 {t['adj']}이며, 성공 패턴은 ‘한 번에 완성’보다 ‘방향 설정 후 반복 개선’에 가깝습니다. "
        f"용신 관점에서는 {yong}이(가) 균형을 돕는 열쇠로 보이며, {yong_reason} "
        f"스스로를 몰아붙이기보다 강점은 드러내고 약점은 루틴·협력·도구로 보완할 때 "
        f"장기 성과가 안정됩니다. 명리학에서 말하는 일간의 주체성—‘내가 세상을 어떻게 해석하는가’—이 "
        f"이 사주의 첫 문장입니다. 동일 원국이면 이 총평의 골격은 항상 같습니다.",
        seed,
        750,
        1000,
    )
    g1b = _expand(
        f"【재물 특성 · 평생 재물 패턴】 재물은 {t['wealth']} 방식으로 모이고 새기 쉽습니다. "
        f"충동 매매·과시성 소비가 약점이 될 수 있으므로 월 단위 예산을 숫자로 고정하세요. "
        f"수입이 늘어나는 시기는 대개 전문성·신뢰가 외부에 알려질 때이며, "
        f"공동 투자·보증은 문서와 한도를 명확히 하지 않으면 인간관계 갈등으로 번질 수 있습니다. "
        f"오행상 {_weak_ko(result)}을 상징하는 색·공간·취미를 생활에 넣으면 결정 피로가 줄어 "
        f"재물 판단이 맑아지는 경우가 많습니다. 평생 관점에서는 ‘한 방’보다 ‘재현 가능한 현금흐름’이 "
        f"이 사주의 재물 해법입니다. 비상금·분산·기록—이 세 가지는 시대가 바뀌어도 유효한 용신적 실천입니다.",
        seed + 7,
        750,
        1000,
    )
    g1c = _expand(
        f"【애정 특성 · 관계의 구조】 사랑에서는 {t['love']}이 매력이자 숙제입니다. "
        f"초반 호감은 빠르게 생겨도, 지속 관계에서는 소통 방식의 차이가 갈등을 만듭니다. "
        f"상대에게 추측하게 두지 말고 원하는 바를 구체적으로 말하는 연습이 필요합니다. "
        f"질투·불안이 올라올 때는 상대 추궁보다 자신의 일정·수면·스트레스를 먼저 점검하세요. "
        f"좋은 인연은 대개 일·취미·학습의 연장선에서 자연스럽게 연결됩니다. "
        f"부부·동반 관계에서는 로맨스보다 운영 체계(가계·역할·경계)가 애정을 지탱합니다. "
        f"일간 {result.day_master}의 {nature} 기질을 이해해 주는 상대와는 회복 속도가 빠릅니다.",
        seed + 14,
        750,
        1000,
    )
    # Combine wealth+love into one group body as design had 3 groups - keep 3 groups but each much longer
    g1_full = g1 + "\n\n" + g1b + "\n\n" + g1c
    if len(g1_full) > 2800:
        g1_full = g1_full[:2800]

    g2 = _expand(
        f"【직업 특성】 적성 분야로는 {t['career']}가 잘 맞습니다. "
        f"조직 안에서는 {t['social']} 역할로 존재감이 생기고, "
        f"프리랜스·창업이라면 전문 영역을 좁혀 ‘이 문제는 이 사람에게’라는 포지션이 유리합니다. "
        f"이직·전직 시 연봉만이 아니라 성장 곡선·동료 문화·출퇴근 리듬을 함께 보세요. "
        f"사주상 강한 기운({_strong_ko(result)})을 쓰는 업무를 맡으면 피로 대비 성과 효율이 높습니다. "
        f"평생 직업은 하나가 아니라 역량의 연속이므로, 3년 단위로 이력의 스토리를 재정의하세요. "
        f"정체기에는 스킬을, 도약기에는 협상·공개 성과를 노리는 리듬이 이 사주와 잘 맞습니다.",
        seed + 21,
        700,
        1000,
    )
    g2b = _expand(
        f"【기질 특성 · 평생의 의사결정 스타일】 기질의 핵심은 {t['mood']}입니다. "
        f"압박이 들어올 때 당신은 {_pick(seed, ['먼저 구조를 짜고', '관계를 조율하고', '정보를 모은 뒤', '원칙을 세운 뒤'])} "
        f"움직이는 편입니다. 장점은 한 번 방향을 잡으면 꾸준함이 생긴다는 점이고, "
        f"단점은 완벽을 기다리다 시작이 늦거나, 확신이 과해 피드백을 닫는 순간이 있다는 점입니다. "
        f"의사결정 전에 ‘반대 의견 한 줄’을 스스로 써 보는 습관이 기질을 성숙하게 만듭니다. "
        f"{t['virtue']}를 의식하면 극단으로 치우치지 않습니다. "
        f"동일 사주에서는 이 기질 서술이 고정되어, 매일 바뀌는 일운과 구분됩니다.",
        seed + 28,
        700,
        1000,
    )
    g2_full = g2 + "\n\n" + g2b

    g3 = _expand(
        f"【성격 특성】 겉으로 드러나는 인상과 속마음은 결이 다를 수 있습니다. "
        f"겉은 {t['adj']}해 보여도, 속으로는 안정과 인정을 동시에 원하는 타입입니다. "
        f"스트레스 해소에는 {_pick(seed + 3, ['혼자만의 정리 시간', '가벼운 운동', '기록과 메모', '자연·산책'])}이 "
        f"특히 효과적입니다. 화를 삼키기보다 ‘사실-감정-요청’ 세 문장으로 표현하면 관계가 덜 꼬입니다. "
        f"건강 면에서는 {t['body']}에 주기적 관심을 두는 것이 좋고, 과로는 판단 오류로 이어지기 쉽습니다. "
        f"성격은 운명을 가두는 틀이 아니라, 다루는 법에 따라 확장되는 도구입니다.",
        seed + 35,
        700,
        1000,
    )
    g3b = _expand(
        f"【사회적 특성 · 평판과 인연】 사회적으로는 {t['social']} 포지션이 자연스럽습니다. "
        f"많은 사람과 얕게 어울리기보다, 신뢰할 수 있는 소수와의 깊은 연결이 자산을 만듭니다. "
        f"모임에서는 경청 후 한 가지 제안을 하는 패턴이 호감을 줍니다. "
        f"평판은 재능보다 ‘약속 이행’에서 쌓이므로 작은 기한도 지키세요. "
        f"갈등이 생기면 공개 자리에서 이기려 하지 말고 1:1로 사실 관계를 맞추는 편이 "
        f"장기 사회적 자본을 지킵니다. 용신 {yong}을 의식한 만남·장소 선택은 "
        f"인연의 질을 높이는 현실적 방법이 됩니다. "
        f"이 사회적 해석 역시 동일 원국 기준 고정 텍스트입니다.",
        seed + 42,
        700,
        1000,
    )
    g3_full = g3 + "\n\n" + g3b

    return {
        "title": "오행·정통 사주 심층 해설 (고정)",
        "day_master": result.day_master,
        "elements": result.elements,
        "groups": [
            {
                "id": "core_wealth_love",
                "title": "총평 · 재물 · 애정 특성",
                "body": g1_full if len(g1_full) <= 3000 else g1_full[:3000],
            },
            {
                "id": "career_temperament",
                "title": "직업 · 기질 특성",
                "body": g2_full if len(g2_full) <= 2200 else g2_full[:2200],
            },
            {
                "id": "personality_social",
                "title": "성격 · 사회적 특성",
                "body": g3_full if len(g3_full) <= 2200 else g3_full[:2200],
            },
        ],
    }


def build_life_reading(result: SajuResult, birth: date, gender: str) -> dict[str, Any]:
    """Lifetime reading — fully deterministic for same birth chart."""
    t = _tone(result)
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    seed = _stable_seed_from_chart(result, birth, gender, "life_v2")
    yong = result.yongsin.element_ko if result.yongsin else "균형"

    early = _expand(
        f"【초년운 (대략 0–30대) · 평생 운세】 "
        f"초년에는 {nature} 기질이 형성되며 환경과 부모·스승의 영향이 크게 각인됩니다. "
        f"핵심 과제는 정체성 확립과 기초 체력·학업·사회 규범 학습입니다. "
        f"실수가 두렵더라도 다양한 시도를 남겨 두는 것이 중년의 선택지를 넓힙니다. "
        f"초년에 겪은 부족함({_weak_ko(result)})은 약점이 아니라 이후 전문 영역의 동기가 되기도 합니다. "
        f"가족 갈등은 단절보다 ‘거리 두기 + 자기 루틴’으로 완충하는 편이 후일에 도움이 됩니다. "
        f"오행상 {_strong_ko(result)}이 일찍 드러나면 주변의 기대를 받기 쉽고, "
        f"그에 따른 부담을 스스로 조절하는 법을 배워야 합니다. "
        f"동일 생년월일시 기준 이 초년 서술은 고정됩니다.",
        seed,
        700,
        1000,
    )
    mid = _expand(
        f"【중년운 (대략 30–50대)】 "
        f"중년은 성과와 책임이 겹치는 시기입니다. {t['career']} 분야에서 직함·수입·영향력이 구체화되기 쉽고, "
        f"동시에 건강·가족 부양 부담이 올라갑니다. 성패는 ‘거절할 줄 아는 용기’와 ‘장기 파트너십’에 달려 있습니다. "
        f"대운 변화 구간에서는 이직·이사·사업 확장을 한 가지씩만 처리하세요. "
        f"중년에 쌓은 평판과 현금 흐름이 말년의 여유를 결정합니다. "
        f"{t['wealth']} 원칙을 지키면 소득 변동기를 완충할 수 있고, "
        f"{t['love']}을 놓치면 성공해도 고립감을 느낄 수 있습니다. "
        f"일간 {result.day_master}의 {nature} 성향은 중년에 ‘전문성 브랜드’로  thrives 하기 쉽습니다."
        .replace(" thrives ", "자리 잡"),
        seed + 9,
        700,
        1000,
    )
    late = _expand(
        f"【말년운 (대략 50대 이후)】 "
        f"말년에는 확장보다 정리와 전승이 테마입니다. 건강 관리, 자산 배분, 관계의 화해·경계가 삶의 질을 가릅니다. "
        f"젊은 세대에게 경험을 나누는 역할({t['social']})에서 보람을 느끼기 쉽습니다. "
        f"고독을 두려워하기보다 취미·학습·봉사로 일상을 구조화하면 정신 건강이 안정됩니다. "
        f"재산은 ‘보관’만이 아니라 ‘의미 있는 사용’의 관점으로 보세요. "
        f"용신 {yong}을 의식한 주거·여행·인간관계는 말년의 만족도를 높입니다. "
        f"평생 운세의 마지막 장은 ‘성취의 크기’보다 ‘후회 없는 선택’으로 읽히는 사주입니다.",
        seed + 18,
        700,
        1000,
    )

    money = _expand(
        f"【금전운 · 평생】 금전 패턴은 {t['wealth']}에 가깝습니다. "
        f"큰 한 방을 노리기보다 현금흐름·비상금·분산의 삼각형을 지키세요. "
        f"동업·보증은 관계를 상하게 하는 대표 원인이므로 문서·한도·종료 조건을 필수화하세요. "
        f"수입 정체기에는 지출 구조부터, 호황기에는 생활 수준 인플레이션을 경계하세요.\n\n"
        f"【행운·기회】 행운은 무작위로 보이지만 실제로는 ‘준비된 노출’에서 옵니다. "
        f"{t['mood']}가 드러나는 활동—포트폴리오, 발표, 커뮤니티—에 정기적으로 모습을 보이세요. "
        f"용신 {yong}을 의식한 일정은 심리적 안정과 판단력을 높입니다.\n\n"
        f"【팔복·삶의 여유】 복은 돈만이 아니라 시간·건강·관계·수면의 합입니다. "
        f"주 1회 완전 오프 반나절, 감사 일기, 정기 검진, 가까운 이들과의 식사가 "
        f"팔복궁을 채우는 현실적 방법입니다. 이 금전·행운 해석은 동일 사주에서 고정됩니다.",
        seed + 27,
        750,
        1000,
    )

    love = _expand(
        f"【연애운 · 평생 패턴】 연애에서는 {t['love']}이 매력 포인트입니다. "
        f"초반 이상화 후 급격한 실망을 줄이려면 3개월 안에 가치관(돈·가족·시간·갈등 해결)을 "
        f"대화로 맞춰 보는 것이 좋습니다. 집착과 회피 사이를 오가지 않도록 연락·만남 빈도를 합의하세요.\n\n"
        f"【궁합 관점】 궁합은 점수가 아니라 갈등 회복 속도입니다. "
        f"당신과 잘 맞는 상대는 {_strong_ko(result)} 기운을 이해해 주고 "
        f"{_weak_ko(result)} 영역을 비난하지 않는 사람입니다. "
        f"너무 비슷한 기질끼리만 모이면 성장이 멈출 수 있으니 건강한 차이도 존중하세요.\n\n"
        f"【부부·동반자 궁】 장기 동반에서는 로맨스보다 운영 체계가 중요합니다. "
        f"가계 역할, 집안일, 부모 부양, 주거 계획을 주기적으로 업데이트하세요. "
        f"싸움 후 24시간 내 ‘사실 확인 + 사과 + 다음 약속’ 루틴이 부부궁을 단단하게 합니다. "
        f"서로의 개별 공간·취미를 허용할 때 애착이 더 오래 갑니다. 고정 해석입니다.",
        seed + 36,
        750,
        1000,
    )

    career = _expand(
        f"【성격과 강점 · 평생】 {nature} 성향 위에 {t['adj']} 에너지가 얹혀 있습니다. "
        f"강점은 {_pick(seed, ['한 번 맡은 일의 책임감', '상황 파악 속도', '사람 사이의 조율', '완성도에 대한 집요함'])}이고, "
        f"약점은 {_pick(seed + 1, ['과한 자기비판', '시작 지연', '감정 억제 후 폭발', '거절 못 함'])}으로 나타날 수 있습니다. "
        f"약점을 ‘고치기’보다 ‘장치로 우회’할 때 성장이 빠릅니다.\n\n"
        f"【적성】 적성 키워드는 {t['career']}입니다. "
        f"같은 직무라도 사람 중심/데이터 중심/제작 중심 중 어디에 에너지를 쓰는지 관찰하세요. "
        f"적성과 반대되는 일로 성공해도 소진이 빨라 중년 전환 비용이 커질 수 있습니다.\n\n"
        f"【직업운】 직업 성장은 직선이 아니라 계단형입니다. "
        f"정체기에는 스킬을, 도약기에는 협상·이직·공개 성과를 노리세요. "
        f"조직이라면 멘토 1·동료 2·후배 1 구도가 안정적이고, "
        f"독립·창업이라면 6개월 생활비와 최소 고객 검증을 선행 조건으로 두세요. "
        f"평생 직업은 역량의 연속—동일 사주에서 이 직업 서술은 고정됩니다.",
        seed + 45,
        750,
        1000,
    )

    return {
        "title": "인생풀이·평생 운세 상세 (고정)",
        "subtitle": f"일간 {result.day_master} · 용신 {yong} · 동일 원국 동일 해석",
        "groups": [
            {
                "id": "life_stages",
                "title": "초년 · 중년 · 말년운",
                "sections": [
                    {"id": "early", "title": "초년운", "body": early},
                    {"id": "mid", "title": "중년운", "body": mid},
                    {"id": "late", "title": "말년운", "body": late},
                ],
            },
            {
                "id": "fortune_wealth",
                "title": "금전 · 행운 · 삶의 여유(팔복)",
                "sections": [
                    {"id": "money_luck", "title": "금전·행운·여유", "body": money},
                ],
            },
            {
                "id": "love_bond",
                "title": "연애 · 궁합 · 부부궁",
                "sections": [
                    {"id": "love_marriage", "title": "연애·궁합·동반", "body": love},
                ],
            },
            {
                "id": "self_career",
                "title": "성격 · 적성 · 직업운",
                "sections": [
                    {"id": "personality_career", "title": "성격·적성·직업", "body": career},
                ],
            },
        ],
    }


def build_full_report(
    result: SajuResult,
    birth: date,
    gender: str,
    *,
    as_of: date | None = None,
) -> dict[str, Any]:
    return {
        "pillars": {
            "year": {"stem": result.pillars.year.stem, "branch": result.pillars.year.branch},
            "month": {"stem": result.pillars.month.stem, "branch": result.pillars.month.branch},
            "day": {"stem": result.pillars.day.stem, "branch": result.pillars.day.branch},
            "hour": (
                {"stem": result.pillars.hour.stem, "branch": result.pillars.hour.branch}
                if result.pillars.hour
                else None
            ),
        },
        "day_master": result.day_master,
        "elements": result.elements,
        "weak_elements": result.weak_elements,
        "strong_elements": result.strong_elements,
        "yongsin": (
            {
                "element": result.yongsin.element,
                "element_ko": result.yongsin.element_ko,
                "reason": result.yongsin.reason,
                "lifestyle": result.yongsin.lifestyle,
            }
            if result.yongsin
            else None
        ),
        "daily": build_daily_long(result, as_of),  # variable by date
        "new_year_2026": build_year_fortune(result, birth, 2026),  # stable
        "five_element": build_five_element_themes(result, birth),  # stable
        "life_reading": build_life_reading(result, birth, gender),  # stable
    }
