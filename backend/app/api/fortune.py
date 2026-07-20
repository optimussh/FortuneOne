"""Public fortune endpoints — no auth required (some optional)."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user, get_optional_user
from app.core.database import get_session
from app.models.engagement import DailyTarotDraw, TarotSession
from app.models.user import User
from app.services.affiliate import recommend_for_elements
from app.services.saju_engine import SajuEngine, compatibility_score
from app.services.saju_report import build_full_report
from app.services.tarot_engine import (
    SPREADS,
    create_shuffle,
    draw_cards,
    reveal_picks,
)
from app.services.topic_fortune import TOPICS, build_topic_fortune
from app.services.zodiac import daily_for_all, daily_for_birth_year

router = APIRouter()
_engine = SajuEngine()

# In-process tarot shuffle sessions (works without migration; single-worker local)
_TAROT_MEM: dict[str, dict] = {}


class SajuRequest(BaseModel):
    solar_date: date
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    gender: Literal["male", "female"]
    time_unknown: bool = False


class StemBranchOut(BaseModel):
    stem: str
    branch: str


class PillarsOut(BaseModel):
    year: StemBranchOut
    month: StemBranchOut
    day: StemBranchOut
    hour: StemBranchOut | None


class DailyOut(BaseModel):
    date: date
    summary: str
    scores: dict[str, int]
    lucky: dict[str, str]


class YongsinOut(BaseModel):
    element: str
    element_ko: str
    reason: str
    lifestyle: list[str]


class DaeunOut(BaseModel):
    start_age: int
    end_age: int
    label: str
    note: str
    is_current: bool


class InputEcho(BaseModel):
    solar_date: date
    hour: int
    minute: int
    gender: str
    time_assumed: bool


class AffiliateItem(BaseModel):
    id: str
    title: str
    reason: str
    price_hint: str
    url: str
    partner: str
    element: str


class SajuResponse(BaseModel):
    input: InputEcho
    pillars: PillarsOut
    day_master: str
    elements: dict[str, int]
    daily: DailyOut
    weak_elements: list[str] = []
    strong_elements: list[str] = []
    yongsin: YongsinOut | None = None
    daeun: list[DaeunOut] = []
    lucky_items: list[AffiliateItem] = []


def _run_saju(body: SajuRequest):
    hour = body.hour
    minute = body.minute
    time_assumed = False
    if body.time_unknown:
        hour = 12
        minute = 0
        time_assumed = True
    try:
        result = _engine.calculate(
            solar_date=body.solar_date,
            hour=hour,
            minute=minute,
            gender=body.gender,
            time_assumed=time_assumed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=f"사주 계산 실패: {exc}") from exc
    return result, hour, minute, time_assumed


def _to_saju_response(result, body: SajuRequest, hour: int, minute: int, time_assumed: bool) -> SajuResponse:
    hour_out = None
    if result.pillars.hour is not None:
        hour_out = StemBranchOut(
            stem=result.pillars.hour.stem,
            branch=result.pillars.hour.branch,
        )
    yong = None
    if result.yongsin:
        yong = YongsinOut(
            element=result.yongsin.element,
            element_ko=result.yongsin.element_ko,
            reason=result.yongsin.reason,
            lifestyle=result.yongsin.lifestyle,
        )
    items = [
        AffiliateItem(**x)
        for x in recommend_for_elements(result.weak_elements)
    ]
    return SajuResponse(
        input=InputEcho(
            solar_date=body.solar_date,
            hour=hour,
            minute=minute,
            gender=body.gender,
            time_assumed=time_assumed,
        ),
        pillars=PillarsOut(
            year=StemBranchOut(stem=result.pillars.year.stem, branch=result.pillars.year.branch),
            month=StemBranchOut(stem=result.pillars.month.stem, branch=result.pillars.month.branch),
            day=StemBranchOut(stem=result.pillars.day.stem, branch=result.pillars.day.branch),
            hour=hour_out,
        ),
        day_master=result.day_master,
        elements=result.elements,
        daily=DailyOut(
            date=result.daily.date,
            summary=result.daily.summary,
            scores=result.daily.scores,
            lucky=result.daily.lucky,
        ),
        weak_elements=result.weak_elements,
        strong_elements=result.strong_elements,
        yongsin=yong,
        daeun=[
            DaeunOut(
                start_age=p.start_age,
                end_age=p.end_age,
                label=p.label,
                note=p.note,
                is_current=p.is_current,
            )
            for p in result.daeun
        ],
        lucky_items=items,
    )


@router.post("/saju", response_model=SajuResponse)
async def calculate_saju(body: SajuRequest) -> SajuResponse:
    result, hour, minute, time_assumed = _run_saju(body)
    return _to_saju_response(result, body, hour, minute, time_assumed)


@router.post("/full-report")
async def full_report(body: SajuRequest):
    """Public long-form report: 일운 · 2026 신년 · 오행 · 인생풀이."""
    result, hour, minute, time_assumed = _run_saju(body)
    _ = (hour, minute, time_assumed)
    return {
        "report": build_full_report(result, body.solar_date, body.gender),
        "input": {
            "solar_date": body.solar_date.isoformat(),
            "hour": 12 if body.time_unknown else body.hour,
            "minute": 0 if body.time_unknown else body.minute,
            "gender": body.gender,
            "time_assumed": body.time_unknown,
        },
    }


class TarotRequest(BaseModel):
    count: int = Field(default=1, ge=1, le=5)
    question: str = ""


class TarotCardOut(BaseModel):
    id: str
    name: str
    arcana: str
    reversed: bool
    meaning: str
    position: str
    image_key: str = ""
    color: str = "#6366f1"
    symbol: str = "✦"


class TarotResponse(BaseModel):
    question: str
    cards: list[TarotCardOut]
    summary: str


@router.post("/tarot", response_model=TarotResponse)
async def tarot_draw(body: TarotRequest) -> TarotResponse:
    """Legacy instant draw — prefer /tarot/shuffle + /tarot/reveal."""
    cards = draw_cards(body.count, question=body.question)
    joined = " · ".join(f"{c.position}: {c.name}{' (역)' if c.reversed else ''}" for c in cards)
    summary = f"뽑힌 카드 — {joined}. 직관을 믿되 현실 행동으로 이어 보세요."
    return TarotResponse(
        question=body.question,
        cards=[
            TarotCardOut(
                id=c.id,
                name=c.name,
                arcana=c.arcana,
                reversed=c.reversed,
                meaning=c.meaning,
                position=c.position,
                image_key=c.image_key,
                color=c.color,
                symbol=c.symbol,
            )
            for c in cards
        ],
        summary=summary,
    )


class TarotShuffleBody(BaseModel):
    spread: Literal["daily_one", "three", "five", "yesno"] = "three"
    question: str = ""
    is_daily: bool = False


@router.post("/tarot/shuffle")
async def tarot_shuffle(
    body: TarotShuffleBody,
    session: AsyncSession = Depends(get_session),
    user: Optional[User] = Depends(get_optional_user),
):
    try:
        data = create_shuffle(body.spread, body.question, is_daily=body.is_daily)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    expires = datetime.fromisoformat(data["expires_at"])
    _TAROT_MEM[data["session_id"]] = {
        "user_id": user.id if user else None,
        "spread": data["spread"],
        "question": body.question,
        "need": data["need"],
        "labels": data["labels"],
        "deck": data["deck_face_down"],
        "is_daily": body.is_daily,
        "revealed": False,
        "expires_at": expires,
    }

    public_deck = [{"slot_id": d["slot_id"]} for d in data["deck_face_down"]]
    return {
        "session_id": data["session_id"],
        "spread": data["spread"],
        "spread_title": data["spread_title"],
        "need": data["need"],
        "labels": data["labels"],
        "question": body.question,
        "is_daily": body.is_daily,
        "deck_face_down": public_deck,
    }


class TarotRevealBody(BaseModel):
    session_id: str
    picked_slot_ids: list[str]


@router.post("/tarot/reveal")
async def tarot_reveal(
    body: TarotRevealBody,
    session: AsyncSession = Depends(get_session),
):
    row = _TAROT_MEM.get(body.session_id)
    if not row or row["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="세션이 만료되었습니다. 다시 섞어 주세요.")
    if row["revealed"]:
        raise HTTPException(status_code=400, detail="이미 공개된 세션입니다")
    if len(body.picked_slot_ids) != row["need"]:
        raise HTTPException(status_code=400, detail=f"{row['need']}장을 선택해 주세요")

    try:
        result = reveal_picks(
            row["deck"], body.picked_slot_ids, row["labels"], row["question"]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    row["revealed"] = True

    if row["is_daily"] and row["user_id"] and result["cards"]:
        from app.api.engagement import today_kst

        today = today_kst()
        try:
            existing = await session.exec(
                select(DailyTarotDraw).where(
                    DailyTarotDraw.user_id == row["user_id"],
                    DailyTarotDraw.draw_date == today,
                )
            )
            if not existing.first():
                c0 = result["cards"][0]
                session.add(
                    DailyTarotDraw(
                        user_id=row["user_id"],
                        draw_date=today,
                        card_id=c0["id"],
                        reversed=c0["reversed"],
                        question=row["question"],
                        meaning=c0["meaning"],
                        name=c0["name"],
                        image_key=c0.get("image_key", ""),
                    )
                )
                await session.commit()
        except Exception:
            # table may not exist yet until server restart create_all
            pass

    return {"question": row["question"], "spread": row["spread"], **result}


class TopicBody(SajuRequest):
    topic: Literal["love", "money", "work", "health"] = "love"


@router.post("/topic")
async def topic_fortune(body: TopicBody):
    if body.topic not in TOPICS:
        raise HTTPException(status_code=400, detail="unknown topic")
    result, _, _, _ = _run_saju(body)
    return build_topic_fortune(result, body.topic)


@router.get("/tarot/daily/today")
async def daily_tarot_today(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    from app.api.engagement import today_kst

    today = today_kst()
    result = await session.exec(
        select(DailyTarotDraw).where(
            DailyTarotDraw.user_id == current_user.id,
            DailyTarotDraw.draw_date == today,
        )
    )
    row = result.first()
    if not row:
        return {"drawn": False, "date": today.isoformat()}
    return {
        "drawn": True,
        "date": today.isoformat(),
        "card": {
            "id": row.card_id,
            "name": row.name,
            "reversed": row.reversed,
            "meaning": row.meaning,
            "image_key": row.image_key,
            "position": "현재",
            "arcana": "major" if row.card_id.startswith("major") else "minor",
            "color": "#6366f1",
            "symbol": "✦",
        },
        "question": row.question,
    }


@router.get("/zodiac/today")
async def zodiac_today(as_of: date | None = Query(default=None)):
    return {"date": (as_of or date.today()).isoformat(), "items": daily_for_all(as_of)}


@router.get("/zodiac/by-year")
async def zodiac_by_year(year: int = Query(..., ge=1900, le=2100), as_of: date | None = None):
    return daily_for_birth_year(year, as_of)


class CompatPerson(BaseModel):
    solar_date: date
    hour: int = Field(default=12, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    gender: Literal["male", "female"] = "male"
    time_unknown: bool = True


class CompatRequest(BaseModel):
    a: CompatPerson
    b: CompatPerson


@router.post("/compatibility")
async def compatibility(body: CompatRequest):
    def to_req(p: CompatPerson) -> SajuRequest:
        return SajuRequest(
            solar_date=p.solar_date,
            hour=p.hour,
            minute=p.minute,
            gender=p.gender,
            time_unknown=p.time_unknown,
        )

    ra, ha, ma, ta = _run_saju(to_req(body.a))
    rb, hb, mb, tb = _run_saju(to_req(body.b))
    _ = (ha, ma, ta, hb, mb, tb)
    result = compatibility_score(ra, rb)
    return {
        **result,
        "a_pillars": {
            "day": {"stem": ra.pillars.day.stem, "branch": ra.pillars.day.branch},
        },
        "b_pillars": {
            "day": {"stem": rb.pillars.day.stem, "branch": rb.pillars.day.branch},
        },
    }


@router.get("/affiliate/recommendations")
async def affiliate_recs(elements: str = Query(default="water,wood")):
    weak = [e.strip() for e in elements.split(",") if e.strip()]
    return {"items": recommend_for_elements(weak)}
