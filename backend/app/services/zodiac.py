"""Korean 12-zodiac (띠) daily fortunes — deterministic by date."""

from __future__ import annotations

from datetime import date

ZODIACS = [
    ("쥐", "rat"),
    ("소", "ox"),
    ("호랑이", "tiger"),
    ("토끼", "rabbit"),
    ("용", "dragon"),
    ("뱀", "snake"),
    ("말", "horse"),
    ("양", "goat"),
    ("원숭이", "monkey"),
    ("닭", "rooster"),
    ("개", "dog"),
    ("돼지", "pig"),
]

_LINES = [
    "작은 협력이 큰 결과를 만듭니다. 연락 한 통이 기회를 부릅니다.",
    "집중이 잘 되는 날. 중요한 일을 오전 중에 처리하세요.",
    "감정 기복에 주의. 충분한 수면이 운을 지켜 줍니다.",
    "지출보다 저축이 이득. 충동 구매를 한 번 더 고민하세요.",
    "새로운 만남·정보가 유입됩니다. 메모해 두면 나중에 쓸모 있습니다.",
    "건강 루틴을 지키면 컨디션이 안정됩니다.",
    "표현이 통하는 날. 거절도 부드럽게 전달할 수 있습니다.",
    "계획 수정이 필요할 수 있습니다. 유연함이 득이 됩니다.",
]


def year_to_zodiac(year: int) -> tuple[str, str]:
    # 2020 was 쥐 (rat); cycle every 12
    idx = (year - 2020) % 12
    return ZODIACS[idx]


def daily_for_all(as_of: date | None = None) -> list[dict]:
    d = as_of or date.today()
    base = d.toordinal()
    out = []
    for i, (ko, en) in enumerate(ZODIACS):
        seed = base * 17 + i * 97
        score = 45 + (seed % 50)
        out.append(
            {
                "zodiac": ko,
                "zodiac_en": en,
                "date": d.isoformat(),
                "score": score,
                "summary": _LINES[seed % len(_LINES)],
                "lucky_color": ["파랑", "빨강", "노랑", "흰", "검정", "초록"][seed % 6],
                "do": "감사 인사·정리 정돈" if score >= 70 else "무리한 약속 자제",
                "dont": "감정 소모 논쟁" if score < 60 else "게으름",
            }
        )
    return out


def daily_for_birth_year(year: int, as_of: date | None = None) -> dict:
    ko, en = year_to_zodiac(year)
    all_items = {x["zodiac"]: x for x in daily_for_all(as_of)}
    item = all_items[ko]
    return {**item, "birth_year": year}
