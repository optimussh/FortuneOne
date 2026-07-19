"""Public fortune endpoints — no auth required."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.saju_engine import SajuEngine

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


class InputEcho(BaseModel):
    solar_date: date
    hour: int
    minute: int
    gender: str
    time_assumed: bool


class SajuResponse(BaseModel):
    input: InputEcho
    pillars: PillarsOut
    day_master: str
    elements: dict[str, int]
    daily: DailyOut


@router.post("/saju", response_model=SajuResponse)
async def calculate_saju(body: SajuRequest) -> SajuResponse:
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

    hour_out = None
    if result.pillars.hour is not None:
        hour_out = StemBranchOut(
            stem=result.pillars.hour.stem,
            branch=result.pillars.hour.branch,
        )

    return SajuResponse(
        input=InputEcho(
            solar_date=body.solar_date,
            hour=hour,
            minute=minute,
            gender=body.gender,
            time_assumed=time_assumed,
        ),
        pillars=PillarsOut(
            year=StemBranchOut(
                stem=result.pillars.year.stem,
                branch=result.pillars.year.branch,
            ),
            month=StemBranchOut(
                stem=result.pillars.month.stem,
                branch=result.pillars.month.branch,
            ),
            day=StemBranchOut(
                stem=result.pillars.day.stem,
                branch=result.pillars.day.branch,
            ),
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
    )
