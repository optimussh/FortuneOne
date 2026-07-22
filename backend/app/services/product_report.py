"""
Product fortune report — FO self-generated text from user saju profile.
Tone/sections differ by category; not a copy of commercial wording.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_engine import ELEMENT_KO, STEM_ELEMENT, SajuResult
from app.services.saju_report import STEM_NATURE, _elems, _pillars_line, _strong, _t, _weak


def _seed(*parts: Any) -> int:
    s = 2166136261
    for p in parts:
        for ch in str(p):
            s ^= ord(ch)
            s = (s * 16777619) & 0x7FFFFFFF
    return s


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)]


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
    tone = (product.get("tone") or "light")
    year = 2026
    age = year - birth.year

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

    intro = (
        f"{name}님(일간 {result.day_master}, {nature} 성향)의 원국 "
        f"{_pillars_line(result)}을 기준으로 한 「{product['title']}」 해석입니다. "
        f"오행 {_elems(result)} · 강 {_strong(result)} · 약 {_weak(result)}. "
        f"{age}세 전후 흐름과 {t['mood']} 기운을 겹쳐 읽습니다. "
        f"본문은 FortuneOne 자체 문체이며, 상용 서비스 문구를 복제하지 않습니다."
    )

    section_titles = list(product.get("result_sections") or ["핵심 요약", "상세 해석"])
    bodies: list[dict[str, str]] = []

    pool_openers = {
        "roadmap": [
            "계획을 세우기 좋은 틀이 보입니다.",
            "상반기·하반기 리듬을 나누면 실행이 쉬워집니다.",
            "목표를 한 줄로 줄이면 운이 따라오기 쉽습니다.",
        ],
        "narrative": [
            "이야기의 결이 천천히 풀리는 타입입니다.",
            "감정과 타이밍이 맞닿을 때 장면이 바뀝니다.",
            "서두르기보다 장면 전환을 기다리는 편이 낫습니다.",
        ],
        "analytical": [
            "구조 비교로 보면 역할이 분명해집니다.",
            "차이는 갈등이 아니라 분업의 재료가 됩니다.",
            "데이터처럼 사실을 먼저 맞춰 보면 오해가 줍니다.",
        ],
        "practical": [
            "현실 루틴이 운보다 먼저입니다.",
            "작은 점검이 큰 손실을 막습니다.",
            "숫자와 일정으로 옮기면 불안이 줄어듭니다.",
        ],
        "deep": [
            "기질의 뿌리가 선택 패턴을 만듭니다.",
            "초년의 습관이 중년의 방향을 남깁니다.",
            "강점을 키우고 약점은 환경으로 보완하는 편이 길합니다.",
        ],
        "light": [
            "가볍게 참고할 힌트가 있습니다.",
            "오늘의 태도 하나가 분위기를 바꿉니다.",
            "부담 없이 가져갈 문장 하나를 고르세요.",
        ],
    }
    openers = pool_openers.get(tone, pool_openers["light"])

    for i, title in enumerate(section_titles):
        s = seed + i * 17
        opener = _pick(s, openers)
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
        action = _pick(
            s + 5,
            [
                "주 1회 점검 일지를 쓰세요",
                "중요한 약속은 오전에 잡으세요",
                "지출 상한선을 숫자로 정하세요",
                "감정을 말하기 전 한 호흡 쉬세요",
                "도움 요청을 구체적으로 하세요",
                "미뤄 둔 일 하나를 오늘 끝내세요",
            ],
        )
        body = (
            f"【{title}】 {opener} "
            f"일간 {result.day_master}의 {t['adj']} 성향을 의식하면, "
            f"핵심 키워드는 ‘{focus}’ 쪽으로 기울 수 있습니다. "
            f"{name}님에게 지금 유효한 실천은 “{action}”입니다. "
            f"같은 사주·같은 상품으로 다시 조회해도 골격은 동일하게 유지됩니다. "
            f"(참고 해석 · 투자·법률 자문 아님)"
        )
        # category-specific extra paragraph
        if cat == "money":
            body += (
                f" 재물 면에서는 {t['wealth']} 태도가 기본이며, "
                f"올해는 불려 쓰기보다 지키는 습관이 점수를 올립니다."
            )
        elif cat in ("love", "marriage"):
            body += (
                f" 관계에서는 {t['love']}이 호감 포인트가 되고, "
                f"과한 추측보다 확인된 약속이 신뢰를 만듭니다."
            )
        elif cat == "career":
            body += (
                f" 일터에서는 {t['career']} 포지션이 잘 맞을 수 있으며, "
                f"성과는 속도보다 마감 품질에서 갈립니다."
            )
        elif cat == "newyear":
            body += (
                f" {year}년 키워드는 ‘{t['mood']}’이며, "
                f"상반기는 정리·하반기는 확장 비중을 조절해 보세요."
            )
        elif cat == "compat" and partner is not None:
            pn = partner_name or "상대"
            body += (
                f" {pn}님 일간 {partner.day_master}와의 조합으로 보면, "
                f"서로 다른 오행 강점({_strong(result)} vs {_strong(partner)})을 "
                f"역할 분담에 쓰면 마찰이 줄 수 있습니다."
            )

        bodies.append({"id": f"s{i+1}", "title": title, "body": body})

    preview = bodies[0]["body"][:220] + "…" if bodies else intro[:200]

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
            "FortuneOne 규칙 기반 해석입니다. 오픈소스 원국 계산과 자체 문장을 사용하며, "
            "상용 운세 문구를 복제하지 않습니다. 엔터테인먼트 목적이며 중요 결정은 전문가 상담을 권합니다."
        ),
        "engine_note": (
            "현재: sajupy 원국 + FO 카테고리별 서사 모듈. "
            "추후 multi-engine(fact layer 합의 + 문체 모듈 분리) 확장 예정."
        ),
    }
