"""
Product fortune report — long-form FO text from user saju.
Unique section bodies by product_id + section index + chart seed.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_engine import SajuResult
from app.services.saju_report import STEM_NATURE, _elems, _pillars_line, _strong, _t, _weak


def _seed(*parts: Any) -> int:
    s = 2166136261
    for p in parts:
        for ch in str(p):
            s ^= ord(ch)
            s = (s * 16777619) & 0x7FFFFFFF
    return s


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)] if options else ""


def _paragraphs(seed: int, chunks: list[list[str]], n: int = 3) -> str:
    parts = []
    for i in range(n):
        pool = chunks[i % len(chunks)]
        parts.append(_pick(seed + i * 13, pool))
    return " ".join(parts)


def build_product_report(
    product: dict[str, Any],
    result: SajuResult,
    birth: date,
    gender: str,
    *,
    display_name: str = "",
    partner: SajuResult | None = None,
    partner_name: str = "",
    partner_birth: date | None = None,
) -> dict[str, Any]:
    name = display_name or "회원"
    t = _t(result)
    seed = _seed(
        product.get("id"),
        result.day_master,
        _pillars_line(result),
        birth.isoformat(),
        gender,
        product.get("copy_version", 2),
    )
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    cat = product.get("category_id") or "theme"
    tone = product.get("tone") or "light"
    year = 2026
    age = year - birth.year
    chart_facts = getattr(result, "chart_facts", None)
    gko = "남" if gender == "male" else "여"

    header = {
        "product_id": product["id"],
        "product_title": product["title"],
        "category_id": cat,
        "category_label": product.get("category_label"),
        "display_name": name,
        "gender": gender,
        "birth": birth.isoformat(),
        "day_master": result.day_master,
        "day_master_nature": nature,
        "pillars_line": _pillars_line(result),
        "elements_line": _elems(result),
        "tone": tone,
    }

    verify_line = ""
    if chart_facts:
        n_ok = sum(1 for e in (chart_facts.get("engines") or []) if e.get("ok"))
        pe = chart_facts.get("primary_engine") or "sajupy"
        if chart_facts.get("agreement"):
            verify_line = (
                f" 원국 fact는 {pe} 기준이며, 상용 가능(MIT) 엔진 {n_ok}개가 일치했습니다."
            )
        else:
            verify_line = (
                f" 원국 fact는 primary({pe})를 사용합니다. "
                f"교차 엔진과 일부 차이가 있어 경고가 기록되었습니다."
            )

    intro = (
        f"{name}님({gko}, 일간 {result.day_master}·{nature})의 원국 "
        f"{_pillars_line(result)}을 기준으로 「{product['title']}」을 풀어 드립니다. "
        f"오행 {_elems(result)}. 강 {_strong(result)} · 약 {_weak(result)}. "
        f"{age}세 전후, {year}년 전후 흐름과 ‘{t['mood']}’ 기운을 겹칩니다. "
        f"이 상품은 스토어 주제 패키지이며, 상세 사주 탭의 신년·토정·부자되기와 "
        f"역할이 다릅니다(탭=기본 제공, 스토어=주제 심화). "
        f"문장은 FortuneOne 자체 생성입니다."
        f"{verify_line}"
    )

    section_titles = list(
        product.get("result_sections")
        or ["핵심 요약", "상세 해석", "실천 제안"]
    )

    # Large phrase banks — rotated by seed so products don't feel identical
    A = [
        f"일간 {result.day_master}의 {t['adj']} 성향이 이 구간의 기본 톤을 만듭니다.",
        f"원국의 결은 {_pillars_line(result)}에서 이미 드러나며, 같은 입력으로는 골격이 고정됩니다.",
        f"강점 {_strong(result)}을 앞에 두고, 약점 {_weak(result)}은 환경으로 보완하는 편이 길합니다.",
        f"{t['virtue']} 가치를 의식하면 선택 기준이 흔들리지 않습니다.",
    ]
    B = [
        f"일·역할 쪽에서는 {t['career']} 포지션이 잘 맞을 수 있습니다.",
        f"관계에서는 {t['love']} 태도가 호감을 만들고, 과한 추측은 신뢰를 깎습니다.",
        f"재물 감각은 {t['wealth']} 쪽이 기본이며 규모보다 회수·기록이 우선일 수 있습니다.",
        f"몸·리듬은 {t['body']} 관련 과로를 피하는 것이 예방입니다.",
        f"사람과 자리에서는 {t['social']} 역할이 자연스럽습니다.",
    ]
    C = [
        f"색·방향 힌트({t['color']} · {t['dir']})는 공간·일정에 소량만 반영해도 충분합니다.",
        "중요한 결정은 감정 고조 직후보다 한 템포 뒤가 낫습니다.",
        "기록이 남는 습관이 불안을 줄이고 다음 판단을 쉽게 합니다.",
        "작은 성과를 인정하고 끝내는 힘이 과욕보다 길합니다.",
        "약속은 짧게, 확인은 두 번이 실수를 줄입니다.",
    ]
    D = [
        f"{name}님에게 지금 유효한 실천은 “{_pick(seed, ['주 1회 점검 일기','오전 핵심 업무 배치','지출 상한 숫자화','감정 전 한 호흡','구체적 도움 요청','미룬 일 하나 완료'])}”입니다.",
        f"한 달 단위로 ‘{_pick(seed+1, ['관계','일','돈','건강','학습'])}’ 지표 하나만 추적해 보세요.",
        f"갈등 시 “사실 → 느낌 → 요청” 순서로 말하면 오해가 줄어듭니다.",
        f"큰 계약·이직·이사 전에는 24시간 숙고 규칙을 두세요.",
    ]
    E = [
        "해석은 참고이며 결정권은 본인에게 있습니다. 투자·법률 자문이 아닙니다.",
        "같은 사주·같은 상품으로 다시 열어도 골격 문장은 동일하게 유지됩니다.",
        "불안할수록 루틴을 단순화하는 편이 운이 돕습니다.",
        "한 문장 실천이 긴 고민보다 다음 장면을 바꿉니다.",
    ]

    cat_extra_pools: dict[str, list[str]] = {
        "newyear": [
            f"{year}년 키워드는 ‘{t['mood']}’로 읽힙니다. 상반기는 정리, 하반기는 선택적 확장 비중을 조절하세요.",
            "월별로는 ‘밀기 / 쉬기 / 점검’ 리듬을 미리 표시해 두면 충동 결정이 줄어듭니다.",
            "신년 탭의 로드맵과 겹치는 부분은 방향 확인용, 이 상품은 실행 디테일 보강용으로 쓰세요.",
        ],
        "love": [
            f"애정 표현은 {t['love']} 쪽이 잘 통하고, 상대 속도를 무시하면 호감이 식기 쉽습니다.",
            "만남은 우연처럼 보여도 준비된 일정이 문을 엽니다. 소개·모임 빈도를 과하게 늘리기보다 질을 높이세요.",
            "이별·재정리는 감정의 끝이 아니라 다음 인연의 경계 설정이기도 합니다.",
        ],
        "marriage": [
            "배우자 상은 ‘완벽한 사람’보다 ‘생활 루틴이 맞는 사람’에 가깝게 읽는 편이 현실적입니다.",
            "혼인 전후 재정·주거·가족 경계 세 가지는 문서로 합의해 두면 갈등이 줄기 쉽습니다.",
            "부자되기·재물 상품과 함께 보면 가정 경제 호흡을 맞추기 좋습니다.",
        ],
        "compat": [
            "두 사람의 차이는 틀린 것이 아니라 분업 재료입니다. 강점을 겹치지 않게 배치하세요.",
            "말의 속도와 사과 타이밍만 맞춰도 체감 궁합이 올라갑니다.",
            "상대 프로필이 있으면 일간·오행 대비가 더 구체화됩니다.",
        ],
        "money": [
            f"재물은 {t['wealth']} 태도가 기본입니다. 올해는 불려 쓰기보다 누수 차단이 점수에 가깝습니다.",
            "문서·보증·동업은 기회처럼 보여도 손안의 현금 범위에서만 검토하세요.",
            "부자되기 탭의 월 등급·일자 캘린더와 함께 보면 ‘언제 줄이고 언제 움직일지’가 선명해집니다.",
        ],
        "career": [
            f"일터에서는 {t['career']} 포지션이 잘 맞을 수 있습니다. 성과는 속도보다 마감 품질과 기록입니다.",
            "이직·전환은 감정의 정점이 아니라 대안이 준비된 뒤가 안전합니다.",
            "상사·동료와의 마찰은 업무 기준을 문장으로 맞추면 상당 부분 예방됩니다.",
        ],
        "life": [
            "초년의 습관, 중년의 선택, 말년의 정리가 한 줄로 이어집니다.",
            "인생풀이 탭과 겹치는 골격은 ‘기질’이고, 이 상품은 구간별 실천을 더 촘촘히 둡니다.",
            "건강·관계·일의 균형을 한 분기에 하나씩만 올려도 충분합니다.",
        ],
        "theme": [
            "한 주제에 초점을 좁힐수록 조언이 실행 가능해집니다.",
            "상황 변수(사람·돈·시간) 중 하나만 바꿔도 결과가 달라질 수 있습니다.",
            "짧은 메모로 시작·중간·끝을 남기면 다음에 같은 실수를 줄입니다.",
        ],
        "free": [
            "체험용 요약입니다. 깊은 구간은 유료(모의) 패키지를 이용하세요.",
            "오늘의 태도 하나가 분위기를 바꿉니다.",
        ],
    }

    bodies: list[dict[str, str]] = []
    for i, title in enumerate(section_titles):
        s = seed + i * 31
        block = _paragraphs(s, [A, B, C, D, E], n=5)
        extra = _pick(s + 9, cat_extra_pools.get(cat, cat_extra_pools["theme"]))
        focus = _pick(
            s + 3,
            [t["career"], t["love"], t["wealth"], t["social"], t["body"], t["mood"]],
        )
        partner_bit = ""
        if partner is not None and cat in ("compat", "love", "marriage"):
            pn = partner_name or "상대"
            partner_bit = (
                f" {pn}님(일간 {partner.day_master}, {_pillars_line(partner)})과의 대비로 보면 "
                f"강점({_strong(result)} vs {_strong(partner)})을 역할로 나누는 편이 마찰을 줄입니다."
            )
        body = (
            f"【{title}】 "
            f"이 구간의 초점 키워드는 ‘{focus}’입니다. "
            f"{block} {extra}{partner_bit} "
            f"({i+1}/{len(section_titles)} · FO 자체 문체 · 참고용)"
        )
        bodies.append({"id": f"s{i+1}", "title": title, "body": body})

    # ensure length - commercial feel
    for b in bodies:
        if len(b["body"]) < 280:
            b["body"] += (
                f" 추가로, {name}님의 오행 분포({_elems(result)})를 기준으로 "
                f"과한 한 쪽 기운만 밀어붙이기보다 약한 쪽을 생활 루틴으로 메우는 전략이 "
                f"장기적으로 안정적입니다."
            )

    preview = bodies[0]["body"][:280] + "…" if bodies else intro[:200]

    return {
        "product": {
            "id": product["id"],
            "title": product["title"],
            "subtitle": product.get("subtitle"),
            "price_krw": product.get("price_krw"),
            "category_id": cat,
            "category_label": product.get("category_label"),
        },
        "header": header,
        "intro": intro,
        "sections": bodies,
        "preview": preview,
        "role_guide": {
            "this_product": "스토어 주제 심화 패키지",
            "free_tabs": "상세 사주 탭 — 오늘/신년/토정/부자되기/오행/인생풀이 기본 제공",
            "note": product.get("diff_from_free_tabs")
            or "탭은 기본 리포트, 스토어는 주제별 심화입니다.",
        },
        "partner": (
            {
                "display_name": partner_name or "상대",
                "day_master": partner.day_master,
                "pillars_line": _pillars_line(partner),
                "birth": partner_birth.isoformat() if partner_birth else None,
            }
            if partner
            else None
        ),
        "disclaimer": (
            "FortuneOne 규칙 기반 해석입니다. MIT 오픈소스 원국 계산과 자체 문장을 사용하며 "
            "상용 운세 문구를 복제하지 않습니다. 엔터테인먼트 목적이며 투자·법률·의료 자문이 아닙니다."
        ),
        "engine_note": (
            "Fact: sajupy (MIT, primary) + lunar_python/6tail (MIT, cross-check). "
            "Narrative: FortuneOne long-form templates v2."
        ),
        "chart_facts": chart_facts,
    }
