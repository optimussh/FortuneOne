"""Mock affiliate catalog — map weak elements to lucky item suggestions."""

from __future__ import annotations

CATALOG: dict[str, list[dict]] = {
    "wood": [
        {
            "id": "wood-plant",
            "title": "미니 공기정화 식물",
            "reason": "목(木) 기운 보강 — 싱그러운 초록",
            "price_hint": "1~3만원대",
            "url": "https://www.coupang.com/",
            "partner": "coupang_mock",
        },
        {
            "id": "wood-tea",
            "title": "허브·녹차 샘플러",
            "reason": "아침 루틴에 나무의 생기를",
            "price_hint": "1만원대",
            "url": "https://www.coupang.com/",
            "partner": "coupang_mock",
        },
    ],
    "fire": [
        {
            "id": "fire-candle",
            "title": "아로마 캔들 (시트러스)",
            "reason": "화(火) — 공간에 온기와 활력",
            "price_hint": "1~2만원대",
            "url": "https://www.coupang.com/",
            "partner": "coupang_mock",
        },
        {
            "id": "fire-keyring",
            "title": "레드 포인트 키링",
            "reason": "재물·열정 상징 소품",
            "price_hint": "1만원 이하",
            "url": "https://www.aliexpress.com/",
            "partner": "ali_mock",
        },
    ],
    "earth": [
        {
            "id": "earth-ceramic",
            "title": "세라믹 머그·화분",
            "reason": "토(土) — 안정과 중심",
            "price_hint": "2만원대",
            "url": "https://www.coupang.com/",
            "partner": "coupang_mock",
        },
    ],
    "metal": [
        {
            "id": "metal-organizer",
            "title": "메탈 데스크 정리함",
            "reason": "금(金) — 정리·결단의 기운",
            "price_hint": "2~4만원대",
            "url": "https://www.coupang.com/",
            "partner": "coupang_mock",
        },
        {
            "id": "metal-bracelet",
            "title": "실버 톤 팔찌",
            "reason": "금속 소재로 기운 보완",
            "price_hint": "1~3만원대",
            "url": "https://www.aliexpress.com/",
            "partner": "ali_mock",
        },
    ],
    "water": [
        {
            "id": "water-diffuser",
            "title": "미니 가습기·디퓨저",
            "reason": "수(水) — 흐름과 휴식",
            "price_hint": "2~5만원대",
            "url": "https://www.coupang.com/",
            "partner": "coupang_mock",
        },
        {
            "id": "water-aquarium",
            "title": "데스크 어항/수경 소품",
            "reason": "물 기운을 공간에",
            "price_hint": "3만원대",
            "url": "https://www.coupang.com/",
            "partner": "coupang_mock",
        },
    ],
}


def recommend_for_elements(weak: list[str], limit: int = 4) -> list[dict]:
    items: list[dict] = []
    for el in weak or ["water", "wood"]:
        for p in CATALOG.get(el, []):
            items.append({**p, "element": el})
            if len(items) >= limit:
                return items
    # pad with popular
    if len(items) < limit:
        for el, prods in CATALOG.items():
            for p in prods:
                if p["id"] not in {x["id"] for x in items}:
                    items.append({**p, "element": el})
                if len(items) >= limit:
                    return items
    return items[:limit]
