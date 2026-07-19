"""Simple Rider-Waite style tarot draw — deterministic optional seed."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date

MAJOR = [
    ("0", "바보", "새로운 시작, 자유, 모험"),
    ("1", "마법사", "의지, 자원 활용, 실행력"),
    ("2", "여사제", "직관, 비밀, 내면의 지혜"),
    ("3", "여황제", "풍요, 돌봄, 창조성"),
    ("4", "황제", "질서, 권위, 구조"),
    ("5", "교황", "전통, 가르침, 신념"),
    ("6", "연인", "선택, 관계, 조화"),
    ("7", "전차", "추진력, 승리, 통제"),
    ("8", "힘", "인내, 용기, 부드러운 힘"),
    ("9", "은둔자", "성찰, 고독, 탐구"),
    ("10", "운명의 수레바퀴", "전환, 기회, 순환"),
    ("11", "정의", "균형, 진실, 책임"),
    ("12", "매달린 사람", "관점 전환, 희생, 기다림"),
    ("13", "죽음", "끝과 시작, 재탄생"),
    ("14", "절제", "조화, 절제, 치유"),
    ("15", "악마", "집착, 속박, 그림자"),
    ("16", "탑", "붕괴, 각성, 급변"),
    ("17", "별", "희망, 치유, 영감"),
    ("18", "달", "불안, 환상, 무의식"),
    ("19", "태양", "성공, 활력, 명확함"),
    ("20", "심판", "부름, 결산, 용서"),
    ("21", "세계", "완성, 통합, 성취"),
]

SUITS = [
    ("완드", ["열정", "행동", "성장", "도전"]),
    ("컵", ["감정", "관계", "직감", "치유"]),
    ("소드", ["사고", "갈등", "진실", "결단"]),
    ("펜타클", ["현실", "재물", "안정", "성과"]),
]

RANKS = ["에이스", "2", "3", "4", "5", "6", "7", "8", "9", "10", "페이지", "나이트", "퀸", "킹"]


def _build_deck() -> list[dict]:
    deck: list[dict] = []
    for num, name, meaning in MAJOR:
        deck.append(
            {
                "id": f"major-{num}",
                "name": name,
                "arcana": "major",
                "upright": meaning,
                "reversed": f"{meaning}의 정체·지연·과잉에 주의",
            }
        )
    for suit, keywords in SUITS:
        for i, rank in enumerate(RANKS):
            kw = keywords[i % len(keywords)]
            deck.append(
                {
                    "id": f"{suit}-{rank}",
                    "name": f"{suit} {rank}",
                    "arcana": "minor",
                    "upright": f"{kw} — 흐름이 순조롭습니다",
                    "reversed": f"{kw} — 막힘이나 과함을 돌아보세요",
                }
            )
    return deck


DECK = _build_deck()


@dataclass
class DrawnCard:
    id: str
    name: str
    arcana: str
    reversed: bool
    meaning: str
    position: str


def draw_cards(
    count: int = 1,
    *,
    question: str = "",
    seed: int | None = None,
) -> list[DrawnCard]:
    count = max(1, min(count, 5))
    rng = random.Random(seed if seed is not None else (hash(question) ^ date.today().toordinal()))
    cards = DECK[:]
    rng.shuffle(cards)
    positions = {
        1: ["현재"],
        3: ["과거", "현재", "미래"],
        5: ["상황", "장애", "조언", "환경", "결과"],
    }
    labels = positions.get(count) or [f"카드{i+1}" for i in range(count)]
    drawn: list[DrawnCard] = []
    for i in range(count):
        c = cards[i]
        rev = rng.random() < 0.5
        drawn.append(
            DrawnCard(
                id=c["id"],
                name=c["name"],
                arcana=c["arcana"],
                reversed=rev,
                meaning=c["reversed"] if rev else c["upright"],
                position=labels[i] if i < len(labels) else f"카드{i+1}",
            )
        )
    return drawn
