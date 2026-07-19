"""Auth-required fortune profile CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.api.fortune import (
    DailyOut,
    InputEcho,
    PillarsOut,
    SajuResponse,
    StemBranchOut,
)
from app.core.database import get_session
from app.models.fortune_profile import (
    FortuneProfile,
    FortuneProfileCreate,
    FortuneProfileRead,
)
from app.models.user import User
from app.services.saju_engine import SajuEngine

router = APIRouter()
_engine = SajuEngine()


@router.get("", response_model=list[FortuneProfileRead])
async def list_profiles(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[FortuneProfile]:
    result = await session.exec(
        select(FortuneProfile)
        .where(FortuneProfile.user_id == current_user.id)
        .order_by(FortuneProfile.created_at.desc())
    )
    return list(result.all())


@router.post("", response_model=FortuneProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    body: FortuneProfileCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FortuneProfile:
    profile = FortuneProfile(
        user_id=current_user.id,
        label=body.label or "나",
        solar_date=body.solar_date,
        hour=None if body.time_unknown else body.hour,
        minute=None if body.time_unknown else body.minute,
        time_unknown=body.time_unknown,
        gender=body.gender,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=FortuneProfileRead)
async def get_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FortuneProfile:
    profile = await session.get(FortuneProfile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    profile = await session.get(FortuneProfile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
    await session.delete(profile)
    await session.commit()


@router.post("/{profile_id}/saju", response_model=SajuResponse)
async def calculate_profile_saju(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SajuResponse:
    """Load a saved profile and run the saju engine (auth)."""
    profile = await session.get(FortuneProfile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")

    hour = profile.hour if profile.hour is not None else 12
    minute = profile.minute if profile.minute is not None else 0
    time_assumed = profile.time_unknown
    if time_assumed:
        hour, minute = 12, 0

    try:
        result = _engine.calculate(
            solar_date=profile.solar_date,
            hour=hour,
            minute=minute,
            gender=profile.gender,
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
            solar_date=profile.solar_date,
            hour=hour,
            minute=minute,
            gender=profile.gender,
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
