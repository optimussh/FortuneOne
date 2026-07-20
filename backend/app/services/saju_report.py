"""
Long-form Korean saju reports: daily, new-year (2026), five-element themes, life reading.
Content is template-based and personalised by day_master / elements / birth year.
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
        "career": "기획, 교육, 의료, 콘텐츠, 환경, 스타트업",
        "love": "솔직하고 따뜻한 표현",
        "wealth": "씨앗을 심는 투자와 장기 성장",
        "social": "네트워킹과 아이디어 공유",
    },
    "fire": {
        "adj": "열정·표현",
        "mood": "가시성과 영향력",
        "career": "마케팅, 공연, 영업, 미디어, 브랜드",
        "love": "설렘과 적극적 어필",
        "wealth": "단기 성과와 가시적 수익",
        "social": "리더십·분위기 메이킹",
    },
    "earth": {
        "adj": "안정·신뢰",
        "mood": "기반과 지속",
        "career": "운영, 재무, 부동산, 행정, HR, 품질",
        "love": "신뢰와 책임감 있는 관계",
        "wealth": "저축·자산 축적·리스크 관리",
        "social": "중재자·버팀목 역할",
    },
    "metal": {
        "adj": "결단·정리",
        "mood": "구조와 완성",
        "career": "법률, 엔지니어링, 감사, 전략, 전문직",
        "love": "원칙과 진정성",
        "wealth": "효율·구조화·고부가 가치",
        "social": "명확한 경계와 기준",
    },
    "water": {
        "adj": "흐름·직관",
        "mood": "유연과 성찰",
        "career": "연구, 상담, 물류, 데이터, 해외, 예술",
        "love": "깊이 있는 공감과 경청",
        "wealth": "순환·현금흐름·정보 기반 판단",
        "social": "조용한 영향력·조율",
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


def _seed(*parts: Any) -> int:
    s = 0
    for p in parts:
        for ch in str(p):
            s = (s * 131 + ord(ch)) & 0x7FFFFFFF
    return s


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)] if options else ""


def _el(result: SajuResult) -> str:
    return STEM_ELEMENT.get(result.day_master, "earth")


def _tone(result: SajuResult) -> dict[str, str]:
    return ELEMENT_TONE[_el(result)]


def _weak_ko(result: SajuResult) -> str:
    if not result.weak_elements:
        return "균형"
    return ", ".join(ELEMENT_KO.get(e, e) for e in result.weak_elements)


def _strong_ko(result: SajuResult) -> str:
    if not result.strong_elements:
        return "고른 분포"
    return ", ".join(ELEMENT_KO.get(e, e) for e in result.strong_elements)


def build_daily_long(result: SajuResult, as_of: date | None = None) -> dict[str, Any]:
    d = as_of or date.today()
    t = _tone(result)
    seed = _seed(result.day_master, d.isoformat(), "daily")
    scores = result.daily.scores
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")

    overview = (
        f"오늘은 일간 {result.day_master}({nature} 기질)을 기준으로 보면, "
        f"{t['mood']}의 결이 하루의 바탕을 이룹니다. "
        f"사주 원국에서 상대적으로 강한 기운은 {_strong_ko(result)}이고, "
        f"보완이 필요한 쪽은 {_weak_ko(result)}입니다. "
        f"따라서 무리하게 속도를 올리기보다, {t['adj']}의 강점을 살리되 "
        f"부족한 기운을 생활 루틴으로 메우는 하루가 유리합니다. "
        f"총운 점수 {scores.get('overall', 70)}점을 중심으로 보면, "
        f"오전에는 집중·정리가, 오후에는 대인·조율이 잘 맞는 리듬일 가능성이 큽니다. "
        f"작은 약속 하나도 명확히 하고, 감정 소모가 큰 논쟁은 하루 미루는 편이 득이 됩니다."
    )
    wealth = (
        f"재물 흐름(점수 {scores.get('money', 65)})은 {t['wealth']} 관점에서 바라보는 것이 좋습니다. "
        f"큰 지출·계약·투자 결정은 가능하면 자료를 한 번 더 검토한 뒤 진행하세요. "
        f"예상치 못한 수입보다는 ‘새는 돈’을 막는 점검—구독, 수수료, 미사용 서비스—이 "
        f"오늘 재물운을 실질적으로 올려 줍니다. "
        f"오후에 숫자 관련 업무(정산, 견적, 예산)를 배치하면 실수가 줄어듭니다. "
        f"주변의 금전 부탁에는 선뜻 응답하기보다 여유와 원칙을 지키세요."
    )
    love = (
        f"애정·관계 운(점수 {scores.get('love', 65)})은 {t['love']}이 핵심 키워드입니다. "
        f"가까운 사람에게는 짧은 안부라도 진심을 담아 전하면 오해가 풀리기 쉽습니다. "
        f"솔로라면 무리한 어필보다 공통 관심사에서의 자연스러운 대화가 유리하고, "
        f"연인·배우자와의 사이에서는 ‘옳고 그름’보다 ‘서로의 피로도’를 먼저 살피는 태도가 "
        f"관계를 부드럽게 만듭니다. 감정적으로 예민해질 수 있는 밤 시간대에는 "
        f"중요한 결정보다 휴식과 가벼운 산책을 권합니다."
    )
    work = (
        f"일과 건강(건강 점수 {scores.get('health', 65)}) 측면에서는 {t['career']} 계열의 "
        f"업무 방식이 잘 맞습니다. 오늘은 완성도보다 ‘진행 중인 일의 한 칸 전진’이 중요합니다. "
        f"회의가 있다면 결론 문장을 미리 적어 두면 영향력이 커집니다. "
        f"컨디션은 수분 섭취와 짧은 스트레칭으로 유지하고, 야근을 강행하기보다 "
        f"내일로 넘겨도 되는 일을 과감히 분류하세요. "
        f"행운 색 {result.daily.lucky.get('color', '청색')}, "
        f"방향 {result.daily.lucky.get('direction', '동')}을 소품·동선에 살짝 반영해 보세요."
    )
    advice = (
        f"【오늘의 한 줄】 {t['adj']}의 강점을 쓰되, {_weak_ko(result)} 기운을 생활에서 보강할 것. "
        f"【피하기】 감정적인 큰 결정, 검증 없는 금전 약속. "
        f"【실천】 아침 10분 계획 정리 + 저녁 감사 한 가지 기록."
    )
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


def build_new_year_2026(result: SajuResult, birth: date) -> dict[str, Any]:
    """New year report fixed to calendar year 2026."""
    year = 2026
    t = _tone(result)
    seed = _seed(result.day_master, birth.isoformat(), year, "ny")
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    age_in_2026 = year - birth.year

    h1 = (
        f"2026년은 일간 {result.day_master}—{nature} 기질—을 가진 당신에게 "
        f"‘{t['mood']}’를 주제로 한 해가 될 가능성이 큽니다. "
        f"만 나이 기준 약 {age_in_2026}세 전후의 시간대에서, "
        f"사주상 강한 기운({_strong_ko(result)})은 성과의 엔진이 되고, "
        f"약한 기운({_weak_ko(result)})은 보완 과제로 반복 등장할 수 있습니다. "
        f"상반기에는 기반 다지기와 관계 정리가, 하반기에는 선택과 확장이 두드러질 수 있으니 "
        f"연초부터 ‘올해 꼭 끝낼 일 3가지 / 내려놓을 일 3가지’를 적어 두는 것을 권합니다. "
        f"2026년의 키워드는 속도보다 방향, 과시보다 지속 가능한 루틴입니다."
    )
    h2 = (
        f"【상반기(1–6월)】 학습·재정 점검·건강 검진·인간관계 경계 설정에 힘을 주세요. "
        f"{t['wealth']} 관점의 재설계가 연말 안정감으로 이어집니다. "
        f"충동 이직·무리한 확장은 상반기보다 하반기 검증 후가 낫습니다. "
        f"【하반기(7–12월)】 준비해 둔 프로젝트가 가시화되기 쉽습니다. "
        f"{t['career']} 분야에서 이름·포트폴리오·실적을 드러내면 기회가 붙습니다. "
        f"다만 과로는 말년 피로로 누적되므로 휴식 일정을 캘린더에 선점하세요."
    )
    h3 = (
        f"재물운은 ‘한 번에 크게’보다 ‘매월 규칙적으로’가 2026년의 정답에 가깝습니다. "
        f"고정비 재협상, 비상금 3–6개월 치 확보, 소득원 분산을 목표로 잡으세요. "
        f"애정·가족운에서는 {t['love']}이 관계를 살리는 열쇠입니다. "
        f"중요한 약속·결혼·동거·이사 결정은 감정 고조기보다 한 템포 쉬어 가며 조율하세요. "
        f"사회적 평판은 {t['social']} 역할에서 쌓이니, 모임·협업에서 약속을 지키는 태도가 "
        f"연말 평판 자산이 됩니다."
    )
    h4 = (
        f"【2026 실천 로드맵】\n"
        f"1) 1월: 목표·예산·건강 베이스라인 측정\n"
        f"2) 3–4월: 스킬·자격·포트폴리오 보강 ({t['career']})\n"
        f"3) 6월: 중간 점검—버린 일 / 키울 일 재분류\n"
        f"4) 9–10월: 가시적 성과 발표·협상·계약\n"
        f"5) 12월: 감사 정리와 2027 씨앗 심기\n"
        f"용신 힌트({result.yongsin.element_ko if result.yongsin else '균형'})를 "
        f"공간·옷·일정에  assiduously 반영하면 한 해의 마찰이 줄어듭니다."
    )
    # fix typo assiduously -> 꾸준히
    h4 = h4.replace(" assiduously ", " 꾸준히 ")

    return {
        "year": year,
        "title": "2026 신년 운세 심층 해설",
        "subtitle": f"일간 {result.day_master} · {t['mood']}",
        "sections": [
            {"id": "theme", "title": "한 해의 주제", "body": h1},
            {"id": "half", "title": "상·하반기 흐름", "body": h2},
            {"id": "life", "title": "재물·애정·사회운", "body": h3},
            {"id": "roadmap", "title": "실천 로드맵", "body": h4},
        ],
    }


def build_five_element_themes(result: SajuResult) -> dict[str, Any]:
    """Grouped: 총평·재물·애정 / 직업·기질 / 성격·사회."""
    t = _tone(result)
    el = _el(result)
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    seed = _seed(result.day_master, result.elements, "five")

    g1 = (
        f"【총평】 당신의 일간은 {result.day_master}으로, {nature} 성향이 사주의 중심축입니다. "
        f"오행 분포상 두드러지는 쪽은 {_strong_ko(result)}, 비어 있거나 약한 쪽은 {_weak_ko(result)}입니다. "
        f"전체적으로 {t['adj']}의 에너지가 삶을 이끄는 주조색이며, "
        f"성공 패턴은 ‘한 번에 완성’보다 ‘방향 설정 후 반복 개선’에 가깝습니다. "
        f"스스로를 몰아붙이기보다, 강점은 드러내고 약점은 시스템(루틴·사람·도구)으로 보완할 때 "
        f"장기 성과가 안정됩니다.\n\n"
        f"【재물 특성】 재물은 {t['wealth']} 방식으로 모이고 새기 쉽습니다. "
        f"충동 매매·과시성 소비가 약점이 될 수 있으므로, 월 단위 예산을 숫자로 고정하세요. "
        f"수입이 늘어나는 시기는 대개 전문성·신뢰가 외부에 알려질 때입니다. "
        f"공동 투자·보증은 문서와 한도를 명확히 하지 않으면 인간관계 갈등으로 번질 수 있습니다. "
        f"오행상 {_weak_ko(result)}을 상징하는 색·공간·취미를 생활에 넣으면 "
        f"결정 피로가 줄어 재물 판단이 맑아지는 경우가 많습니다.\n\n"
        f"【애정 특성】 사랑에서는 {t['love']}이 매력이자 숙제입니다. "
        f"초반 호감은 빠르게 생겨도, 지속 관계에서는 소통 방식의 차이가 갈등을 만듭니다. "
        f"상대에게 ‘추측하게 두지 말고’ 원하는 바를 구체적으로 말하는 연습이 필요합니다. "
        f"질투·불안이 올라올 때는 상대를 추궁하기보다 자신의 일정·수면·스트레스를 먼저 점검하세요. "
        f"좋은 인연은 대개 일·취미·학습의 연장선에서 자연스럽게 연결됩니다."
    )
    g2 = (
        f"【직업 특성】 적성 분야로는 {t['career']}가 잘 맞습니다. "
        f"조직 안에서는 {t['social']} 역할로 존재감이 생기고, "
        f"프리랜스·창업이라면 전문 영역을 좁혀 ‘이 문제는 이 사람에게’라는 포지션을 만드는 것이 유리합니다. "
        f"이직·전직을 고민 중이라면 연봉만이 아니라 성장 곡선·동료 문화·출퇴근 리듬을 함께 보세요. "
        f"사주상 강한 기운({_strong_ko(result)})을 쓰는 업무를 맡으면 피로 대비 성과 효율이 높습니다.\n\n"
        f"【기질 특성】 기질의 핵심은 {t['mood']}입니다. "
        f"압박이 들어올 때 당신은 {_pick(seed, ['먼저 구조를 짜고', '관계를 조율하고', '정보를 모은 뒤', '원칙을 세운 뒤'])} "
        f"움직이는 편입니다. 장점은 한 번 방향을 잡으면 꾸준함이 생긴다는 점이고, "
        f"단점은 완벽을 기다리다 시작이 늦거나, 반대로 확신이 과해 피드백을 닫는 순간이 있다는 점입니다. "
        f"의사결정 전에 ‘반대 의견 한 줄’을 스스로 써 보는 습관이 기질을 성숙하게 만듭니다."
    )
    g3 = (
        f"【성격 특성】 겉으로 드러나는 인상과 속마음은 결이 다를 수 있습니다. "
        f"겉은 {t['adj']}해 보여도, 속으로는 안정과 인정을 동시에 원하는 타입입니다. "
        f"스트레스 해소는 사람마다 다르지만, 당신에게는 "
        f"{_pick(seed + 3, ['혼자만의 정리 시간', '가벼운 운동', '기록과 메모', '자연·산책'])}이 "
        f"특히 효과적입니다. 화를 삼키기보다 ‘사실-감정-요청’ 세 문장으로 표현하면 "
        f"관계가 덜 꼬입니다.\n\n"
        f"【사회적 특성】 사회적으로는 {t['social']} 포지션이 자연스럽습니다. "
        f"많은 사람과 얕게 어울리기보다, 신뢰할 수 있는 소수와의 깊은 연결이 자산을 만듭니다. "
        f"모임에서는 경청 후 한 가지 제안을 하는 패턴이 호감을 줍니다. "
        f"평판은 재능보다 ‘약속 이행’에서 쌓이므로, 작은 기한도 지켜 보세요. "
        f"갈등이 생기면 공개 자리에서 이기려 하지 말고, 1:1로 사실 관계를 맞추는 편이 "
        f"장기적으로 사회적 자본을 지킵니다."
    )
    return {
        "title": "오행 사주 심층 해설",
        "day_master": result.day_master,
        "elements": result.elements,
        "groups": [
            {
                "id": "core_wealth_love",
                "title": "총평 · 재물 · 애정 특성",
                "body": g1,
            },
            {
                "id": "career_temperament",
                "title": "직업 · 기질 특성",
                "body": g2,
            },
            {
                "id": "personality_social",
                "title": "성격 · 사회적 특성",
                "body": g3,
            },
        ],
    }


def build_life_reading(result: SajuResult, birth: date, gender: str) -> dict[str, Any]:
    """인생풀이: 초중말년 / 금전·행운 / 연애·부부 / 성격·적성·직업 — grouped long text."""
    t = _tone(result)
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    seed = _seed(result.day_master, birth.year, gender, "life")
    yong = result.yongsin.element_ko if result.yongsin else "균형"

    early = (
        f"【초년운 (대략 0–30대 전후)】 초년에는 {nature} 기질이 형성되며, "
        f"환경과 부모님·스승의 영향이 크게 각인됩니다. "
        f"이 시기의  thrives 과제는 ‘정체성 확립’과 ‘기초 체력·학업·사회 규범 학습’입니다. "
        f"실수가 두렵더라도 다양한 시도를 남겨 두는 것이 중년의 선택지를 넓힙니다. "
        f"초년에 겪은 부족함({_weak_ko(result)})은 약점이 아니라 이후 전문 영역의 동기가 되기도 합니다. "
        f"가족과의 갈등은 단절보다 ‘거리 두기 + 자기 루틴’으로 완충하는 편이 후일에 도움이 됩니다."
    ).replace(" thrives ", "핵심 ")
    mid = (
        f"【중년운 (대략 30–50대)】 중년은 성과와 책임이 겹치는 시기입니다. "
        f"{t['career']} 분야에서 직함·수입·영향력이 구체화되기 쉽고, "
        f"동시에 건강·가족 부양 부담이 올라갑니다. "
        f"이 구간의 성패는 ‘거절할 줄 아는 용기’와 ‘장기 파트너십’에 달려 있습니다. "
        f"대운 흐름상 변화 구간에서는 이직·이사·사업 확장을 한 가지씩만 처리하세요. "
        f"중년에 쌓은 평판과 현금 흐름이 말년의 여유를 결정합니다."
    )
    late = (
        f"【말년운 (대략 50대 이후)】 말년에는 확장보다 정리와 전승이 테마입니다. "
        f"건강 관리, 자산 배분, 관계의 화해·경계가 삶의 질을 가릅니다. "
        f"젊은 세대에게 경험을 나누는 역할({t['social']})에서 보람을 느끼기 쉽습니다. "
        f"고독을 두려워하기보다, 취미·학습·봉사로 일상을 구조화하면 "
        f"말년의 정신 건강이 안정됩니다. 재산은 ‘보관’만이 아니라 ‘의미 있는 사용’의 관점으로 보세요."
    )

    money = (
        f"【금전운】 금전 패턴은 {t['wealth']}에 가깝습니다. "
        f"큰 한 방을 노리기보다 현금흐름·비상금·분산 투자의 삼각형을 지키세요. "
        f"동업·보증은 관계를 상하게 하는 대표 원인이므로 문서·한도·종료 조건을 필수화하세요. "
        f"수입 정체기에는 지출 구조부터 손보고, 호황기에는 생활 수준 인플레이션을 경계하세요.\n\n"
        f"【행운·기회】 행운은 무작위로 보이지만, 실제로는 ‘준비된 노출’에서 옵니다. "
        f"{t['mood']}가 드러나는 활동—포트폴리오, 발표, 커뮤니티—에 정기적으로 모습을 보이세요. "
        f"용신 {yong}을 의식한 일정(장소·색·만남)은 심리적 안정과 함께 판단력을 높여 줍니다.\n\n"
        f"【팔복·삶의 여유】 복은 돈만이 아니라 시간·건강·관계·수면의 합입니다. "
        f"주 1회 ‘완전 오프’ 반나절을 지키면 장기 성과가 오히려 올라갑니다. "
        f"감사 일기, 정기 검진, 가까운 이들과의 식사 같은 작은 복 루틴을 제도화하세요."
    )
    love = (
        f"【연애운】 연애에서는 {t['love']}이 매력 포인트입니다. "
        f"초반 이상화 후 급격한 실망을 줄이려면, 3개월 안에 가치관(돈·가족·시간·갈등 해결)을 "
        f"대화로 맞춰 보는 것이 좋습니다. 집착과 회피 사이를 오가지 않도록 "
        f"연락 주기·만남 빈도를 합의하세요.\n\n"
        f"【궁합 관점】 궁합은 점수가 아니라 ‘갈등 회복 속도’입니다. "
        f"당신과 잘 맞는 상대는 대체로 {_strong_ko(result)} 기운을 이해해 주고, "
        f"{_weak_ko(result)} 영역을 비난하지 않는 사람입니다. "
        f"너무 비슷한 기질끼리만 모이면 성장이 멈출 수 있으니, 건강한 차이도 존중하세요.\n\n"
        f"【부부·동반자 궁】 장기 동반 관계에서는 로맨스보다 운영 체계가 중요합니다. "
        f"가계 역할, 집안일, 부모 부양, 주거 계획을 주기적으로 업데이트하세요. "
        f"싸움 후 24시간 내 ‘사실 확인 + 사과 + 다음 약속’ 루틴이 부부궁을 단단하게 합니다. "
        f"서로의 개별 공간·취미를 허용할 때 애착이 더 오래 갑니다."
    )
    career = (
        f"【성격과 강점】 {nature} 성향 위에 {t['adj']} 에너지가 얹혀 있습니다. "
        f"강점은 {_pick(seed, ['한 번 맡은 일의 책임감', '상황 파악 속도', '사람 사이의 조율', '완성도에 대한 집요함'])}이고, "
        f"약점은 {_pick(seed + 1, ['과한 자기비판', '시작 지연', '감정 억제 후 폭발', '거절 못 함'])}으로 나타날 수 있습니다. "
        f"약점을 ‘고치기’보다 ‘장치로 우회’할 때 성장이 빠릅니다.\n\n"
        f"【적성】 적성 키워드는 {t['career']}입니다. "
        f"같은 직무라도 ‘사람 중심 / 데이터 중심 / 제작 중심’ 중 어디에 에너지를 쓰는지 관찰하세요. "
        f"적성과 반대되는 일로 성공해도 소진이 빨라, 중년에 방향 전환 비용이 커질 수 있습니다.\n\n"
        f"【직업운】 직업 성장은 직선이 아니라 계단형입니다. "
        f"정체기에는 스킬을 쌓고, 도약기에는 협상·이직·공개 성과를 노리세요. "
        f"조직 생활이라면 멘토 1명·동료 협력자 2명·후배 1명 구도를 만들면 안정됩니다. "
        f"독립·창업을 택한다면 6개월 생활비와 최소 고객 검증을 선행 조건으로 두세요. "
        f"평생 직업은 하나가 아니라 ‘역량의 연속’이므로, 3년 단위로 이력의 스토리를 재정의하세요."
    )

    return {
        "title": "인생풀이 상세 사주",
        "subtitle": f"일간 {result.day_master} · 용신 {yong}",
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
        "daily": build_daily_long(result, as_of),
        "new_year_2026": build_new_year_2026(result, birth),
        "five_element": build_five_element_themes(result),
        "life_reading": build_life_reading(result, birth, gender),
    }
