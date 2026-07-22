"""
Product fortune report — FO self-generated text from user saju profile.
Tone/sections differ by category; not a copy of commercial wording.
Richer multi-paragraph bodies per section (corpus foundation).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_report import STEM_NATURE, _elems, _pillars_line, _strong, _t, _weak
from app.services.saju_engine import SajuResult


def _seed(*parts: Any) -> int:
    s = 2166136261
    for p in parts:
        for ch in str(p):
            s ^= ord(ch)
            s = (s * 16777619) & 0x7FFFFFFF
    return s


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)] if options else ""


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
    )
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    cat = product.get("category_id") or "theme"
    tone = product.get("tone") or "light"
    year = 2026
    age = year - birth.year
    chart_facts = getattr(result, "chart_facts", None)

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
        ag = chart_facts.get("agreement")
        pe = chart_facts.get("primary_engine") or "sajupy"
        n_ok = sum(1 for e in (chart_facts.get("engines") or []) if e.get("ok"))
        if ag:
            verify_line = f" 원국 fact는 {pe} 기준이며 상용 안전 엔진 {n_ok}개가 일치했습니다."
        else:
            verify_line = (
                f" 원국 fact는 primary({pe})를 사용합니다. "
                f"교차 엔진과 일부 차이가 있어 경고가 기록되었습니다."
            )

    intro = (
        f"{name}님(일간 {result.day_master}, {nature} 성향)의 원국 "
        f"{_pillars_line(result)}을 기준으로 한 「{product['title']}」 해석입니다. "
        f"오행 {_elems(result)} · 강 {_strong(result)} · 약 {_weak(result)}. "
        f"{age}세 전후 흐름과 {t['mood']} 기운을 겹쳐 읽습니다. "
        f"본문은 FortuneOne 자체 문체이며, 상용 서비스 문구를 복제하지 않습니다."
        f"{verify_line}"
    )

    section_titles = list(product.get("result_sections") or ["핵심 요약", "상세 해석"])
    bodies: list[dict[str, str]] = []

    pool_openers = {
        "roadmap": [
            "계획을 세우기 좋은 틀이 보입니다.",
            "상반기·하반기 리듬을 나누면 실행이 쉬워집니다.",
            "목표를 한 줄로 줄이면 운이 따라오기 쉽습니다.",
            "로드맵은 굵게, 일정은 얇게 잡는 편이 맞습니다.",
        ],
        "narrative": [
            "이야기의 결이 천천히 풀리는 타입입니다.",
            "감정과 타이밍이 맞닿을 때 장면이 바뀝니다.",
            "서두르기보다 장면 전환을 기다리는 편이 낫습니다.",
            "서사 속에서 ‘왜 끌리는지’를 먼저 읽으면 선택이 선명해집니다.",
        ],
        "analytical": [
            "구조 비교로 보면 역할이 분명해집니다.",
            "차이는 갈등이 아니라 분업의 재료가 됩니다.",
            "데이터처럼 사실을 먼저 맞춰 보면 오해가 줍니다.",
            "점수보다 변수(말투·속도·약속)를 조절하는 쪽이 효율적입니다.",
        ],
        "practical": [
            "현실 루틴이 운보다 먼저입니다.",
            "작은 점검이 큰 손실을 막습니다.",
            "숫자와 일정으로 옮기면 불안이 줄어듭니다.",
            "오늘 할 수 있는 한 가지가 내일의 여유를 만듭니다.",
        ],
        "deep": [
            "기질의 뿌리가 선택 패턴을 만듭니다.",
            "초년의 습관이 중년의 방향을 남깁니다.",
            "강점을 키우고 약점은 환경으로 보완하는 편이 길합니다.",
            "깊은 해석일수록 일상 한 줄 실천이 따라와야 의미가 있습니다.",
        ],
        "light": [
            "가볍게 참고할 힌트가 있습니다.",
            "오늘의 태도 하나가 분위기를 바꿉니다.",
            "부담 없이 가져갈 문장 하나를 고르세요.",
            "짧은 메모가 긴 고민보다 도움이 될 때가 있습니다.",
        ],
    }
    openers = pool_openers.get(tone, pool_openers["light"])

    mid_lines = [
        f"일간 {result.day_master}의 {t['adj']} 결을 의식하면 과한 승부보다 페이스 조절이 길합니다.",
        f"환경 키워드로는 {t['career']} · 관계에서는 {t['love']} 쪽이 잘 맞을 수 있습니다.",
        f"재물 감각은 {t['wealth']} 성향이 기본 톤이며, 올해는 규모보다 회수·정리가 우선일 수 있습니다.",
        f"몸·리듬은 {t['body']} 쪽을 과로하지 않는 선에서 관리하세요.",
        f"색·방향 힌트: {t['color']} · {t['dir']} — 공간·일정에 소량만 반영해도 충분합니다.",
    ]
    actions = [
        "주 1회 점검 일지를 쓰세요",
        "중요한 약속은 오전에 잡으세요",
        "지출 상한선을 숫자로 정하세요",
        "감정을 말하기 전 한 호흡 쉬세요",
        "도움 요청을 구체적으로 하세요",
        "미뤄 둔 일 하나를 오늘 끝내세요",
        "주말 2시간은 관계·휴식에만 쓰세요",
        "계약·문서는 24시간 뒤 재확인하세요",
    ]
    closers = [
        "같은 사주·같은 상품으로 다시 조회해도 골격은 동일합니다.",
        "해석은 참고이며, 결정권은 항상 본인에게 있습니다.",
        "불안할수록 루틴을 단순화하는 편이 운이 돕습니다.",
        "한 문장만 실천해도 다음 장면이 달라질 수 있습니다.",
    ]

    for i, title in enumerate(section_titles):
        s = seed + i * 17
        opener = _pick(s, openers)
        mid = _pick(s + 2, mid_lines)
        focus = _pick(
            s + 3,
            [
                t["career"],
                t["love"],
                t["wealth"],
                t["social"],
                t["body"],
                f"{t['color']} 기운",
                f"{t['dir']} 방향",
            ],
        )
        action = _pick(s + 5, actions)
        closer = _pick(s + 7, closers)
        para2 = (
            f"이 구간의 초점 키워드는 ‘{focus}’입니다. "
            f"{name}님에게 유효한 실천은 “{action}”입니다."
        )
        # category spice
        extra = ""
        if cat == "money":
            extra = (
                f" 재물 면에서는 들어와도 나갈 구멍을 먼저 막고, "
                f"{t['wealth']} 태도로 단기 목표 수익만 짧게 잡는 편이 안전합니다."
            )
        elif cat in ("love", "marriage"):
            extra = (
                f" 관계에서는 {t['love']}이 호감 포인트가 되고, "
                f"추측보다 확인된 약속·일정이 신뢰를 만듭니다."
            )
        elif cat == "career":
            extra = (
                f" 일터에서는 {t['career']} 포지션이 잘 맞을 수 있으며, "
                f"성과는 속도보다 마감 품질과 기록에서 갈립니다."
            )
        elif cat == "newyear":
            extra = (
                f" {year}년 키워드는 ‘{t['mood']}’이며, "
                f"상반기는 정리·하반기는 선택적 확장을 권합니다."
            )
        elif cat == "compat" and partner is not None:
            pn = partner_name or "상대"
            extra = (
                f" {pn}님 일간 {partner.day_master}와의 조합으로 보면, "
                f"강점({_strong(result)} vs {_strong(partner)})을 역할 분담에 쓰면 마찰이 줄 수 있습니다."
            )
        elif cat == "life":
            extra = (
                f" 평생 관점에서는 초년 습관·중년 선택·말년 정리가 한 줄로 이어지므로, "
                f"지금 자리의 성실함이 다음 10년의 여유를 만듭니다."
            )

        body = (
            f"【{title}】 {opener} {mid} {para2}{extra} {closer} "
            f"(참고 해석 · 투자·법률 자문 아님)"
        )
        bodies.append({"id": f"s{i+1}", "title": title, "body": body})

    preview = bodies[0]["body"][:240] + "…" if bodies else intro[:200]

    return {
        "product": {
            "id": product["id"],
            "title": product["title"],
            "price_krw": product.get("price_krw"),
            "category_id": cat,
            "category_label": product.get("category_label"),
        },
        "header": header,
        "intro": intro,
        "sections": bodies,
        "preview": preview,
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
            "FortuneOne 규칙 기반 해석입니다. 오픈소스 원국 계산(MIT)과 자체 문장을 사용하며, "
            "상용 운세 문구를 복제하지 않습니다. 엔터테인먼트 목적이며 중요 결정은 전문가 상담을 권합니다."
        ),
        "engine_note": (
            "Fact: sajupy (MIT, primary) + lunar_python/6tail (MIT, cross-check). "
            "Narrative: FortuneOne category templates."
        ),
        "chart_facts": chart_facts,
    }
