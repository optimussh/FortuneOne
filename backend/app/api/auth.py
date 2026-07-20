from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.fortune_profile import FortuneProfile, FortuneProfileRead
from app.models.user import Token, User, UserRead

router = APIRouter()


class SajuOnRegister(BaseModel):
    # Detailed form (preferred)
    display_name: str = ""
    label: str = "본인"
    birth_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    birth_month: Optional[int] = Field(default=None, ge=1, le=12)
    birth_day: Optional[int] = Field(default=None, ge=1, le=31)
    time_slot: str = "unknown"
    calendar_type: Literal["solar", "lunar"] = "solar"
    gender: Literal["male", "female"]
    # Legacy
    solar_date: Optional[date] = None
    hour: int = Field(default=12, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    time_unknown: bool = True


class RegisterRequest(BaseModel):
    email: str
    password: str
    password_confirm: str
    saju: Optional[SajuOnRegister] = None


class RegisterResponse(BaseModel):
    user: UserRead
    access_token: str
    token_type: str = "bearer"
    profile: Optional[FortuneProfileRead] = None


@router.post("/register", response_model=RegisterResponse)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    if body.password != body.password_confirm:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="비밀번호는 6자 이상이어야 합니다")

    result = await session.exec(select(User).where(User.email == body.email))
    if result.first():
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다")

    if body.saju is None:
        raise HTTPException(
            status_code=400,
            detail="사주 정보(생년월일·성별)를 입력해 주세요",
        )

    user = User(
        email=body.email,
        full_name="",
        hashed_password=get_password_hash(body.password),
        is_verified=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    from app.services.saju_time import hour_from_slot, ymd_to_date
    from app.api.profiles import _to_read

    s = body.saju
    if s.birth_year and s.birth_month and s.birth_day:
        solar = ymd_to_date(s.birth_year, s.birth_month, s.birth_day)
    elif s.solar_date:
        solar = s.solar_date
    else:
        raise HTTPException(status_code=400, detail="생년월일을 입력해 주세요")

    hour, time_unknown = hour_from_slot(s.time_slot or "unknown")
    if s.time_unknown and s.time_slot == "unknown":
        time_unknown = True
        hour = None
    profile = FortuneProfile(
        user_id=user.id,
        label=s.label or "본인",
        display_name=s.display_name or user.email.split("@")[0],
        solar_date=solar,
        hour=hour,
        minute=0 if hour is not None else None,
        time_unknown=time_unknown,
        time_slot=s.time_slot or "unknown",
        gender=s.gender,
        calendar_type=s.calendar_type or "solar",
        is_self=True,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    token = create_access_token(subject=user.id)
    return RegisterResponse(
        user=UserRead.model_validate(user, from_attributes=True),
        access_token=token,
        profile=_to_read(profile),
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(select(User).where(User.email == form_data.username))
    user = result.first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 올바르지 않습니다")

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def get_me(
    token: str = Depends(
        __import__("app.api.deps", fromlist=["oauth2_scheme"]).oauth2_scheme
    ),
    session: AsyncSession = Depends(get_session),
):
    from app.api.deps import get_current_user

    user = await get_current_user(token=token, session=session)
    return user


@router.post("/verify-email")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    try:
        user_id = int(token.split("-")[0])
        result = await session.exec(select(User).where(User.id == user_id))
        user = result.first()
        if not user:
            raise ValueError()

        user.is_verified = True
        session.add(user)
        await session.commit()
        return {"message": "이메일 인증이 완료되었습니다"}
    except Exception:
        raise HTTPException(status_code=400, detail="유효하지 않은 토큰입니다") from None
