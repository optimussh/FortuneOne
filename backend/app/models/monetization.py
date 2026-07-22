"""Wallet, content unlocks, bead ledger — local hybrid monetization."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint


class UserWallet(SQLModel, table=True):
    __tablename__ = "user_wallets"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, unique=True)
    beads: int = Field(default=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentUnlock(SQLModel, table=True):
    __tablename__ = "content_unlocks"
    __table_args__ = (
        UniqueConstraint("user_id", "product_key", name="uq_user_product_unlock"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    product_key: str = Field(index=True, max_length=64)  # e.g. wealth_2026 / product:p1
    source: str = Field(default="purchase", max_length=32)  # purchase | beads | grant | free
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Re-view windows (commercial policy template)
    # web_expires_at: logged-in web access (default +7d from grant/renew)
    # email_expires_at: magic link access (default +30d)
    web_expires_at: Optional[datetime] = None
    email_expires_at: Optional[datetime] = None
    email_token: Optional[str] = Field(default=None, index=True, max_length=64)
    profile_id: Optional[int] = None  # last profile used for result deep-link
    partner_profile_id: Optional[int] = None
    renewed_at: Optional[datetime] = None


class BeadLedger(SQLModel, table=True):
    __tablename__ = "bead_ledger"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    delta: int  # + purchase, - spend
    balance_after: int
    reason: str = Field(max_length=64)
    meta: str = Field(default="", max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DailyFreeUse(SQLModel, table=True):
    """Track free daily asks etc."""

    __tablename__ = "daily_free_uses"
    __table_args__ = (
        UniqueConstraint("user_id", "use_date", "kind", name="uq_daily_free_use"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    use_date: str = Field(max_length=10)  # YYYY-MM-DD
    kind: str = Field(max_length=32)  # ask, tarot_extra counted separately
    count: int = Field(default=0)
