"""Fortune journal APIs (auth)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.engagement import FortuneJournal
from app.models.fortune_profile import FortuneProfile
from app.models.user import User
from app.services.saju_engine import SajuEngine

router = APIRouter()
_engine = SajuEngine()


class JournalBody(BaseModel):
    mood: Optional[int] = Field(default=None, ge=1, le=5)
    body: str = Field(default="", max_length=1000)


class JournalOut(BaseModel):
    id: int
    entry_date: date
    mood: Optional[int]
    body: str
    linked_overall_score: Optional[int]
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=list[JournalOut])
async def list_journal(
    limit: int = Query(default=30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(FortuneJournal)
        .where(FortuneJournal.user_id == current_user.id)
        .order_by(FortuneJournal.entry_date.desc())
        .limit(limit)
    )
    return list(result.all())


@router.get("/{entry_date}", response_model=JournalOut)
async def get_journal(
    entry_date: date,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(FortuneJournal).where(
            FortuneJournal.user_id == current_user.id,
            FortuneJournal.entry_date == entry_date,
        )
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="일기 없음")
    return row


@router.put("/{entry_date}", response_model=JournalOut)
async def upsert_journal(
    entry_date: date,
    body: JournalBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(FortuneJournal).where(
            FortuneJournal.user_id == current_user.id,
            FortuneJournal.entry_date == entry_date,
        )
    )
    row = result.first()
    score = None
    # snapshot overall score from primary profile if possible
    try:
        pr = await session.exec(
            select(FortuneProfile)
            .where(FortuneProfile.user_id == current_user.id)
            .order_by(FortuneProfile.created_at.asc())
        )
        profile = pr.first()
        if profile:
            hour = 12 if profile.time_unknown else (profile.hour or 12)
            minute = 0 if profile.time_unknown else (profile.minute or 0)
            saju = _engine.calculate(
                profile.solar_date, hour, minute, profile.gender, as_of=entry_date
            )
            score = saju.daily.scores.get("overall")
    except Exception:
        score = None

    now = datetime.utcnow()
    if row:
        row.mood = body.mood
        row.body = body.body
        row.linked_overall_score = score if score is not None else row.linked_overall_score
        row.updated_at = now
        session.add(row)
    else:
        row = FortuneJournal(
            user_id=current_user.id,
            entry_date=entry_date,
            mood=body.mood,
            body=body.body,
            linked_overall_score=score,
            created_at=now,
            updated_at=now,
        )
        session.add(row)
    await session.commit()
    await session.refresh(row)
    return row
