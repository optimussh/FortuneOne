"""Engagement models: streak, journal, daily tarot, tarot sessions."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint


class UserStreak(SQLModel, table=True):
    __tablename__ = "user_streaks"

    user_id: int = Field(primary_key=True, foreign_key="user.id")
    current_streak: int = 0
    longest_streak: int = 0
    last_checkin_date: Optional[date] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCheckin(SQLModel, table=True):
    __tablename__ = "user_checkins"
    __table_args__ = (UniqueConstraint("user_id", "checkin_date", name="uq_user_checkin_date"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    checkin_date: date
    source: str = Field(default="hub", max_length=32)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FortuneJournal(SQLModel, table=True):
    __tablename__ = "fortune_journals"
    __table_args__ = (UniqueConstraint("user_id", "entry_date", name="uq_journal_user_date"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    entry_date: date
    mood: Optional[int] = Field(default=None, ge=1, le=5)
    body: str = Field(default="", max_length=1000)
    linked_overall_score: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DailyTarotDraw(SQLModel, table=True):
    __tablename__ = "daily_tarot_draws"
    __table_args__ = (UniqueConstraint("user_id", "draw_date", name="uq_daily_tarot"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    draw_date: date
    card_id: str = Field(max_length=64)
    reversed: bool = False
    question: str = Field(default="", max_length=500)
    meaning: str = Field(default="", max_length=2000)
    name: str = Field(default="", max_length=100)
    image_key: str = Field(default="", max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TarotSession(SQLModel, table=True):
    __tablename__ = "tarot_sessions"

    id: str = Field(primary_key=True, max_length=36)  # uuid
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    spread: str = Field(max_length=32)
    question: str = Field(default="", max_length=500)
    need: int = 1
    # JSON: list of {slot_id, card_id}
    deck_json: str = Field(default="[]")
    # JSON: picked slot order
    picked_json: str = Field(default="[]")
    is_daily: bool = False
    revealed: bool = False
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
