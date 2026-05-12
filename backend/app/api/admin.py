from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List

from app.api.deps import get_current_superuser
from app.core.database import get_session
from app.models.user import User, UserRead

router = APIRouter()

@router.get("/users", response_model=List[UserRead])
async def get_users(
    skip: int = 0, limit: int = 100, 
    current_user: User = Depends(get_current_superuser),
    session: AsyncSession = Depends(get_session)
):
    result = await session.exec(select(User).offset(skip).limit(limit))
    users = result.all()
    return users
