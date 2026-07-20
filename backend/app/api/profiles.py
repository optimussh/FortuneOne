"""Auth-required fortune profile CRUD + full report."""

from __future__ import annotations

from datetime import date, datetime

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
    FortuneProfileUpdate,
)
from app.models.user import User
from app.services.saju_engine import SajuEngine
from app.services.saju_report import build_full_report
from app.services.saju_time import hour_from_slot, slot_from_hour, ymd_to_date

router = APIRouter()
_engine = SajuEngine()


def _resolve_birth(body: FortuneProfileCreate | FortuneProfileUpdate) -> tuple[date, int | None, int | None, bool, str]:
    """Return solar_date, hour, minute, time_unknown, time_slot."""
    time_slot = getattr(body, "time_slot", None) or "unknown"
    if getattr(body, "time_unknown", None) is True:
        time_slot = "unknown"
    hour, time_unknown = hour_from_slot(time_slot)
    minute = 0 if hour is not None else None

    if body.birth_year and body.birth_month and body.birth_day:
        d = ymd_to_date(body.birth_year, body.birth_month, body.birth_day)
    elif getattr(body, "solar_date", None):
        d = body.solar_date  # type: ignore[assignment]
    else:
        raise HTTPException(status_code=400, detail="생년월일을 입력해 주세요")

    # legacy hour override
    if getattr(body, "hour", None) is not None and not time_unknown:
        hour = body.hour
        minute = getattr(body, "minute", None) or 0
        time_slot = slot_from_hour(hour, False)

    return d, hour, minute, time_unknown, time_slot


def _to_read(p: FortuneProfile) -> FortuneProfileRead:
    return FortuneProfileRead(
        id=p.id,  # type: ignore[arg-type]
        user_id=p.user_id,
        label=p.label,
        display_name=getattr(p, "display_name", "") or "",
        solar_date=p.solar_date,
        hour=p.hour,
        minute=p.minute,
        time_unknown=p.time_unknown,
        time_slot=getattr(p, "time_slot", None) or slot_from_hour(p.hour, p.time_unknown),
        gender=p.gender,
        calendar_type=getattr(p, "calendar_type", None) or "solar",
        is_self=bool(getattr(p, "is_self", False)),
        created_at=p.created_at,
        birth_year=p.solar_date.year,
        birth_month=p.solar_date.month,
        birth_day=p.solar_date.day,
    )


def _profile_calc(profile: FortuneProfile):
    hour = profile.hour if profile.hour is not None else 12
    minute = profile.minute if profile.minute is not None else 0
    time_assumed = profile.time_unknown
    if time_assumed:
        hour, minute = 12, 0
    try:
        return _engine.calculate(
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


@router.get("/meta/form-options")
async def form_options():
    from app.services.saju_time import RELATION_LABELS, SAJU_HOURS

    years = list(range(2026, 1919, -1))
    return {
        "relations": RELATION_LABELS,
        "hours": SAJU_HOURS,
        "years": years,
        "months": list(range(1, 13)),
        "days": list(range(1, 32)),
        "calendar_types": [
            {"key": "solar", "label": "양력"},
            {"key": "lunar", "label": "음력"},
        ],
        "genders": [
            {"key": "male", "label": "남자"},
            {"key": "female", "label": "여자"},
        ],
    }


@router.get("", response_model=list[FortuneProfileRead])
async def list_profiles(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(FortuneProfile)
        .where(FortuneProfile.user_id == current_user.id)
        .order_by(FortuneProfile.is_self.desc(), FortuneProfile.created_at.asc())
    )
    return [_to_read(p) for p in result.all()]


@router.post("", response_model=FortuneProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    body: FortuneProfileCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    d, hour, minute, time_unknown, time_slot = _resolve_birth(body)
    is_self = body.is_self or body.label in ("본인", "나")
    profile = FortuneProfile(
        user_id=current_user.id,
        label=body.label or "본인",
        display_name=body.display_name or "",
        solar_date=d,
        hour=hour,
        minute=minute,
        time_unknown=time_unknown,
        time_slot=time_slot,
        gender=body.gender,
        calendar_type=body.calendar_type or "solar",
        is_self=is_self,
        updated_at=datetime.utcnow(),
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return _to_read(profile)


@router.api_route(
    "/{profile_id}",
    methods=["PATCH", "PUT"],
    response_model=FortuneProfileRead,
)
async def update_profile(
    profile_id: int,
    body: FortuneProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    profile = await session.get(FortuneProfile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")

    data = body.model_dump(exclude_unset=True)
    # rebuild birth if any birth fields
    if any(
        k in data
        for k in (
            "birth_year",
            "birth_month",
            "birth_day",
            "solar_date",
            "time_slot",
            "hour",
            "minute",
            "time_unknown",
        )
    ):
        # merge current into create-like
        create_like = FortuneProfileCreate(
            label=body.label or profile.label,
            display_name=body.display_name if body.display_name is not None else profile.display_name,
            birth_year=body.birth_year or profile.solar_date.year,
            birth_month=body.birth_month or profile.solar_date.month,
            birth_day=body.birth_day or profile.solar_date.day,
            time_slot=body.time_slot
            or getattr(profile, "time_slot", None)
            or slot_from_hour(profile.hour, profile.time_unknown),
            calendar_type=body.calendar_type
            or getattr(profile, "calendar_type", None)
            or "solar",  # type: ignore[arg-type]
            gender=body.gender or profile.gender,  # type: ignore[arg-type]
            is_self=body.is_self if body.is_self is not None else profile.is_self,
            solar_date=body.solar_date,
            hour=body.hour,
            minute=body.minute,
            time_unknown=body.time_unknown,
        )
        d, hour, minute, time_unknown, time_slot = _resolve_birth(create_like)
        profile.solar_date = d
        profile.hour = hour
        profile.minute = minute
        profile.time_unknown = time_unknown
        profile.time_slot = time_slot

    if body.label is not None:
        profile.label = body.label
    if body.display_name is not None:
        profile.display_name = body.display_name
    if body.gender is not None:
        profile.gender = body.gender
    if body.calendar_type is not None:
        profile.calendar_type = body.calendar_type
    if body.is_self is not None:
        profile.is_self = body.is_self
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return _to_read(profile)


@router.get("/primary/full-report")
async def primary_full_report(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """본인 우선, 없으면 첫 프로필."""
    result = await session.exec(
        select(FortuneProfile)
        .where(FortuneProfile.user_id == current_user.id)
        .order_by(FortuneProfile.is_self.desc(), FortuneProfile.created_at.asc())
    )
    profile = result.first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="저장된 사주 프로필이 없습니다. 사주 정보를 먼저 등록해 주세요.",
        )
    eng = _profile_calc(profile)
    report = build_full_report(
        eng,
        profile.solar_date,
        profile.gender,
        display_name=getattr(profile, "display_name", "") or "",
        calendar_type=getattr(profile, "calendar_type", None) or "solar",
        time_slot=getattr(profile, "time_slot", None),
        hour=profile.hour,
        time_unknown=profile.time_unknown,
    )
    return {
        "profile": _to_read(profile),
        "report": report,
    }


@router.get("/{profile_id}/full-report")
async def profile_full_report(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    profile = await session.get(FortuneProfile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
    eng = _profile_calc(profile)
    report = build_full_report(
        eng,
        profile.solar_date,
        profile.gender,
        display_name=getattr(profile, "display_name", "") or "",
        calendar_type=getattr(profile, "calendar_type", None) or "solar",
        time_slot=getattr(profile, "time_slot", None),
        hour=profile.hour,
        time_unknown=profile.time_unknown,
    )
    return {
        "profile": _to_read(profile),
        "report": report,
    }


@router.get("/{profile_id}", response_model=FortuneProfileRead)
async def get_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    profile = await session.get(FortuneProfile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
    return _to_read(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
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
    profile = await session.get(FortuneProfile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")

    hour = profile.hour if profile.hour is not None else 12
    minute = profile.minute if profile.minute is not None else 0
    time_assumed = profile.time_unknown
    if time_assumed:
        hour, minute = 12, 0

    result = _profile_calc(profile)
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
