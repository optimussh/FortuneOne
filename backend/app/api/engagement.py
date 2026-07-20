"""Streak / check-in APIs (auth)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.engagement import UserCheckin, UserStreak
from app.models.user import User

router = APIRouter()


def today_kst() -> date:
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Seoul")).date()
    except Exception:
        return (datetime.utcnow() + timedelta(hours=9)).date()


class CheckinBody(BaseModel):
    source: Literal["hub", "daily", "tarot", "journal"] = "hub"


class StreakOut(BaseModel):
    current_streak: int
    longest_streak: int
    last_checkin_date: Optional[date]
    already_checked_in_today: bool
    recent_7: list[bool]


async def _get_or_create_streak(session: AsyncSession, user_id: int) -> UserStreak:
    row = await session.get(UserStreak, user_id)
    if not row:
        row = UserStreak(user_id=user_id)
        session.add(row)
        await session.commit()
        await session.refresh(row)
    return row


@router.get("/streak", response_model=StreakOut)
async def get_streak(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    today = today_kst()
    streak = await _get_or_create_streak(session, current_user.id)
    already = streak.last_checkin_date == today
    recent = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        r = await session.exec(
            select(UserCheckin).where(
                UserCheckin.user_id == current_user.id,
                UserCheckin.checkin_date == d,
            )
        )
        recent.append(r.first() is not None)
    return StreakOut(
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        last_checkin_date=streak.last_checkin_date,
        already_checked_in_today=already,
        recent_7=recent,
    )


@router.post("/checkin", response_model=StreakOut)
async def checkin(
    body: CheckinBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    today = today_kst()
    streak = await _get_or_create_streak(session, current_user.id)

    if streak.last_checkin_date == today:
        return await get_streak(current_user, session)

    # existing checkin row?
    existing = await session.exec(
        select(UserCheckin).where(
            UserCheckin.user_id == current_user.id,
            UserCheckin.checkin_date == today,
        )
    )
    if not existing.first():
        session.add(
            UserCheckin(user_id=current_user.id, checkin_date=today, source=body.source)
        )

    yesterday = today - timedelta(days=1)
    if streak.last_checkin_date == yesterday:
        streak.current_streak += 1
    else:
        streak.current_streak = 1
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.last_checkin_date = today
    streak.updated_at = datetime.utcnow()
    session.add(streak)
    await session.commit()
    return await get_streak(current_user, session)
