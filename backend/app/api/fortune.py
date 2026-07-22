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
    chart_facts: dict | None = None


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
        chart_facts=getattr(result, "chart_facts", None),
    )


@router.get("/engines")
async def list_safe_engines():
    """Commercial-safe engine registry (MIT/Apache/BSD only)."""
    from app.services.engines.merge import COMMERCIAL_SAFE_ENGINES

    return {
        "policy": "Only MIT/Apache/BSD engines with explicit commercial use.",
        "engines": COMMERCIAL_SAFE_ENGINES,
    }


@router.post("/saju", response_model=SajuResponse)
async def calculate_saju(body: SajuRequest) -> SajuResponse:
    result, hour, minute, time_assumed = _run_saju(body)
    return _to_saju_response(result, body, hour, minute, time_assumed)


@router.post("/full-report")
async def full_report(body: SajuRequest):
    """Public long-form report — wealth_year is free-preview gated."""
    from app.services.monetization import apply_wealth_access

    result, hour, minute, time_assumed = _run_saju(body)
    _ = (hour, minute, time_assumed)
    report = build_full_report(result, body.solar_date, body.gender)
    if report.get("wealth_year"):
        report["wealth_year"] = apply_wealth_access(
            report["wealth_year"], unlocked=False, profile_is_self=True
        )
    return {
        "report": report,
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


class TarotShuffleBodyPaid(TarotShuffleBody):
    """Optional: pay beads for extra draw after daily free used."""

    use_beads: bool = False


@router.post("/tarot/shuffle")
async def tarot_shuffle(
    body: TarotShuffleBody,
    session: AsyncSession = Depends(get_session),
    user: Optional[User] = Depends(get_optional_user),
    use_beads: bool = Query(False),
):
    from app.api.engagement import today_kst
    from app.services import monetization as mon

    beads_charged = 0
    beads_balance = None
    # Daily free once; extra daily-style or re-draw needs beads when logged in
    if user and body.is_daily:
        today = today_kst()
        existing = await session.exec(
            select(DailyTarotDraw).where(
                DailyTarotDraw.user_id == user.id,
                DailyTarotDraw.draw_date == today,
            )
        )
        already = existing.first() is not None
        if already:
            # require beads for extra
            try:
                wallet = await mon.spend_beads(
                    session,
                    user.id,
                    mon.COSTS["tarot_extra"],
                    reason="tarot_extra",
                    meta="daily_redraw",
                )
                beads_charged = mon.COSTS["tarot_extra"]
                beads_balance = wallet.beads
            except ValueError as exc:
                raise HTTPException(
                    status_code=402,
                    detail=str(exc)
                    + f" · 오늘의 타로는 이미 뽑았습니다. 추가 뽑기는 구슬 {mon.COSTS['tarot_extra']}개.",
                ) from exc

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
        "extra_paid": beads_charged > 0,
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
        "beads_charged": beads_charged,
        "beads": beads_balance,
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
    """Birth input. solar_date = entered date (양력 그대로 / 음력이면 lunar YMD)."""

    solar_date: date  # entered calendar date (name kept for API compat)
    hour: int = Field(default=12, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    gender: Literal["male", "female"] = "male"
    time_unknown: bool = True
    calendar_type: Literal["solar", "lunar"] = "solar"
    display_name: str = ""
    time_slot: str | None = None
    is_leap_month: bool = False


class CompatRequest(BaseModel):
    a: CompatPerson
    b: CompatPerson


def _resolve_solar_date(p: CompatPerson) -> tuple[date, str, str]:
    """Return (solar_date_for_engine, birth_input_label, solar_used_iso)."""
    entered = p.solar_date
    if p.calendar_type == "lunar":
        try:
            from sajupy import lunar_to_solar

            lu = lunar_to_solar(
                entered.year,
                entered.month,
                entered.day,
                bool(p.is_leap_month),
            )
            solar = date(int(lu["solar_year"]), int(lu["solar_month"]), int(lu["solar_day"]))
            return (
                solar,
                f"음력 {entered.year}.{entered.month}.{entered.day}"
                + ("(윤)" if p.is_leap_month else ""),
                solar.isoformat(),
            )
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"음력 변환 실패 ({entered}): {exc}",
            ) from exc
    return (
        entered,
        f"양력 {entered.year}.{entered.month}.{entered.day}",
        entered.isoformat(),
    )


def _time_label(p: CompatPerson) -> str:
    if p.time_unknown:
        return "시간 모름 (정오 가정)"
    if p.time_slot:
        from app.services.saju_time import SAJU_HOURS

        for item in SAJU_HOURS:
            if item["key"] == p.time_slot:
                rng = item.get("range") or ""
                lab = item.get("label_short") or item["key"]
                return f"{lab} ({rng})" if rng else lab
    return f"{p.hour:02d}:{p.minute:02d}"


@router.post("/compatibility")
async def compatibility(body: CompatRequest):
    from app.services.compatibility import build_compatibility

    def run_person(p: CompatPerson):
        solar, birth_lab, solar_iso = _resolve_solar_date(p)
        req = SajuRequest(
            solar_date=solar,
            hour=p.hour,
            minute=p.minute,
            gender=p.gender,
            time_unknown=p.time_unknown,
        )
        result, hour, minute, time_assumed = _run_saju(req)
        meta = {
            "name": (p.display_name or "").strip() or ("A" if p is body.a else "B"),
            "gender": p.gender,
            "calendar_type": p.calendar_type,
            "birth_input": birth_lab,
            "solar_used": solar_iso,
            "time_text": _time_label(p),
            "time_unknown": p.time_unknown or time_assumed,
        }
        return result, meta, hour, minute

    ra, a_meta, _, _ = run_person(body.a)
    rb, b_meta, _, _ = run_person(body.b)
    # fix names if empty
    if a_meta["name"] == "A" and body.a.display_name:
        a_meta["name"] = body.a.display_name
    if b_meta["name"] == "B" and body.b.display_name:
        b_meta["name"] = body.b.display_name

    report = build_compatibility(ra, rb, a_meta=a_meta, b_meta=b_meta)
    return report


@router.get("/affiliate/recommendations")
async def affiliate_recs(elements: str = Query(default="water,wood")):
    weak = [e.strip() for e in elements.split(",") if e.strip()]
    return {"items": recommend_for_elements(weak)}
