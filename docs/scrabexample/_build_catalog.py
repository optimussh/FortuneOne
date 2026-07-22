# -*- coding: utf-8 -*-
"""Build FortuneOne product catalog from unsin scrape (structure only, rewritten titles)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
extract = json.loads((ROOT / "extract.json").read_text(encoding="utf-8"))
pay = json.loads((ROOT / "payment" / "payment.json").read_text(encoding="utf-8"))

# amount by cid from payment capture
price_by_cid: dict[str, int] = {}
for p in pay:
    if not p.get("ok"):
        continue
    m = re.search(r"cid=(\d+)", p.get("detailUrl") or "")
    if not m:
        continue
    hint = p.get("amountHint") or ""
    digits = re.sub(r"[^\d]", "", hint)
    if digits:
        price_by_cid[m.group(1)] = int(digits)

# Category mapping from sample site IA (ca2 + free themes)
CATEGORY_RULES: list[tuple[str, str, list[str]]] = [
    ("newyear", "신년·연간", ["2026", "신년", "올해", "연간", "12개월", "토정", "세운"]),
    ("love", "연애·인연", ["연애", "사랑", "인연", "만남", "짝", "고백", "이별", "재회", "솔로", "썸"]),
    ("marriage", "결혼·배우자", ["결혼", "배우자", "신랑", "신부", "웨딩", "혼인"]),
    ("compat", "궁합·관계", ["궁합", "두 사람", "우리", "그 사람", "상대"]),
    ("money", "재물·금전", ["재물", "금전", "돈", "부자", "재테크", "투자", "모으", "유실"]),
    ("career", "직장·사업", ["직장", "사업", "동업", "상사", "부하", "이직", "취업"]),
    ("life", "평생·사주풀이", ["평생", "사주", "인생", "명리", "기질", "성격"]),
    ("theme", "테마·기타", ["자녀", "꿈", "혈액", "별자리", "타로", "주간", "월간", "오늘"]),
    ("free", "무료·체험", ["무료"]),
]


def guess_category(title: str) -> tuple[str, str]:
    for cid, label, keys in CATEGORY_RULES:
        if any(k in title for k in keys):
            return cid, label
    return "theme", "테마·기타"


# Rewrite helpers — change feel without copying commercial slogans
REWRITES = [
    (r"운세의\s*신", "FortuneOne"),
    (r"토정비결", "연간 명리 리포트"),
    (r"명품\s*토정", "프리미엄 연간"),
    (r"짝사랑", "마음 인연"),
    (r"신통방통", "통찰"),
    (r"진실로\s*알고\s*싶다면", "깊이 알고 싶을 때"),
    (r"반드시\s*만날", "만나기 쉬운"),
    (r"운명적", "흐름이 강한"),
    (r"대박", "기회"),
    (r"반값", "체험가"),
]


def rewrite_title(t: str) -> str:
    out = t.strip()
    for pat, rep in REWRITES:
        out = re.sub(pat, rep, out)
    # light tone shift prefixes
    if not out.startswith("[") and len(out) > 8:
        # keep uniqueness, add FO style only if generic
        pass
    return out


SECTION_TEMPLATES = {
    "newyear": [
        "한 해 흐름 총평",
        "월별 포인트 12",
        "기회·주의 구간",
        "실천 로드맵",
    ],
    "love": [
        "인연의 결",
        "만남 시기 힌트",
        "표현·소통 스타일",
        "조심할 패턴",
    ],
    "marriage": [
        "배우자 상",
        "혼인 흐름",
        "가정 안정의 조건",
        "시기별 조언",
    ],
    "compat": [
        "두 사람 기질 비교",
        "보완·충돌 포인트",
        "관계 운영법",
        "함께할 때 실천",
    ],
    "money": [
        "재물 그릇",
        "수입·지출 리듬",
        "투자·기회 태도",
        "지키는 습관",
    ],
    "career": [
        "일 기질",
        "조직·역할 궁합",
        "전환 타이밍",
        "성장 루트",
    ],
    "life": [
        "기질 구조",
        "초·중·말년 흐름",
        "강점·보완",
        "평생 테마",
    ],
    "theme": [
        "핵심 요약",
        "상세 해석",
        "주의 포인트",
        "실천 제안",
    ],
    "free": [
        "간단 요약",
        "오늘의 팁",
    ],
}

products = []
for e in extract:
    url = e.get("url") or ""
    d = e.get("data") or {}
    title = (d.get("title") or "").strip()
    if not title or title in ("오늘만 반값", "운세의 신"):
        continue
    m = re.search(r"cid=(\d+)", url)
    cid = m.group(1) if m else None
    price_raw = d.get("price")
    price = None
    if price_raw is not None:
        try:
            price = int(str(price_raw).replace(",", "").replace("원", "").strip())
        except ValueError:
            price = None
    if price is None and cid and cid in price_by_cid:
        price = price_by_cid[cid]
    if price is None:
        price = 3900

    cat_id, cat_label = guess_category(title)
    fo_title = rewrite_title(title)
    slug = f"p{cid}" if cid else f"x{abs(hash(title)) % 10_000_000}"

    products.append(
        {
            "id": slug,
            "source_cid": cid,
            "source_url": url,
            "category_id": cat_id,
            "category_label": cat_label,
            "title": fo_title,
            "source_title": title,  # internal ref only, not for UI copy of body
            "price_krw": price,
            "currency": "KRW",
            "needs_profile": True,
            "needs_partner": cat_id in ("compat",) or "궁합" in title or "두 사람" in title,
            "is_free": price == 0 or cat_id == "free",
            "preview_sections": ["운세 소개", "이런 분께", "구성 미리보기"],
            "result_sections": SECTION_TEMPLATES.get(cat_id, SECTION_TEMPLATES["theme"]),
            "tone": {
                "newyear": "roadmap",
                "love": "narrative",
                "marriage": "narrative",
                "compat": "analytical",
                "money": "practical",
                "career": "practical",
                "life": "deep",
                "theme": "light",
                "free": "light",
            }.get(cat_id, "light"),
            "payment": {
                "methods_mock": [
                    "신용카드",
                    "간편결제(네이버/카카오/삼성)",
                    "휴대폰",
                    "계좌이체",
                    "문화상품권",
                ],
                "result_view_days_web": 7,
                "result_view_days_email": 30,
            },
        }
    )

# dedupe by source_cid or title
uniq = {}
for p in products:
    key = p["source_cid"] or p["title"]
    if key not in uniq:
        uniq[key] = p
products = list(uniq.values())
products.sort(key=lambda x: (x["category_id"], x["price_krw"], x["title"]))

menu = [
    {"id": "home", "label": "홈", "href": "/"},
    {"id": "newyear", "label": "신년·연간", "href": "/store?cat=newyear"},
    {"id": "love", "label": "연애·인연", "href": "/store?cat=love"},
    {"id": "marriage", "label": "결혼", "href": "/store?cat=marriage"},
    {"id": "compat", "label": "궁합", "href": "/store?cat=compat"},
    {"id": "money", "label": "재물", "href": "/store?cat=money"},
    {"id": "career", "label": "직장·사업", "href": "/store?cat=career"},
    {"id": "life", "label": "평생사주", "href": "/store?cat=life"},
    {"id": "theme", "label": "테마", "href": "/store?cat=theme"},
    {"id": "free", "label": "무료", "href": "/store?cat=free"},
    {"id": "tarot", "label": "타로", "href": "/tarot"},
    {"id": "today", "label": "오늘·띠별", "href": "/today"},
    {"id": "hub", "label": "내 운세", "href": "/hub"},
    {"id": "shop", "label": "구슬·충전", "href": "/shop"},
]

out = {
    "version": 1,
    "brand": "FortuneOne",
    "note": "Catalog structure benchmarked from sample IA; titles rewritten; body text is FO-generated placeholders.",
    "menu": menu,
    "categories": [
        {"id": c, "label": l} for c, l, _ in CATEGORY_RULES
    ],
    "products": products,
    "payment_module": {
        "mode": "mock",
        "fields": ["buyer_name", "email", "phone", "agree_privacy", "agree_age14"],
        "notices": [
            "결제 완료 후 뒤로가기·새로고침을 반복하지 마세요.",
            "결과 다시보기: 웹 7일 · 이메일 링크 30일(예정).",
            "본 서비스는 엔터테인먼트 목적이며 투자·법률 자문이 아닙니다.",
            "로컬 MVP는 모의 결제입니다. 실제 카드 청구가 없습니다.",
        ],
        "methods": [
            "신용카드",
            "간편결제",
            "휴대폰",
            "계좌이체",
            "문화상품권",
        ],
    },
    "engine_plan": {
        "current": "sajupy (pillars) + FO templates",
        "recommended_multi_source": [
            "sajupy — pillars / lunar",
            "bazica-style or gracefullight/saju — ten gods / chart features",
            "hoonsikim/saju JS logic port — element / day master checks",
            "custom FO narrative layer — product sections",
        ],
        "merge_strategy": "one chart fact layer + multi narrative modules per product tone",
    },
}

out_path = ROOT.parent / "superpowers" / "specs" / "2026-07-22-unsin-benchmark-catalog.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# also copy into backend for API
be = ROOT.parent.parent / "backend" / "app" / "data" / "product_catalog.json"
be.parent.mkdir(parents=True, exist_ok=True)
be.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

print("products", len(products))
print("wrote", out_path)
print("wrote", be)
print("categories", Counter := __import__("collections").Counter(p["category_id"] for p in products))
for k, v in Counter.most_common():
    print(f"  {k}: {v}")
