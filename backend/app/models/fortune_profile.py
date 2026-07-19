from datetime import date, datetime
from typing import Literal, Optional

from sqlmodel import Field, SQLModel


class FortuneProfile(SQLModel, table=True):
    __tablename__ = "fortune_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    label: str = Field(default="나", max_length=100)
    solar_date: date
    hour: Optional[int] = Field(default=None, ge=0, le=23)
    minute: Optional[int] = Field(default=None, ge=0, le=59)
    time_unknown: bool = False
    gender: str = Field(max_length=16)  # male | female
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FortuneProfileCreate(SQLModel):
    label: str = "나"
    solar_date: date
    hour: Optional[int] = Field(default=None, ge=0, le=23)
    minute: Optional[int] = Field(default=None, ge=0, le=59)
    time_unknown: bool = False
    gender: Literal["male", "female"]


class FortuneProfileRead(SQLModel):
    id: int
    user_id: int
    label: str
    solar_date: date
    hour: Optional[int]
    minute: Optional[int]
    time_unknown: bool
    gender: str
    created_at: datetime
