"""Tarot deck, spreads, shuffle session helpers."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

# (num, name, upright_3lines, reversed_3lines, color)
MAJOR = [
    ("0", "바보", "새로운 여정의 문턱에 서 있습니다. 완벽한 준비보다 한 걸음의 용기가 길을 엽니다. 가벼운 마음으로 시작하되, 기본 안전장치는 챙기세요.", "성급함이나 계획 없는 모험이 낭패로 이어질 수 있습니다. 한 박자 쉬어 정보를 모으고, 충동을 점검하세요. 무모함과 용기를 구분하는 것이 과제입니다.", "#7c3aed"),
    ("1", "마법사", "의지와 자원이 맞물리는 타이밍입니다. 이미 가진 도구·인맥·아이디어를 조합하면 성과가 납니다. 말로만 끝내지 말고 오늘 실행 한 가지를 하세요.", "능력은 있으나 방향이 흐리거나 과신이 독이 됩니다. 우선순위를 다시 정하고, 과장된 약속은 줄이세요. 실행 전 현실 점검이 필요합니다.", "#2563eb"),
    ("2", "여사제", "직관이 이성의 앞설 수 있는 흐름입니다. 드러나지 않은 정보·속마음을 살피면 답이 보입니다. 서두르기보다 침묵 속에서 신호를 읽으세요.", "비밀·오해·감정의 억압이 커질 수 있습니다. 회피하지 말고 안전한 방식으로 표현하세요. 직관만 믿다 사실을 놓치지 않도록 균형을 잡으세요.", "#4f46e5"),
    ("3", "여황제", "풍요와 돌봄의 기운이 돕습니다. 창작·관계·몸 돌보기에 좋은 시기입니다. 풍요를 ‘소비’가 아니라 ‘가꾸기’로 해석하면 더 오래갑니다.", "과보호·과소비·안주가 성장을 막을 수 있습니다. 의존을 줄이고 자립의 한 축을 세우세요. 풍요의 이면인 나태를 경계합니다.", "#db2777"),
    ("4", "황제", "질서·권위·구조가 힘을 발휘합니다. 규칙을 세우고 책임을 명확히 하면 안정이 옵니다. 리더십을 발휘하되 독선은 피하세요.", "경직·통제 과잉이 갈등을 부를 수 있습니다. 유연함을 섞고, 권위를 강요하기보다 설득하세요. 구조가 사람을 억누르지 않게 조정합니다.", "#b45309"),
    ("5", "교황", "전통과 가르침, 신념의 가이드가 필요합니다. 멘토·제도·검증된 방법을 따르면 안전합니다. 공동체의 지혜를 빌려 결정하세요.", "맹목적 순응이나 형식주의에 빠질 수 있습니다. 스스로의 신념을 점검하고, 필요하면 관습에서 한 걸음 벗어나세요.", "#0f766e"),
    ("6", "연인", "선택과 관계, 조화의 카드입니다. 마음의 끌림과 가치관이 일치하는지 확인하세요. 솔직한 대화가 인연을 깊게 만듭니다.", "우유부단·유혹·가치 충돌이 관계를 흔들 수 있습니다. 선택이 늦어질수록 비용이 커집니다. 기준을 정해 한쪽으로 무게를 두세요.", "#e11d48"),
    ("7", "전차", "추진력과 승리, 통제력이 살아납니다. 목표를 향해 집중하면 돌파가 가능합니다. 감정과 이성을 한 방향에 태우세요.", "과속·감정 충돌·방향 상실에 주의하세요. 브레이크 없이 달리면 사고 납니다. 잠시 정차해 목적지를 재확인합니다.", "#1d4ed8"),
    ("8", "힘", "부드러운 인내와 내면의 용기가 핵심입니다. 억지로 누르기보다 다독이며 이끌 때 힘이 납니다. 자신과 타인을 신뢰하세요.", "자신감 저하·억압·조급함이 균형을 깨뜨립니다. 강압 대신 설득을, 자책 대신 작은 승리를 쌓으세요.", "#ca8a04"),
    ("9", "은둔자", "성찰과 고독이 지혜를 줍니다. 혼자만의 시간이 답을 정리해 줍니다. 외부 소음보다 내면의 나침반을 보세요.", "고립·비관·소통 단절이 독이 될 수 있습니다. 필요한 도움은 요청하고, 은둔이 도피가 되지 않게 하세요.", "#57534e"),
    ("10", "운명의 수레바퀴", "전환과 기회의 순환이 돕습니다. 好运이 돌 때 준비된 사람이 잡습니다. 변화에 열려 있되 중심은 지키세요.", "불운의 순환·타이밍 놓침·무기력에 주의합니다. 통제 불가능한 일에 집착하지 말고, 할 수 있는 준비에 집중하세요.", "#7c3aed"),
    ("11", "정의", "균형·진실·책임이 중심입니다. 공정한 결정과 문서화가 당신을 보호합니다. 감정보다 사실로 말하세요.", "불공정·회피·이중 잣대가 갈등을 키웁니다. 책임을 미루면 비용이 커집니다. 솔직함으로 균형을 회복하세요.", "#0369a1"),
    ("12", "매달린 사람", "관점 전환과 기다림이 필요합니다. 당장 움직이지 못하는 것은 실패가 아니라 재정비입니다. 다른 각도에서 보면 출구가 보입니다.", "희생의 강요·정체·자기 비하를 경계하세요. 의미 없는 버팀보다 건강한 포기가 나을 때도 있습니다.", "#6d28d9"),
    ("13", "죽음", "끝과 시작, 재탄생의 문입니다. 낡은 관계를 정리해야 새 흐름이 들어옵니다. 변화의 아픔을 통과하면 가벼워집니다.", "변화 거부·집착·질질 끄는 마무리가 에너지를 뺏습니다. 의식적으로 ‘종료 의식’을 갖고 비우세요.", "#18181b"),
    ("14", "절제", "조화와 치유, 중용의 카드입니다. 과한 것을 줄이고 균형을 맞추면 회복됩니다. 시간과 재료를 섞듯 인내하세요.", "과잉·불균형·조급 혼합이 결과를 망칩니다. 한 번에 다 하려 하지 말고 비율을 조절하세요.", "#059669"),
    ("15", "악마", "집착과 그림자가 드러납니다. 욕망을 인정하되 지배당하지 마세요. 묶인 고리를 인식하는 순간 풀리기 시작합니다.", "중독·의존·유혹이 강해질 수 있습니다. 경계를 세우고, 건강한 탈출구를 만드세요. 혼자 버티기보다 도움을 요청합니다.", "#7f1d1d"),
    ("16", "탑", "급변과 각성의 충격이 올 수 있습니다. 무너지는 것은 약한 기반입니다. 충격을 배움으로 바꾸면 재건이 빠릅니다.", "예고된 위기를 외면하면 충격이 커집니다. 리스크를 점검하고, 비상 계획을 미리 세우세요.", "#9f1239"),
    ("17", "별", "희망과 치유, 영감이 돌아옵니다. 상처 후에도 빛은 남아 있습니다. 작은 믿음을 키우면 길이 열립니다.", "회의·낙담·방향 상실이 희망을 가릴 수 있습니다. 거대한 꿈보다 오늘 가능한 한 가지에 집중하세요.", "#0284c7"),
    ("18", "달", "불안과 환상, 무의식이 흔들 수 있습니다. 모든 그림자를 사실로 받아들이지 마세요. 검증 후에 움직이세요.", "오해·소문·공포가 과장될 수 있습니다. 밤에 큰 결정은 미루고, 아침에 다시 판단하세요.", "#312e81"),
    ("19", "태양", "성공·활력·명확함의 기운입니다. 자신감이 주변을 밝히고 성과가 드러납니다. 기쁨을 나누면 운이 더 커집니다.", "과열·자만·번아웃을 경계하세요. 빛도 그늘이 필요합니다. 휴식과 겸손을 챙기세요.", "#ea580c"),
    ("20", "심판", "부름과 결산, 용서의 시기입니다. 지난 선택을 정리하고 다음 챕터로 넘어가세요. 스스로를 사면할 때 길이 열립니다.", "자책·미루는 결산·후회 반복에 빠질 수 있습니다. 완벽한 해명보다 전진하는 한 걸음이 중요합니다.", "#b45309"),
    ("21", "세계", "완성·통합·성취의 카드입니다. 한 사이클이 마무리되고 시야가 넓어집니다. 성과를 인정하고 다음 무대를 준비하세요.", "미완성·지연·시야 협소에 답답할 수 있습니다. 마무리를 미루지 말고, 작은 완결을 만드세요.", "#15803d"),
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
    for num, name, upright, reversed_m, color in MAJOR:
        deck.append(
            {
                "id": f"major-{num}",
                "name": name,
                "arcana": "major",
                "suit": None,
                "rank": num,
                "upright": upright,
                "reversed": reversed_m,
                "image_key": f"major-{num.zfill(2) if num.isdigit() else num}",
                "color": color,
                "symbol": "✦",
            }
        )
    symbols = {"wands": "🜂", "cups": "🜄", "swords": "⚔", "pentacles": "⬤"}
    suit_theme = {
        "wands": ("열정과 행동", "추진이 과하면 소진"),
        "cups": ("감정과 관계", "감정에 휩쓸리면 판단이 흐려짐"),
        "swords": ("사고와 결단", "날카로움이 상처를 남길 수 있음"),
        "pentacles": ("현실과 재물", "물질에만 매몰되면 의미를 잃음"),
    }
    for suit_en, suit_ko, keywords, color in SUITS:
        theme_u, theme_r = suit_theme[suit_en]
        for i, (rank_en, rank_ko) in enumerate(RANKS):
            kw = keywords[i % len(keywords)]
            deck.append(
                {
                    "id": f"{suit_en}-{rank_en}",
                    "name": f"{suit_ko} {rank_ko}",
                    "arcana": "minor",
                    "suit": suit_en,
                    "rank": rank_en,
                    "upright": (
                        f"{suit_ko} {rank_ko}은(는) {theme_u}의 흐름을 보여 줍니다. "
                        f"핵심 키워드는 ‘{kw}’이며, 지금 상황에 이 에너지가 순조롭게 작동합니다. "
                        f"작은 실천 한 가지로 이 기운을 현실에 고정해 보세요."
                    ),
                    "reversed": (
                        f"{suit_ko} {rank_ko} 역방향은 {theme_r}을(를) 암시합니다. "
                        f"‘{kw}’가 막히거나 과한 상태일 수 있으니 속도를 조절하세요. "
                        f"한 박자 쉬어 원인부터 정리하면 다시 흐름이 열립니다."
                    ),
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
        f"{'질문을 마음에 두고 읽으면 메시지가 더 선명합니다. ' if question else ''}"
        f"각 카드의 해석을 포지션(위치)과 연결해 보면, 상황의 흐름이 이야기로 이어집니다. "
        f"직관을 믿되 오늘 할 수 있는 작은 행동 한 가지로 고정해 보세요. "
        f"타로 해석은 뽑을 때마다 달라질 수 있으며, 참고용 통찰로 활용하시기 바랍니다."
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
