from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str = ""
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Profile fields
    nickname: str = ""
    handle: str = ""  # @handle
    avatar_url: Optional[str] = None
    job_title: str = ""
    career_level: str = ""
    company: str = ""
    bio: str = ""

class UserCreate(SQLModel):
    email: str
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime
    nickname: str = ""
    handle: str = ""
    avatar_url: Optional[str] = None
    job_title: str = ""
    career_level: str = ""
    company: str = ""
    bio: str = ""

class UserProfileUpdate(SQLModel):
    nickname: Optional[str] = None
    handle: Optional[str] = None
    avatar_url: Optional[str] = None
    job_title: Optional[str] = None
    career_level: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    full_name: Optional[str] = None

class Token(SQLModel):
    access_token: str
    token_type: str
