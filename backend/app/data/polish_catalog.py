# -*- coding: utf-8 -*-
"""
Polish product catalog for FO product quality:
- re-tag categories (money/career/love/etc.)
- rewrite titles + detail copy (no commercial scrape body)
- expand result section labels
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "product_catalog.json"

# keyword buckets — first match wins by priority score
CAT_DEFS: list[tuple[str, str, list[str], int]] = [
    # id, label, keywords, priority weight
    ("free", "무료·체험", ["무료"], 100),
    (
        "money",
        "재물·금전",
        [
            "재물", "금전", "돈", "부자", "재테크", "투자", "모으", "유실", "재산",
            "수입", "지출", "주식", "부동산", "월급", "연봉", "복권", "재성",
            "경제", "풍요", "부유", "빚", "대출", "사업 수익", "재복", "재운",
            "금운", "돈복", "부귀", "재물운", "금전운", "부적", "로또",
        ],
        95,
    ),
    (
        "career",
        "직장·사업",
        [
            "직장", "사업", "동업", "상사", "부하", "이직", "취업", "승진", "회사",
            "직업", "업무", "커리어", "창업", "조직", "동료", "면접", "명예", "출세",
            "퇴사", "연봉 협상", "진로", "업무운", "직장운", "사업운",
        ],
        88,
    ),
    (
        "newyear",
        "신년·연간",
        ["2026", "신년", "올해", "연간", "12개월", "토정", "세운", "월별", "한 해", "세배"],
        80,
    ),
    (
        "marriage",
        "결혼·배우자",
        ["결혼", "배우자", "신랑", "신부", "웨딩", "혼인", "약혼", "혼기", "시댁", "처가"],
        75,
    ),
    (
        "compat",
        "궁합·관계",
        ["궁합", "두 사람", "우리 둘", "호흡", "상성", "케미", "둘의"],
        70,
    ),
    (
        "love",
        "연애·인연",
        [
            "연애", "사랑", "인연", "만남", "짝", "고백", "이별", "재회", "솔로", "썸",
            "연인", "애정", "이성", "첫사랑", "소개팅", "그 사람", "상대", "남자", "여자",
            "마음", "감정", "로맨스",
        ],
        60,
    ),
    (
        "life",
        "평생·사주풀이",
        ["평생", "사주", "인생", "명리", "기질", "성격", "팔자", "총운", "운명", "타고난"],
        55,
    ),
    (
        "theme",
        "테마·기타",
        ["자녀", "꿈", "혈액", "별자리", "타로", "주간", "월간", "오늘", "건강", "가족"],
        40,
    ),
]

SECTION_BY_CAT: dict[str, list[str]] = {
    "newyear": [
        "한 해 총평",
        "상반기 흐름",
        "하반기 흐름",
        "월별 포인트 맵",
        "기회 구간",
        "주의 구간",
        "인간·직장 연결",
        "실천 로드맵",
    ],
    "love": [
        "인연의 결",
        "끌림 패턴",
        "만남 시기",
        "표현·소통",
        "오해·갈등 포인트",
        "관계 회복 팁",
        "정리·거리 두기",
        "한 달 실천 체크",
    ],
    "marriage": [
        "배우자 상",
        "혼인 흐름",
        "가정 안정 조건",
        "갈등 조율",
        "시기별 조언",
        "재정·생활 호흡",
        "함께 키울 습관",
        "장기 로드맵",
    ],
    "compat": [
        "기질 비교",
        "보완 포인트",
        "충돌 포인트",
        "감정 온도차",
        "대화 운영법",
        "생활 리듬",
        "함께할 실천",
        "장기 호흡",
    ],
    "money": [
        "재물 그릇",
        "수입 리듬",
        "지출·누수",
        "투자 태도",
        "문서·계약",
        "사람·동업",
        "지키는 습관",
        "올해 우선순위",
    ],
    "career": [
        "일 기질",
        "역할 궁합",
        "조직 호흡",
        "전환 타이밍",
        "성장 루트",
        "성과 루틴",
        "관계 리스크",
        "다음 분기 액션",
    ],
    "life": [
        "기질 구조",
        "초년 흐름",
        "중년 흐름",
        "말년 흐름",
        "강점 활용",
        "보완 포인트",
        "인간관계 기본",
        "평생 테마",
    ],
    "theme": [
        "핵심 요약",
        "상세 해석 1",
        "상세 해석 2",
        "환경·타이밍",
        "주의 포인트",
        "기회 포인트",
        "실천 제안",
        "한 줄 메모",
    ],
    "free": ["간단 요약", "오늘의 팁", "주의 한 가지"],
}

# FO title templates by category — {theme} filled from source signals
TITLE_BANK: dict[str, list[str]] = {
    "newyear": [
        "2026 연간 흐름 리포트",
        "한 해 세운 가이드",
        "신년 로드맵 풀이",
        "12개월 운 리듬 맵",
        "연간 기회·주의 체크",
        "2026 상하반기 전략",
        "세운 기반 실천 플랜",
        "연간 명리 브리핑",
        "새해 방향 설정 리포트",
        "한 해 총운·월운 패키지",
        "2026 흐름 압축 해석",
        "연간 선택 가이드",
        "신년 테마 리딩",
    ],
    "love": [
        "인연 결 읽기",
        "끌림 패턴 분석",
        "만남 타이밍 힌트",
        "애정 소통 스타일",
        "마음 거리 조절법",
        "솔로 구간의 기회",
        "재회·정리 가이드",
        "이성 운 리듬",
        "소개팅·만남 전 체크",
        "감정 기복 다루기",
        "인연의 문 열기",
        "관계 온도 맞추기",
        "연애 흐름 브리핑",
        "호감 신호 해석",
        "애정운 실천 노트",
    ],
    "marriage": [
        "배우자 상 스케치",
        "혼인 흐름 리포트",
        "가정 안정의 조건",
        "결혼 시기 힌트",
        "부부 호흡 가이드",
        "혼기 전후 체크",
        "배우자 인연 맵",
        "가정 재정 호흡",
        "결혼 결정 전 점검",
        "동반 생활 루틴",
        "배우자 궁합 브리프",
        "혼인 로드맵",
    ],
    "compat": [
        "두 사람 기질 비교",
        "상성·호흡 리포트",
        "보완과 충돌 맵",
        "대화 온도 맞추기",
        "장기 동반 가이드",
        "관계 운영 매뉴얼",
        "케미 분석 브리핑",
        "함께할 때 실천표",
    ],
    "money": [
        "재물 그릇 진단",
        "수입·지출 리듬",
        "지키는 재테크 태도",
        "문서·계약 주의보",
        "재물 누수 점검",
        "올해 금전 우선순위",
        "현금흐름 가이드",
        "투자 규모 조절법",
    ],
    "career": [
        "일 기질 진단",
        "조직 역할 궁합",
        "이직·전환 타이밍",
        "성과 루틴 설계",
        "상사·동료 호흡",
        "커리어 성장 루트",
        "사업 확장 체크",
        "분기 액션 플랜",
    ],
    "life": [
        "평생 기질 구조",
        "초중말 인생 흐름",
        "타고난 강점 활용",
        "보완 포인트 처방",
        "인간관계 기본기",
        "생활 리듬 설계",
        "팔자 흐름 다시 읽기",
        "평생 테마 리포트",
    ],
    "theme": [
        "테마 집중 풀이",
        "상황별 힌트 모음",
        "타이밍 브리핑",
        "선택 전 체크리스트",
        "환경 맞추기 가이드",
        "단기 흐름 해석",
        "주제별 실천 노트",
        "한 주제 심화 리딩",
    ],
    "free": [
        "무료 간단 브리핑",
        "오늘 참고 한 줄",
        "체험용 요약 운세",
    ],
}

ROLE_NOTE = (
    "상세 사주 탭(오늘·신년·토정·부자되기)은 기본 제공 리포트이고, "
    "스토어 상품은 주제를 더 깊게 파는 유료(모의) 패키지입니다."
)


def score_category(title: str, source_title: str) -> tuple[str, str]:
    text = f"{source_title} {title}"
    best = ("theme", "테마·기타", -1)
    for cid, label, keys, weight in CAT_DEFS:
        hits = sum(1 for k in keys if k in text)
        if hits == 0:
            continue
        score = hits * 10 + weight
        if cid == "marriage" and any(k in text for k in ["결혼", "배우자", "혼인", "혼기", "웨딩"]):
            score += 40
        if cid == "money" and any(k in text for k in ["재물", "금전", "부자", "재테크", "재운", "금운"]):
            score += 35
        if cid == "career" and any(k in text for k in ["직장", "직업", "사업", "이직", "승진", "진로"]):
            score += 35
        # "직업" inside marriage titles (배우자 직업) → prefer marriage if 결혼 present
        if cid == "career" and any(k in text for k in ["결혼", "배우자", "혼인", "혼기"]):
            score -= 50
        if score > best[2]:
            best = (cid, label, score)
    return best[0], best[1]


def fo_title(cat: str, idx: int, source: str) -> str:
    """FO-owned title only — no leftover commercial phrasing, no cross-cat tags."""
    bank = TITLE_BANK.get(cat) or TITLE_BANK["theme"]
    base = bank[idx % len(bank)]
    # uniquify within category when bank wraps
    if idx >= len(bank):
        return f"{base} #{idx // len(bank) + 1}"
    return base


def intro_blurbs(cat: str, title: str) -> list[str]:
    common = [
        f"「{title}」은 회원님 사주 원국(양력·시진 반영)을 바탕으로 FortuneOne이 생성하는 주제형 리포트입니다.",
        ROLE_NOTE,
        "MIT 오픈소스 엔진으로 원국을 교차 검증하고, 해석 문장은 자체 템플릿으로 작성합니다. 상용 사이트 문구를 복제하지 않습니다.",
    ]
    by_cat = {
        "newyear": "한 해 방향·월 리듬·기회/주의 구간을 로드맵 톤으로 정리합니다. 매일 보는 일운과는 역할이 다릅니다.",
        "love": "인연·표현·타이밍을 이야기형으로 풀어, 오늘의 연애 점수보다 패턴을 보는 데 초점을 둡니다.",
        "marriage": "배우자 상·혼인 흐름·생활 호흡을 중심으로, 장기 동반 관점의 조언을 담습니다.",
        "compat": "두 사람 프로필(또는 본인+상대) 기준 기질 비교·조율법에 집중합니다.",
        "money": "재물 그릇·현금흐름·지키는 습관 중심. 부자되기 탭의 연간 재물 캘린더와 보완적으로 쓰세요.",
        "career": "일 기질·조직 호흡·전환 타이밍. 직장/사업 의사결정 전 참고용입니다.",
        "life": "초·중·말 흐름과 기질 구조. 인생풀이 탭과 결은 비슷하지만 상품별로 다른 초점 섹션을 둡니다.",
        "theme": "특정 상황·질문에 맞춘 집중 풀이 패키지입니다.",
        "free": "짧게 맛보는 체험용 요약입니다. 깊은 내용은 유료(모의) 상품을 이용하세요.",
    }
    return [common[0], by_cat.get(cat, by_cat["theme"]), common[1], common[2]]


def for_whom(cat: str) -> list[str]:
    m = {
        "newyear": ["올해 방향이 궁금한 분", "분기별 계획을 세우는 분", "월별 리듬을 보고 싶은 분"],
        "love": ["연애 패턴을 정리하고 싶은 분", "만남·이별 타이밍이 궁금한 분", "표현 방식을 바꾸고 싶은 분"],
        "marriage": ["혼인·배우자 상이 궁금한 분", "가정 안정 조건을 보고 싶은 분"],
        "compat": ["두 사람 호흡을 점검하고 싶은 분", "갈등 포인트를 미리 알고 싶은 분"],
        "money": ["지출·수입 리듬을 다잡고 싶은 분", "큰 결정 전 금전 태도를 보고 싶은 분"],
        "career": ["이직·역할 전환을 고민하는 분", "조직 안 포지션이 궁금한 분"],
        "life": ["기질·인생 구간을 넓게 보고 싶은 분"],
        "theme": ["한 가지 주제에 집중하고 싶은 분"],
        "free": ["가볍게 체험해 보고 싶은 분"],
    }
    return m.get(cat, m["theme"])


def _extra_fo_products() -> list[dict]:
    """FO-authored products to balance money/career (sample site was love-heavy)."""
    extras = []
    money_titles = TITLE_BANK["money"]
    career_titles = TITLE_BANK["career"]
    for i, title in enumerate(money_titles):
        extras.append(
            {
                "id": f"fo_money_{i+1}",
                "source_cid": None,
                "source_url": "",
                "source_title": f"[FO] {title}",
                "category_id": "money",
                "category_label": "재물·금전",
                "title": title,
                "price_krw": 3900 + (i % 4) * 1000,
                "currency": "KRW",
                "needs_profile": True,
                "needs_partner": False,
                "is_free": False,
                "tone": "practical",
                "payment": {
                    "methods_mock": ["신용카드", "간편결제", "휴대폰"],
                    "result_view_days_web": 7,
                },
            }
        )
    for i, title in enumerate(career_titles):
        extras.append(
            {
                "id": f"fo_career_{i+1}",
                "source_cid": None,
                "source_url": "",
                "source_title": f"[FO] {title}",
                "category_id": "career",
                "category_label": "직장·사업",
                "title": title,
                "price_krw": 4200 + (i % 4) * 1000,
                "currency": "KRW",
                "needs_profile": True,
                "needs_partner": False,
                "is_free": False,
                "tone": "practical",
                "payment": {
                    "methods_mock": ["신용카드", "간편결제", "휴대폰"],
                    "result_view_days_web": 7,
                },
            }
        )
    # a few free + life + compat
    extras.append(
        {
            "id": "fo_free_1",
            "source_title": "[FO] free",
            "category_id": "free",
            "category_label": "무료·체험",
            "title": "무료 간단 브리핑",
            "price_krw": 0,
            "is_free": True,
            "needs_profile": True,
            "tone": "light",
        }
    )
    extras.append(
        {
            "id": "fo_compat_1",
            "source_title": "[FO] 궁합",
            "category_id": "compat",
            "category_label": "궁합·관계",
            "title": "관계 운영 매뉴얼",
            "price_krw": 5500,
            "needs_profile": True,
            "needs_partner": True,
            "tone": "analytical",
        }
    )
    return extras


def polish(catalog: dict) -> dict:
    products = list(catalog.get("products") or [])
    # drop previous FO extras on re-run
    products = [p for p in products if not str(p.get("id", "")).startswith("fo_")]
    products.extend(_extra_fo_products())
    counters: dict[str, int] = Counter()
    out = []
    for p in products:
        src = p.get("source_title") or p.get("title") or ""
        old_title = p.get("title") or src
        cat, label = score_category(old_title, src)
        counters[cat] += 1
        idx = counters[cat] - 1
        title = fo_title(cat, idx, src + old_title)
        sections = SECTION_BY_CAT.get(cat, SECTION_BY_CAT["theme"])
        # price keep; free if 0
        price = int(p.get("price_krw") or 0)
        is_free = price == 0 or cat == "free"
        needs_partner = cat == "compat" or "궁합" in src or "둘이" in title
        tone = {
            "newyear": "roadmap",
            "love": "narrative",
            "marriage": "narrative",
            "compat": "analytical",
            "money": "practical",
            "career": "practical",
            "life": "deep",
            "theme": "light",
            "free": "light",
        }.get(cat, "light")

        out.append(
            {
                **{k: v for k, v in p.items() if k not in ("intro_blurbs",)},
                "title": title,
                "subtitle": f"{label} 주제 패키지 · 사주 프로필 연동",
                "category_id": cat,
                "category_label": label,
                "result_sections": sections,
                "preview_sections": ["이런 분께", "구성", "기본 탭과 차이"],
                "intro_blurbs": intro_blurbs(cat, title),
                "for_whom": for_whom(cat),
                "diff_from_free_tabs": ROLE_NOTE,
                "tone": tone,
                "needs_partner": needs_partner,
                "is_free": is_free,
                "copy_version": 2,
            }
        )

    catalog["products"] = out
    catalog["content_quality"] = {
        "version": 2,
        "notes": [
            "Titles and blurbs are FO-authored; source_title kept for internal mapping only.",
            "Categories re-scored for money/career/marriage priority.",
            ROLE_NOTE,
        ],
        "category_counts": dict(Counter(p["category_id"] for p in out)),
    }
    catalog["role_guide"] = {
        "free_tabs": {
            "daily": "오늘의 운세 — 매일 변하는 짧은 일운",
            "newyear": "2026 신년 — 연간 테마·로드맵(기본 제공)",
            "tojeong": "2026 토정 — 이야기형 종합·월별·영역",
            "wealth": "2026 부자되기 — 재물 전용 월등급·일자 캘린더",
            "five": "오행 — 기질·구조",
            "life": "인생풀이 — 초중말·평생",
        },
        "store": "주제별 심화 패키지(결제/모의). 프로필 선택 후 결과 생성.",
        "summary": ROLE_NOTE,
    }
    return catalog


def main() -> None:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    polished = polish(data)
    CATALOG_PATH.write_text(
        json.dumps(polished, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # mirror to docs
    docs = ROOT.parent.parent.parent / "docs" / "superpowers" / "specs" / "2026-07-22-unsin-benchmark-catalog.json"
    if docs.parent.exists():
        docs.write_text(json.dumps(polished, ensure_ascii=False, indent=2), encoding="utf-8")
    print("category_counts", polished["content_quality"]["category_counts"])
    print("products", len(polished["products"]))
    print("sample titles:")
    for p in polished["products"][:8]:
        print(f"  [{p['category_id']}] {p['title']}")


if __name__ == "__main__":
    main()
