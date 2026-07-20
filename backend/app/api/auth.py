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
    solar_date: date
    hour: int = Field(default=12, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    time_unknown: bool = True
    gender: Literal["male", "female"]
    label: str = "나"


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

    s = body.saju
    profile = FortuneProfile(
        user_id=user.id,
        label=s.label or "나",
        solar_date=s.solar_date,
        hour=None if s.time_unknown else s.hour,
        minute=None if s.time_unknown else s.minute,
        time_unknown=s.time_unknown,
        gender=s.gender,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    token = create_access_token(subject=user.id)
    return RegisterResponse(
        user=UserRead.model_validate(user, from_attributes=True),
        access_token=token,
        profile=FortuneProfileRead.model_validate(profile, from_attributes=True),
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
