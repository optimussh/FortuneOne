from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from pydantic import BaseModel

from app.core.database import get_session
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserCreate, UserRead, Token

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str
    password: str
    password_confirm: str


@router.post("/register", response_model=UserRead)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    if body.password != body.password_confirm:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다")

    result = await session.exec(select(User).where(User.email == body.email))
    if result.first():
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다")
        
    hashed_password = get_password_hash(body.password)
    user = User(
        email=body.email,
        full_name="",
        hashed_password=hashed_password,
        is_verified=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
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
    except:
        raise HTTPException(status_code=400, detail="유효하지 않은 토큰입니다")
