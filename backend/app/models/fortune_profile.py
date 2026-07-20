from datetime import date, datetime
from typing import Literal, Optional

from sqlmodel import Field, SQLModel


class FortuneProfile(SQLModel, table=True):
    __tablename__ = "fortune_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    # 관계 라벨: 본인/엄마/애인…
    label: str = Field(default="본인", max_length=100)
    # 표시 이름
    display_name: str = Field(default="", max_length=100)
    solar_date: date
    hour: Optional[int] = Field(default=None, ge=0, le=23)
    minute: Optional[int] = Field(default=None, ge=0, le=59)
    time_unknown: bool = False
    # 자시·축시… or unknown
    time_slot: str = Field(default="unknown", max_length=32)
    gender: str = Field(max_length=16)  # male | female
    # solar | lunar (lunar stored as entered; engine uses solar_date as-is for MVP)
    calendar_type: str = Field(default="solar", max_length=16)
    is_self: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FortuneProfileCreate(SQLModel):
    label: str = "본인"
    display_name: str = ""
    # Preferred detailed form fields
    birth_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    birth_month: Optional[int] = Field(default=None, ge=1, le=12)
    birth_day: Optional[int] = Field(default=None, ge=1, le=31)
    time_slot: str = "unknown"
    calendar_type: Literal["solar", "lunar"] = "solar"
    gender: Literal["male", "female"]
    is_self: bool = False
    # Legacy / alternate
    solar_date: Optional[date] = None
    hour: Optional[int] = Field(default=None, ge=0, le=23)
    minute: Optional[int] = Field(default=None, ge=0, le=59)
    time_unknown: Optional[bool] = None


class FortuneProfileUpdate(SQLModel):
    label: Optional[str] = None
    display_name: Optional[str] = None
    birth_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    birth_month: Optional[int] = Field(default=None, ge=1, le=12)
    birth_day: Optional[int] = Field(default=None, ge=1, le=31)
    time_slot: Optional[str] = None
    calendar_type: Optional[Literal["solar", "lunar"]] = None
    gender: Optional[Literal["male", "female"]] = None
    is_self: Optional[bool] = None
    solar_date: Optional[date] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    time_unknown: Optional[bool] = None


class FortuneProfileRead(SQLModel):
    id: int
    user_id: int
    label: str
    display_name: str = ""
    solar_date: date
    hour: Optional[int]
    minute: Optional[int]
    time_unknown: bool
    time_slot: str = "unknown"
    gender: str
    calendar_type: str = "solar"
    is_self: bool = False
    created_at: datetime
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
