"""Streak / check-in APIs (auth) — milestones + bead rewards (B10)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.engagement import UserCheckin, UserStreak
from app.models.user import User
from app.services import monetization as mon

router = APIRouter()

# day streak -> beads
MILESTONES: dict[int, int] = {3: 2, 7: 5, 30: 15}


def today_kst() -> date:
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Seoul")).date()
    except Exception:
        return (datetime.utcnow() + timedelta(hours=9)).date()


class CheckinBody(BaseModel):
    source: Literal["hub", "daily", "tarot", "journal"] = "hub"


class MilestoneInfo(BaseModel):
    day: int
    beads: int
    achieved: bool
    claimed: bool
    label: str


class StreakOut(BaseModel):
    current_streak: int
    longest_streak: int
    last_checkin_date: Optional[date]
    already_checked_in_today: bool
    recent_7: list[bool]
    milestones: list[MilestoneInfo] = Field(default_factory=list)
    beads_awarded_today: int = 0
    reward_message: Optional[str] = None
    next_milestone: Optional[MilestoneInfo] = None


async def _get_or_create_streak(session: AsyncSession, user_id: int) -> UserStreak:
    row = await session.get(UserStreak, user_id)
    if not row:
        row = UserStreak(user_id=user_id)
        session.add(row)
        await session.commit()
        await session.refresh(row)
    return row


async def _milestone_claimed(session: AsyncSession, user_id: int, day: int) -> bool:
    from app.models.monetization import BeadLedger

    reason = f"streak_milestone_{day}"
    r = await session.exec(
        select(BeadLedger).where(
            BeadLedger.user_id == user_id,
            BeadLedger.reason == reason,
        )
    )
    return r.first() is not None


async def _build_milestones(
    session: AsyncSession, user_id: int, current: int
) -> list[MilestoneInfo]:
    out: list[MilestoneInfo] = []
    labels = {3: "3일 연속", 7: "7일 연속", 30: "30일 연속"}
    for day, beads in sorted(MILESTONES.items()):
        claimed = await _milestone_claimed(session, user_id, day)
        out.append(
            MilestoneInfo(
                day=day,
                beads=beads,
                achieved=current >= day,
                claimed=claimed,
                label=labels.get(day, f"{day}일"),
            )
        )
    return out


async def _streak_payload(
    session: AsyncSession,
    user_id: int,
    streak: UserStreak,
    *,
    beads_awarded: int = 0,
    reward_message: str | None = None,
) -> StreakOut:
    today = today_kst()
    already = streak.last_checkin_date == today
    recent = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        r = await session.exec(
            select(UserCheckin).where(
                UserCheckin.user_id == user_id,
                UserCheckin.checkin_date == d,
            )
        )
        recent.append(r.first() is not None)
    milestones = await _build_milestones(session, user_id, streak.current_streak)
    nxt = next((m for m in milestones if not m.achieved), None)
    return StreakOut(
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        last_checkin_date=streak.last_checkin_date,
        already_checked_in_today=already,
        recent_7=recent,
        milestones=milestones,
        beads_awarded_today=beads_awarded,
        reward_message=reward_message,
        next_milestone=nxt,
    )


@router.get("/streak", response_model=StreakOut)
async def get_streak(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    streak = await _get_or_create_streak(session, current_user.id)
    return await _streak_payload(session, current_user.id, streak)


@router.post("/checkin", response_model=StreakOut)
async def checkin(
    body: CheckinBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    today = today_kst()
    streak = await _get_or_create_streak(session, current_user.id)

    if streak.last_checkin_date == today:
        return await _streak_payload(session, current_user.id, streak)

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
    await session.refresh(streak)

    beads_awarded = 0
    messages: list[str] = []
    for day, amount in MILESTONES.items():
        if streak.current_streak == day:
            if not await _milestone_claimed(session, current_user.id, day):
                await mon.add_beads(
                    session,
                    current_user.id,
                    amount,
                    reason=f"streak_milestone_{day}",
                    meta=f"checkin_source={body.source}",
                )
                beads_awarded += amount
                messages.append(f"{day}일 연속 출석 보상 구슬 {amount}개")

    reward_message = " · ".join(messages) if messages else None
    return await _streak_payload(
        session,
        current_user.id,
        streak,
        beads_awarded=beads_awarded,
        reward_message=reward_message,
    )
