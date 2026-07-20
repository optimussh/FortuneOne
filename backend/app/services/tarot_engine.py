"""Tarot deck, spreads, shuffle session helpers."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

MAJOR = [
    ("0", "바보", "새로운 시작, 자유, 모험", "#7c3aed"),
    ("1", "마법사", "의지, 자원 활용, 실행력", "#2563eb"),
    ("2", "여사제", "직관, 비밀, 내면의 지혜", "#4f46e5"),
    ("3", "여황제", "풍요, 돌봄, 창조성", "#db2777"),
    ("4", "황제", "질서, 권위, 구조", "#b45309"),
    ("5", "교황", "전통, 가르침, 신념", "#0f766e"),
    ("6", "연인", "선택, 관계, 조화", "#e11d48"),
    ("7", "전차", "추진력, 승리, 통제", "#1d4ed8"),
    ("8", "힘", "인내, 용기, 부드러운 힘", "#ca8a04"),
    ("9", "은둔자", "성찰, 고독, 탐구", "#57534e"),
    ("10", "운명의 수레바퀴", "전환, 기회, 순환", "#7c3aed"),
    ("11", "정의", "균형, 진실, 책임", "#0369a1"),
    ("12", "매달린 사람", "관점 전환, 희생, 기다림", "#6d28d9"),
    ("13", "죽음", "끝과 시작, 재탄생", "#18181b"),
    ("14", "절제", "조화, 절제, 치유", "#059669"),
    ("15", "악마", "집착, 속박, 그림자", "#7f1d1d"),
    ("16", "탑", "붕괴, 각성, 급변", "#9f1239"),
    ("17", "별", "희망, 치유, 영감", "#0284c7"),
    ("18", "달", "불안, 환상, 무의식", "#312e81"),
    ("19", "태양", "성공, 활력, 명확함", "#ea580c"),
    ("20", "심판", "부름, 결산, 용서", "#b45309"),
    ("21", "세계", "완성, 통합, 성취", "#15803d"),
]

SUITS = [
    ("wands", "완드", ["열정", "행동", "성장", "도전"], "#c2410c"),
    ("cups", "컵", ["감정", "관계", "직감", "치유"], "#1d4ed8"),
    ("swords", "소드", ["사고", "갈등", "진실", "결단"], "#475569"),
    ("pentacles", "펜타클", ["현실", "재물", "안정", "성과"], "#a16207"),
]

RANKS = [
    ("ace", "에이스"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
    ("page", "페이지"),
    ("knight", "나이트"),
    ("queen", "퀸"),
    ("king", "킹"),
]

SPREADS: dict[str, dict[str, Any]] = {
    "daily_one": {"need": 1, "labels": ["현재"], "title": "오늘의 한 장"},
    "three": {"need": 3, "labels": ["과거", "현재", "미래"], "title": "과거·현재·미래"},
    "five": {
        "need": 5,
        "labels": ["상황", "장애", "조언", "환경", "결과"],
        "title": "상황 조언 5장",
    },
    "yesno": {"need": 1, "labels": ["답"], "title": "예·아니오"},
}

DISPLAY_COUNT = 18  # face-down cards on table


def _build_deck() -> list[dict]:
    deck: list[dict] = []
    for num, name, meaning, color in MAJOR:
        deck.append(
            {
                "id": f"major-{num}",
                "name": name,
                "arcana": "major",
                "suit": None,
                "rank": num,
                "upright": meaning,
                "reversed": f"{meaning}의 정체·지연·과잉에 주의",
                "image_key": f"major-{num.zfill(2) if num.isdigit() else num}",
                "color": color,
                "symbol": "✦",
            }
        )
    symbols = {"wands": "🜂", "cups": "🜄", "swords": "⚔", "pentacles": "⬤"}
    for suit_en, suit_ko, keywords, color in SUITS:
        for i, (rank_en, rank_ko) in enumerate(RANKS):
            kw = keywords[i % len(keywords)]
            deck.append(
                {
                    "id": f"{suit_en}-{rank_en}",
                    "name": f"{suit_ko} {rank_ko}",
                    "arcana": "minor",
                    "suit": suit_en,
                    "rank": rank_en,
                    "upright": f"{kw} — 흐름이 순조롭습니다",
                    "reversed": f"{kw} — 막힘이나 과함을 돌아보세요",
                    "image_key": f"{suit_en}-{rank_en}",
                    "color": color,
                    "symbol": symbols[suit_en],
                }
            )
    return deck


DECK = _build_deck()
DECK_BY_ID = {c["id"]: c for c in DECK}


@dataclass
class DrawnCard:
    id: str
    name: str
    arcana: str
    reversed: bool
    meaning: str
    position: str
    image_key: str
    color: str
    symbol: str


def create_shuffle(
    spread: str,
    question: str = "",
    *,
    is_daily: bool = False,
    seed: int | None = None,
) -> dict[str, Any]:
    if spread not in SPREADS:
        raise ValueError(f"unknown spread: {spread}")
    if is_daily:
        spread = "daily_one"
    meta = SPREADS[spread]
    need = meta["need"]
    rng = random.Random(seed if seed is not None else (uuid.uuid4().int & 0xFFFFFFFF))
    cards = DECK[:]
    rng.shuffle(cards)
    shown = cards[:DISPLAY_COUNT]
    session_id = str(uuid.uuid4())
    deck_face_down = []
    for i, c in enumerate(shown):
        deck_face_down.append(
            {
                "slot_id": f"s{i}",
                "card_id": c["id"],  # client may not show until reveal; UI uses back
            }
        )
    return {
        "session_id": session_id,
        "spread": spread,
        "spread_title": meta["title"],
        "need": need,
        "labels": meta["labels"],
        "question": question,
        "is_daily": is_daily,
        "deck_face_down": deck_face_down,
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }


def reveal_picks(
    deck_face_down: list[dict],
    picked_slot_ids: list[str],
    labels: list[str],
    question: str = "",
    *,
    seed: int | None = None,
) -> dict[str, Any]:
    slot_map = {d["slot_id"]: d["card_id"] for d in deck_face_down}
    if len(picked_slot_ids) != len(set(picked_slot_ids)):
        raise ValueError("중복된 카드 선택입니다")
    for sid in picked_slot_ids:
        if sid not in slot_map:
            raise ValueError(f"invalid slot: {sid}")

    rng = random.Random(seed if seed is not None else hash(tuple(picked_slot_ids)) & 0xFFFFFFFF)
    drawn: list[DrawnCard] = []
    for i, sid in enumerate(picked_slot_ids):
        cid = slot_map[sid]
        meta = DECK_BY_ID[cid]
        rev = rng.random() < 0.45
        drawn.append(
            DrawnCard(
                id=meta["id"],
                name=meta["name"],
                arcana=meta["arcana"],
                reversed=rev,
                meaning=meta["reversed"] if rev else meta["upright"],
                position=labels[i] if i < len(labels) else f"카드{i+1}",
                image_key=meta["image_key"],
                color=meta["color"],
                symbol=meta["symbol"],
            )
        )

    joined = " · ".join(
        f"{c.position}: {c.name}{' (역)' if c.reversed else ''}" for c in drawn
    )
    summary = (
        f"당신이 고른 카드 — {joined}. "
        f"{'질문을 마음에 두고 ' if question else ''}"
        f"직관을 믿되, 현실에서 한 가지 행동으로 이어 보세요."
    )
    return {
        "cards": [
            {
                "id": c.id,
                "name": c.name,
                "arcana": c.arcana,
                "reversed": c.reversed,
                "meaning": c.meaning,
                "position": c.position,
                "image_key": c.image_key,
                "color": c.color,
                "symbol": c.symbol,
            }
            for c in drawn
        ],
        "summary": summary,
    }


def draw_cards(count: int = 1, *, question: str = "", seed: int | None = None) -> list[DrawnCard]:
    """Legacy instant draw (compat)."""
    spread = "daily_one" if count == 1 else "three" if count == 3 else "five"
    if count == 5:
        spread = "five"
    sh = create_shuffle(spread, question, seed=seed)
    picks = [d["slot_id"] for d in sh["deck_face_down"][: sh["need"]]]
    res = reveal_picks(sh["deck_face_down"], picks, sh["labels"], question, seed=seed)
    return [
        DrawnCard(
            id=c["id"],
            name=c["name"],
            arcana=c["arcana"],
            reversed=c["reversed"],
            meaning=c["meaning"],
            position=c["position"],
            image_key=c["image_key"],
            color=c["color"],
            symbol=c["symbol"],
        )
        for c in res["cards"]
    ]
