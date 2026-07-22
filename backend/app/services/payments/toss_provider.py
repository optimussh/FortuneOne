"""
Toss Payments provider (test + live keys).

Docs: https://docs.tosspayments.com/reference
Confirm: POST https://api.tosspayments.com/v1/payments/confirm
Auth: Basic base64(secretKey + ':')
"""

from __future__ import annotations

import base64
from typing import Any

import httpx

from app.core.config import settings
from app.services.payments.base import ConfirmPaymentResult, CreatePaymentResult

TOSS_API = "https://api.tosspayments.com/v1"


class TossPaymentProvider:
    name = "toss"

    def __init__(self, client_key: str | None = None, secret_key: str | None = None):
        self.client_key = client_key or settings.TOSS_CLIENT_KEY or ""
        self.secret_key = secret_key or settings.TOSS_SECRET_KEY or ""

    def _configured(self) -> bool:
        return bool(self.client_key and self.secret_key)

    def create_payment(
        self,
        *,
        order_id: str,
        amount_krw: int,
        order_name: str,
        customer_key: str,
        success_url: str,
        fail_url: str,
    ) -> CreatePaymentResult:
        if not self._configured():
            raise RuntimeError(
                "Toss keys missing. Set TOSS_CLIENT_KEY and TOSS_SECRET_KEY, "
                "or use PAYMENT_PROVIDER=mock for local tests."
            )
        return CreatePaymentResult(
            order_id=order_id,
            amount_krw=amount_krw,
            provider="toss",
            client_key=self.client_key,
            customer_key=customer_key,
            success_url=success_url,
            fail_url=fail_url,
            mock_auto_confirm=False,
            extra={
                "order_name": order_name,
                "sdk": "https://js.tosspayments.com/v2/standard",
                "widget": "payment",
            },
        )

    def confirm_payment(
        self,
        *,
        payment_key: str,
        order_id: str,
        amount_krw: int,
    ) -> ConfirmPaymentResult:
        if not self.secret_key:
            return ConfirmPaymentResult(
                ok=False,
                order_id=order_id,
                error="TOSS_SECRET_KEY not set",
            )
        token = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        try:
            with httpx.Client(timeout=20.0) as client:
                res = client.post(
                    f"{TOSS_API}/payments/confirm",
                    headers={
                        "Authorization": f"Basic {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "paymentKey": payment_key,
                        "orderId": order_id,
                        "amount": amount_krw,
                    },
                )
            data: dict[str, Any] = res.json() if res.content else {}
            if res.status_code >= 400:
                msg = data.get("message") or data.get("code") or res.text
                return ConfirmPaymentResult(
                    ok=False,
                    order_id=order_id,
                    payment_key=payment_key,
                    error=str(msg),
                    raw=data,
                )
            return ConfirmPaymentResult(
                ok=True,
                order_id=order_id,
                payment_key=payment_key,
                method=str(data.get("method") or "card"),
                amount_krw=int(data.get("totalAmount") or amount_krw),
                raw=data,
            )
        except Exception as exc:
            return ConfirmPaymentResult(
                ok=False,
                order_id=order_id,
                payment_key=payment_key,
                error=str(exc),
            )
