"""
Long-form Korean saju reports — unique paragraphs per section (no filler reuse).

Stable (same chart → same text): 신년, 오행 심층, 인생풀이
Variable by date: 오늘의 운세
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_engine import ELEMENT_KO, STEM_ELEMENT, SajuResult

ELEMENT_TONE: dict[str, dict[str, str]] = {
    "wood": {
        "adj": "생장·확장",
        "mood": "시작과 성장",
        "career": "기획, 교육, 의료, 콘텐츠, 환경, 스타트업, 브랜딩",
        "love": "솔직하고 따뜻한 표현",
        "wealth": "장기 복리와 씨앗형 투자",
        "social": "네트워킹과 아이디어 연결",
        "body": "간·담·눈의 긴장, 근육 과사용",
        "virtue": "인(仁)·추진",
        "color": "청·록",
        "dir": "동·동남",
    },
    "fire": {
        "adj": "열정·표현",
        "mood": "가시성과 영향력",
        "career": "마케팅, 공연, 영업, 미디어, 강의, 브랜드",
        "love": "설렘과 적극적 관심",
        "wealth": "단기 성과 사이클과 가시 수익",
        "social": "분위기 리더십",
        "body": "심장·수면·과열성 피로",
        "virtue": "예(禮)·표현",
        "color": "적·주황",
        "dir": "남",
    },
    "earth": {
        "adj": "안정·신뢰",
        "mood": "기반과 지속",
        "career": "운영, 재무, 부동산, 행정, HR, 품질",
        "love": "책임과 신뢰 기반 관계",
        "wealth": "저축·자산 완충·리스크 관리",
        "social": "중재자·버팀목",
        "body": "비위·소화·습관적 과식",
        "virtue": "신(信)·꾸준함",
        "color": "황·베이지",
        "dir": "중앙·서남",
    },
    "metal": {
        "adj": "결단·정리",
        "mood": "구조와 완성",
        "career": "법률, 엔지니어링, 감사, 전략, 분석 전문직",
        "love": "원칙과 진정성 있는 애정",
        "wealth": "효율·고부가 포지션·구조화",
        "social": "기준과 약속 이행",
        "body": "폐·호흡·피부 건조",
        "virtue": "의(義)·절제",
        "color": "백·은",
        "dir": "서·서북",
    },
    "water": {
        "adj": "흐름·직관",
        "mood": "유연과 성찰",
        "career": "연구, 상담, 데이터, 해외, 예술, 전략",
        "love": "깊이 있는 공감과 경청",
        "wealth": "현금흐름·정보 우위·순환",
        "social": "조용한 조율과 영향력",
        "body": "신장·수분·과로성 피로",
        "virtue": "지(智)·유연",
        "color": "흑·남색",
        "dir": "북",
    },
}

STEM_NATURE = {
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
    s = 2166136261
    for p in parts:
        for ch in str(p):
            s ^= ord(ch)
            s = (s * 16777619) & 0x7FFFFFFF
    return s


def _stable(result: SajuResult, birth: date, *extra: Any) -> int:
    p = result.pillars
    key = (
        f"{p.year.stem}{p.year.branch}{p.month.stem}{p.month.branch}"
        f"{p.day.stem}{p.day.branch}"
    )
    return _seed(result.day_master, key, birth.isoformat(), *extra)


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)] if options else ""


def _el(r: SajuResult) -> str:
    return STEM_ELEMENT.get(r.day_master, "earth")


def _t(r: SajuResult) -> dict[str, str]:
    return ELEMENT_TONE[_el(r)]


def _weak(r: SajuResult) -> str:
    if not r.weak_elements:
        return "비교적 고른 편"
    return ", ".join(ELEMENT_KO.get(e, e) for e in r.weak_elements)


def _strong(r: SajuResult) -> str:
    if not r.strong_elements:
        return "고른 분포"
    return ", ".join(ELEMENT_KO.get(e, e) for e in r.strong_elements)


def _elems(r: SajuResult) -> str:
    return " / ".join(
        f"{ELEMENT_KO[k]} {r.elements.get(k, 0)}"
        for k in ("wood", "fire", "earth", "metal", "water")
    )


def _pillars_line(r: SajuResult) -> str:
    p = r.pillars
    h = f"{p.hour.stem}{p.hour.branch}" if p.hour else "시주미상"
    return f"년{p.year.stem}{p.year.branch} 월{p.month.stem}{p.month.branch} 일{p.day.stem}{p.day.branch} 시{h}"


# ── Daily (changes by date) ───────────────────────────────────────────────


def build_daily_long(result: SajuResult, as_of: date | None = None) -> dict[str, Any]:
    d = as_of or date.today()
    t = _t(result)
    seed = _seed(result.day_master, d.isoformat(), "daily_v3")
    sc = result.daily.scores
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    tip = _pick(
        seed,
        [
            "오전에 중요한 결정을 배치해 보세요.",
            "오후 대인 일정을 앞당기면 흐름이 좋습니다.",
            "저녁엔 정보 입력보다 정리가 유리합니다.",
            "짧은 산책이 판단 오류를 줄여 줍니다.",
        ],
    )

    overview = (
        f"【{d.month}월 {d.day}일 총운】 일간 {result.day_master}({nature}) 기준으로 오늘의 바탕은 "
        f"‘{t['mood']}’입니다. 원국 강약은 강 {_strong(result)} · 약 {_weak(result)}이며, "
        f"오행 분포는 {_elems(result)}입니다. 총운 {sc.get('overall', 70)}점대에서는 "
        f"{t['adj']} 강점을 쓰되 과속은 금물입니다. {tip} "
        f"감정 소모 큰 논쟁은 하루 미루고, 약속은 짧게 확인하세요. "
        f"행운 색 {result.daily.lucky.get('color', t['color'])}, 방향 {result.daily.lucky.get('direction', t['dir'])}을 "
        f"동선에 살짝 반영해도 좋습니다. "
        f"오늘 해석은 날짜가 바뀌면 달라질 수 있는 ‘일운’ 영역입니다."
    )
    wealth = (
        f"【재물】 점수 {sc.get('money', 65)}. 키워드는 {t['wealth']}입니다. "
        f"큰 결제·계약은 숫자 재확인 후, 충동 소비 대신 ‘목록 구매’를 권합니다. "
        f"고정비·구독·수수료처럼 새는 구멍을 막으면 체감 운이 올라갑니다. "
        f"수입 아이디어는 메모만 하고 저녁에 실현 가능성을 검토하세요. "
        f"금전 부탁에는 원칙과 한도를 분명히 하세요. "
        f"{_pick(seed + 1, ['현금 흐름표 한 줄 업데이트', '불필요 구독 1건 점검', '견적 비교 한 번'])}을 실천 과제로 둡니다."
    )
    love = (
        f"【관계】 점수 {sc.get('love', 65)}. {t['love']}이 오늘의 관계 톤입니다. "
        f"가까운 이에게는 추측 대신 확인 질문이 오해를 줄입니다. "
        f"솔로는 공통 관심사 대화가, 커플은 ‘이기고 지는 말’보다 피로도 배려가 유리합니다. "
        f"밤늦은 감정 논쟁은 피하고, 사실-느낌-요청 순으로 말해 보세요. "
        f"{_pick(seed + 2, ['짧은 감사 인사', '경청 후 한 줄 공감', '함께 짧은 산책'])} 한 가지면 충분합니다."
    )
    work = (
        f"【일·건강】 건강 {sc.get('health', 65)}. {t['career']} 방식의 업무가 잘 맞습니다. "
        f"100% 완성보다 ‘제출 가능한 80%’를 먼저 내보내세요. "
        f"회의 전 결론 문장 메모가 영향력을 키웁니다. "
        f"몸 쪽은 {t['body']} 관련 무리를 줄이고 수분·스트레칭을 챙기세요. "
        f"야근 강행보다 내일로 넘겨도 되는 일을 분류하는 날이 효율적입니다."
    )
    advice = (
        f"【가이드】 강점 {t['adj']} 활용 · 보완 {_weak(result)}. "
        f"피하기: 감정 큰 결정, 검증 없는 금전 약속. "
        f"실천: 아침 10분 계획 + 저녁 감사 한 줄. "
        f"일간 {result.day_master}의 {nature} 페이스를 존중하세요."
    )

    return {
        "date": d.isoformat(),
        "title": f"{d.month}월 {d.day}일 오늘의 운세",
        "scores": sc,
        "lucky": result.daily.lucky,
        "sections": [
            {"id": "overview", "title": "총운 해설", "body": overview},
            {"id": "wealth", "title": "재물·실속", "body": wealth},
            {"id": "love", "title": "애정·인간관계", "body": love},
            {"id": "work_health", "title": "일·건강·실천", "body": work},
            {"id": "advice", "title": "오늘 가이드", "body": advice},
        ],
    }


# ── Stable yearly ─────────────────────────────────────────────────────────


def build_new_year_2026(result: SajuResult, birth: date) -> dict[str, Any]:
    return build_year_fortune(result, birth, 2026)


def build_year_fortune(result: SajuResult, birth: date, year: int = 2026) -> dict[str, Any]:
    t = _t(result)
    seed = _stable(result, birth, f"year_{year}_v3")
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    age = year - birth.year
    yong = result.yongsin.element_ko if result.yongsin else "균형"
    yong_r = result.yongsin.reason if result.yongsin else "오행 균형을 의식한 선택이 유익합니다."
    pillars = _pillars_line(result)

    h1 = (
        f"【{year}년 한 해의 주제 · 정통 사주】 "
        f"원국 {pillars}, 일간 {result.day_master}({nature})인 당신에게 {year}년은 "
        f"‘{t['mood']}’가 주제로 작동하는 해입니다. 대략 만 {age}세 전후 시점으로, "
        f"강한 기운 {_strong(result)}은 성과의 엔진이 되고 약한 기운 {_weak(result)}은 "
        f"보완 과제로 반복 등장할 수 있습니다. 오행 {_elems(result)} 분포 위에서 "
        f"{t['virtue']}를 의식한 선택이 마찰을 줄입니다. "
        f"용신 관점의 {yong}—{yong_r} "
        f"연초에는 ‘끝낼 일 3 / 내려놓을 일 3’을 문서로 남겨 방향을 고정하세요. "
        f"이 해의 승부처는 속도가 아니라 방향과 지속 가능한 루틴입니다. "
        f"같은 생년월일시와 같은 연도({year})로 다시 조회해도 이 주제 해석은 동일하게 유지됩니다."
    )
    h2 = (
        f"【{year} 상·하반기】 "
        f"상반기(1–6월)는 학습, 재정 점검, 건강 베이스라인, 관계 경계 설정에 무게를 두는 편이 맞습니다. "
        f"{t['wealth']} 원칙으로 가계를 재설계하면 연말 완충력이 커집니다. "
        f"충동 이직·무리한 확장은 상반기보다 하반기 검증 후가 안전합니다. "
        f"하반기(7–12월)는 준비해 둔 일이 가시화되기 쉽고, {t['career']} 영역에서 "
        f"실적·이름·포트폴리오를 드러내면 기회가 붙습니다. "
        f"다만 과로는 누적 피로로 돌아오므로 휴식 일정을 미리 캘린더에 넣으세요. "
        f"분기마다 목표를 ‘버릴 것/키울 것’으로 재분류하면 대운 리듬과도 맞물리기 쉽습니다. "
        f"일간 {result.day_master}의 {nature} 성향은 ‘한 방’보다 ‘방향 고정 후 반복 개선’에서 진가를 냅니다."
    )
    h3 = (
        f"【{year} 재물·애정·사회】 "
        f"재물은 한 번에 크게보다 매월 규칙이 정답에 가깝습니다. "
        f"고정비 재협상, 비상금 3–6개월, 소득 분산을 연간 목표로 잡으세요. "
        f"애정·가족에서는 {t['love']}이 관계를 살리는 열쇠이며, 결혼·동거·이사 같은 고관여 결정은 "
        f"감정 고조기보다 한 템포 쉬어 조율하는 편이 안전합니다. "
        f"사회적으로는 {t['social']} 역할에서 평판이 쌓이니, 작은 약속도 지켜 연말 신뢰 자산으로 만드세요. "
        f"약한 오행({_weak(result)})을 상징하는 생활 요소—색({t['color']})·방향({t['dir']})·루틴—을 "
        f"보강하면 결정 피로가 줄어 재물·관계 판단이 맑아지는 경우가 많습니다. "
        f"이 영역 해석 역시 {year}년·동일 원국 기준 고정 텍스트입니다."
    )
    h4 = (
        f"【{year} 실천 로드맵】 "
        f"1월: 목표·예산·건강 수치 측정. 3–4월: {t['career']} 관련 스킬·자격·포트폴리오 보강. "
        f"6월: 중간 점검으로 버릴 일과 키울 일 재분류. 9–10월: 성과 공개·협상·계약. "
        f"12월: 감사 정리와 다음 해 씨앗 심기. "
        f"이 로드맵은 인생풀이의 초·중·말년 큰 흐름 위에서 {year}년이라는 한 계단을 오르는 설계입니다. "
        f"{t['adj']} 강점은 드러내고, 약점은 사람·도구·습관으로 보완하십시오. "
        f"용신 {yong}을 일정표에 월 1회 이상 의도적으로 배치하는 것만으로도 한 해의 중심이 잡힙니다. "
        f"동일 사주·동일 연도면 본 로드맵의 골격은 변하지 않습니다."
    )

    return {
        "year": year,
        "title": f"{year} 신년 운세 심층 해설",
        "subtitle": f"일간 {result.day_master} · {t['mood']} · 연도 고정 해석",
        "sections": [
            {"id": "theme", "title": "한 해의 주제 (정통 사주)", "body": h1},
            {"id": "half", "title": "상·하반기 흐름", "body": h2},
            {"id": "life", "title": "재물·애정·사회운", "body": h3},
            {"id": "roadmap", "title": "실천 로드맵", "body": h4},
        ],
    }


# ── Stable five-element ───────────────────────────────────────────────────


def build_five_element_themes(result: SajuResult, birth: date | None = None) -> dict[str, Any]:
    birth = birth or date(1990, 1, 1)
    t = _t(result)
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    seed = _stable(result, birth, "five_v3")
    yong = result.yongsin.element_ko if result.yongsin else "균형"
    yong_r = result.yongsin.reason if result.yongsin else "오행 균형을 맞추는 방향이 유익합니다."
    pillars = _pillars_line(result)
    life = _pick(
        seed,
        ["기준표를 스스로 만드는 사람", "관계를 통해 성장하는 사람", "구조를 세우는 사람", "흐름을 읽는 사람"],
    )

    g1 = (
        f"【총평 · 정통 사주】 원국 {pillars}. 일간 {result.day_master}은 {nature} 성향의 중심축입니다. "
        f"오행 분포 {_elems(result)}에서 두드러짐은 {_strong(result)}, 보완점은 {_weak(result)}입니다. "
        f"전체 톤은 {t['adj']}이며, 성공 패턴은 한 번에 완성보다 방향 설정 후 반복 개선에 가깝습니다. "
        f"용신 {yong}: {yong_r} "
        f"명리에서 일간은 ‘내가 세상을 해석하는 방식’이므로, 이 사주는 {life}으로 읽히는 경우가 많습니다. "
        f"강점은 드러내고 약점은 루틴·협력·도구로 보완할 때 장기 성과가 안정됩니다. "
        f"동일 원국이면 이 총평 골격은 항상 같습니다.\n\n"
        f"【재물 성향】 재물 패턴은 {t['wealth']} 쪽에 가깝습니다. "
        f"충동 매매·과시 소비가 독이 되기 쉬우니 월 예산을 숫자로 고정하세요. "
        f"수입 상승기는 대개 전문성·신뢰가 외부에 알려질 때이며, 동업·보증은 문서·한도·종료 조건이 필수입니다. "
        f"약한 오행({_weak(result)})을 상징하는 생활 요소를 보강하면 결정 피로가 줄어 금전 판단이 맑아질 수 있습니다. "
        f"평생 관점의 해법은 ‘한 방’이 아니라 ‘재현 가능한 현금흐름’입니다.\n\n"
        f"【애정 성향】 관계에서는 {t['love']}이 매력이자 숙제입니다. "
        f"초반 호감 이후에는 소통 방식 차이가 갈등의 원인이 됩니다. "
        f"추측 대신 구체적 요청, 질투가 올라올 때는 상대 추궁보다 수면·일정·스트레스부터 점검하세요. "
        f"좋은 인연은 일·취미·학습의 연장선에서 자연스럽게 연결되는 경우가 많습니다. "
        f"장기 동반에서는 로맨스보다 가계·역할·경계 같은 운영 체계가 애정을 지탱합니다."
    )

    g2 = (
        f"【직업】 적성 키워드는 {t['career']}입니다. "
        f"조직에서는 {t['social']} 역할로 존재감이 생기고, 독립·창업이라면 전문 영역을 좁혀 "
        f"‘이 문제는 이 사람에게’라는 포지션이 유리합니다. "
        f"이직 시 연봉만이 아니라 성장 곡선·동료 문화·출퇴근 리듬을 함께 보세요. "
        f"강한 기운({_strong(result)})을 쓰는 업무일수록 피로 대비 효율이 높습니다. "
        f"평생 직업은 하나가 아니라 역량의 연속이므로 3년 단위로 이력 스토리를 재정의하세요. "
        f"정체기엔 스킬, 도약기엔 협상·공개 성과를 노리는 리듬이 이 사주와 잘 맞습니다.\n\n"
        f"【기질·의사결정】 기질 핵심은 {t['mood']}입니다. "
        f"압박 시 {_pick(seed, ['구조를 먼저 짜고', '관계를 조율한 뒤', '정보를 모은 다음', '원칙을 세운 뒤'])} "
        f"움직이는 편입니다. 장점은 방향이 잡히면 꾸준하다는 점, 단점은 완벽 대기로 시작이 늦거나 "
        f"확신이 과해 피드백을 닫을 수 있다는 점입니다. "
        f"결정 전 ‘반대 의견 한 줄’을 스스로 쓰면 기질이 성숙해집니다. "
        f"{t['virtue']}를 의식하면 극단으로 치우치지 않습니다. "
        f"이 기질 서술은 일운과 달리 원국 고정 해석입니다."
    )

    g3 = (
        f"【성격】 겉의 {t['adj']} 인상과 속의 안정·인정 욕구가 함께 있을 수 있습니다. "
        f"스트레스 해소에는 {_pick(seed + 5, ['혼자 정리하는 시간', '가벼운 유산소', '메모·저널', '자연 속 걷기'])}이 "
        f"특히 잘 맞습니다. 감정은 삼키기보다 사실-감정-요청 순으로 표현할 때 관계가 덜 꼬입니다. "
        f"건강 면에서는 {t['body']}에 주기적 관심을 두세요. 과로는 판단 오류로 이어지기 쉽습니다. "
        f"성격은 운명을 가두는 틀이 아니라, 다루는 법에 따라 확장되는 도구입니다.\n\n"
        f"【사회·평판】 사회적으로 {t['social']} 포지션이 자연스럽습니다. "
        f"다수와의 얕은 연결보다 소수와의 깊은 신뢰가 자산이 됩니다. "
        f"모임에서는 경청 후 한 가지 제안이 호감을 주고, 평판은 재능보다 약속 이행에서 쌓입니다. "
        f"갈등 시 공개 자리 승부보다 1:1 사실 확인이 장기 자본을 지킵니다. "
        f"용신 {yong}을 의식한 만남·장소 선택은 인연의 질을 높이는 현실적 방법입니다. "
        f"동일 사주 기준 이 사회 해석도 고정됩니다."
    )

    return {
        "title": "오행·정통 사주 심층 해설 (원국 고정)",
        "day_master": result.day_master,
        "elements": result.elements,
        "groups": [
            {"id": "core_wealth_love", "title": "총평 · 재물 · 애정 특성", "body": g1},
            {"id": "career_temperament", "title": "직업 · 기질 특성", "body": g2},
            {"id": "personality_social", "title": "성격 · 사회적 특성", "body": g3},
        ],
    }


# ── Stable life reading ───────────────────────────────────────────────────


def build_life_reading(result: SajuResult, birth: date, gender: str) -> dict[str, Any]:
    t = _t(result)
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    seed = _stable(result, birth, gender, "life_v3")
    yong = result.yongsin.element_ko if result.yongsin else "균형"
    pillars = _pillars_line(result)
    g_word = "남" if gender == "male" else "여"

    early = (
        f"【초년 · 평생 운세】 원국 {pillars}, 일간 {result.day_master}({nature}), {g_word}성 기준. "
        f"초년(대략 0–30대)은 기질이 형성되고 부모·스승·환경의 각인이 큰 시기입니다. "
        f"과제는 정체성 확립과 기초 체력·학습·사회 규범 익히기입니다. "
        f"실수가 두려워 시도를 줄이면 중년 선택지가 좁아집니다. "
        f"초년의 부족감({_weak(result)})은 약점이 아니라 전문 영역의 동기가 되기도 합니다. "
        f"가족 갈등은 단절보다 거리 두기와 자기 루틴으로 완충하는 편이 낫습니다. "
        f"{_strong(result)}이 일찍 드러나면 기대를 받기 쉽고, 그 부담을 스스로 조절하는 법을 배워야 합니다. "
        f"동일 생년월일시라면 이 초년 서술은 바뀌지 않습니다."
    )
    mid = (
        f"【중년】 30–50대는 성과와 책임이 겹칩니다. {t['career']} 분야에서 직함·수입·영향력이 구체화되기 쉽고, "
        f"동시에 건강·부양 부담이 올라갑니다. 성패의 키는 거절의 용기와 장기 파트너십입니다. "
        f"대운이 바뀌는 구간에서는 이직·이사·확장을 한 번에 몰지 말고 한 가지씩 처리하세요. "
        f"중년에 쌓은 평판과 현금흐름이 말년 여유를 만듭니다. "
        f"{t['wealth']} 원칙을 지키면 소득 변동기를 완충하고, {t['love']}을 놓치면 성공해도 고립감을 느낄 수 있습니다. "
        f"일간 {result.day_master}의 {nature} 성향은 중년에 ‘전문성 브랜드’로 자리 잡기 쉽습니다. "
        f"이 중년 해석 역시 동일 원국 고정입니다."
    )
    late = (
        f"【말년】 50대 이후는 확장보다 정리와 전승이 주제입니다. "
        f"건강, 자산 배분, 관계의 화해와 경계가 삶의 질을 가릅니다. "
        f"{t['social']} 역할로 경험을 나누는 일에서 보람을 느끼기 쉽습니다. "
        f"고독을 두려워하기보다 취미·학습·봉사로 일상을 구조화하면 정신 건강이 안정됩니다. "
        f"재산은 보관만이 아니라 의미 있는 사용의 문제로 전환됩니다. "
        f"용신 {yong}을 의식한 주거·여행·인간관계가 만족도를 높입니다. "
        f"평생 운세의 마지막 장은 성취의 크기보다 후회 없는 선택으로 읽히는 사주입니다."
    )

    money = (
        f"【금전 · 평생 패턴】 금전 결은 {t['wealth']}에 가깝습니다. "
        f"한 방보다 현금흐름·비상금·분산의 삼각형이 안전합니다. "
        f"동업·보증은 관계 파손의 대표 원인이므로 문서·한도·종료 조건을 필수화하세요. "
        f"정체기엔 지출 구조부터, 호황기엔 생활비 인플레이션을 경계합니다.\n\n"
        f"【행운】 행운은 준비된 노출에서 옵니다. {t['mood']}가 드러나는 활동"
        f"(포트폴리오, 발표, 커뮤니티)에 정기적으로 모습을 보이세요. "
        f"용신 {yong}을 일정에 넣으면 안정과 판단력이 함께 올라갑니다.\n\n"
        f"【여유·팔복】 복은 돈만이 아니라 시간·건강·관계·수면의 합입니다. "
        f"주 1회 완전 오프, 감사 기록, 검진, 가까운 식사 루틴이 여유를 만듭니다. "
        f"동일 사주에서 이 금전·행운 해석은 고정됩니다."
    )

    love = (
        f"【연애 패턴】 {t['love']}이 매력 포인트입니다. "
        f"이상화 후 급실망을 줄이려면 초반 3개월 안에 돈·가족·시간·갈등 해결 가치관을 맞춰 보세요. "
        f"집착과 회피 사이를 오가지 않도록 연락·만남 빈도를 합의하세요.\n\n"
        f"【궁합】 점수가 아니라 갈등 회복 속도가 핵심입니다. "
        f"잘 맞는 상대는 {_strong(result)}을 이해해 주고 {_weak(result)}을 비난하지 않는 사람입니다. "
        f"너무 비슷한 기질만 모이면 성장이 멈출 수 있어 건강한 차이도 필요합니다.\n\n"
        f"【동반·부부】 장기 관계의 핵심은 운영 체계입니다. "
        f"가계·역할·부모 부양·주거를 주기적으로 업데이트하고, "
        f"다툼 후 24시간 내 사실 확인·사과·다음 약속을 루틴화하세요. "
        f"개별 공간과 취미를 허용할 때 애착이 오래갑니다. 고정 해석입니다."
    )

    career = (
        f"【성격·강점】 {nature} 바탕에 {t['adj']} 에너지가 얹혀 있습니다. "
        f"강점: {_pick(seed, ['책임감', '상황 파악 속도', '조율력', '완성 집요함'])}. "
        f"약점: {_pick(seed + 1, ['자기비판 과다', '시작 지연', '감정 억압 후 폭발', '거절 어려움'])}. "
        f"약점은 고치기보다 장치(체크리스트·동료·시간 제한)로 우회할 때 성장이 빠릅니다.\n\n"
        f"【적성】 {t['career']}. 같은 직무라도 사람/데이터/제작 중 어디에 에너지가 쓰이는지 관찰하세요. "
        f"적성 반대 일로 성공해도 소진이 빨라 중년 전환 비용이 커질 수 있습니다.\n\n"
        f"【직업 리듬】 성장은 계단형입니다. 정체기엔 스킬, 도약기엔 협상·공개 성과. "
        f"조직은 멘토·동료·후배 구도가, 독립은 6개월 생활비와 최소 고객 검증이 선행 조건입니다. "
        f"평생 직업은 역량의 연속—동일 사주에서 이 직업 서술은 고정입니다."
    )

    return {
        "title": "인생풀이·평생 운세 (원국 고정)",
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
                "title": "금전 · 행운 · 삶의 여유",
                "sections": [{"id": "money_luck", "title": "금전·행운·여유", "body": money}],
            },
            {
                "id": "love_bond",
                "title": "연애 · 궁합 · 부부궁",
                "sections": [{"id": "love_marriage", "title": "연애·궁합·동반", "body": love}],
            },
            {
                "id": "self_career",
                "title": "성격 · 적성 · 직업운",
                "sections": [
                    {"id": "personality_career", "title": "성격·적성·직업", "body": career}
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
    display_name: str = "",
    calendar_type: str = "solar",
    time_slot: str | None = None,
    hour: int | None = None,
    time_unknown: bool = True,
    tojeong_year: int = 2026,
) -> dict[str, Any]:
    from app.services.sipsung import mingshi_table
    from app.services.tojeong import build_tojeong

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
        "mingshi": mingshi_table(result),
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
        "new_year_2026": build_year_fortune(result, birth, 2026),
        "five_element": build_five_element_themes(result, birth),
        "life_reading": build_life_reading(result, birth, gender),
        "tojeong": build_tojeong(
            result,
            birth,
            gender,
            year=tojeong_year,
            display_name=display_name,
            calendar_type=calendar_type,
            time_slot=time_slot,
            hour=hour,
            time_unknown=time_unknown,
        ),
    }
