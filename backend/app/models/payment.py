"""Payment orders — mock / Toss ready."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PaymentOrder(SQLModel, table=True):
    __tablename__ = "payment_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(index=True, unique=True, max_length=64)
    user_id: int = Field(index=True)
    # store_product | beads_pack | wealth_year
    kind: str = Field(max_length=32, default="store_product")
    product_key: str = Field(max_length=128, default="")  # product:p123 / pack_200 / wealth_2026
    product_name: str = Field(max_length=255, default="")
    amount_krw: int = Field(default=0)
    currency: str = Field(default="KRW", max_length=8)
    status: str = Field(
        default="ready", max_length=32
    )  # ready | pending | paid | failed | canceled | expired
    provider: str = Field(default="mock", max_length=32)  # mock | toss
    # meta for unlock
    profile_id: Optional[int] = None
    partner_profile_id: Optional[int] = None
    buyer_name: str = Field(default="", max_length=100)
    buyer_email: str = Field(default="", max_length=200)
    buyer_phone: str = Field(default="", max_length=40)
    # provider fields
    payment_key: Optional[str] = Field(default=None, max_length=200)
    method: Optional[str] = Field(default=None, max_length=64)
    raw_confirm: Optional[str] = Field(default=None)  # json snippet
    fail_reason: Optional[str] = Field(default=None, max_length=500)
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
