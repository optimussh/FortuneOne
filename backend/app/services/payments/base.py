"""Payment provider protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class CreatePaymentResult:
    order_id: str
    amount_krw: int
    provider: str
    # frontend needs these
    client_key: str | None = None  # Toss widget
    customer_key: str | None = None
    success_url: str = ""
    fail_url: str = ""
    # mock: auto-complete path
    mock_auto_confirm: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfirmPaymentResult:
    ok: bool
    order_id: str
    payment_key: str | None = None
    method: str | None = None
    amount_krw: int = 0
    raw: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class PaymentProvider(Protocol):
    name: str

    def create_payment(
        self,
        *,
        order_id: str,
        amount_krw: int,
        order_name: str,
        customer_key: str,
        success_url: str,
        fail_url: str,
    ) -> CreatePaymentResult: ...

    def confirm_payment(
        self,
        *,
        payment_key: str,
        order_id: str,
        amount_krw: int,
    ) -> ConfirmPaymentResult: ...
