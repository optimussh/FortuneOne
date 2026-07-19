"""Public fortune endpoints — no auth required."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.affiliate import recommend_for_elements
from app.services.saju_engine import SajuEngine, compatibility_score
from app.services.tarot_engine import draw_cards
from app.services.zodiac import daily_for_all, daily_for_birth_year

router = APIRouter()
_engine = SajuEngine()


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


class TarotResponse(BaseModel):
    question: str
    cards: list[TarotCardOut]
    summary: str


@router.post("/tarot", response_model=TarotResponse)
async def tarot_draw(body: TarotRequest) -> TarotResponse:
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
            )
            for c in cards
        ],
        summary=summary,
    )


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
