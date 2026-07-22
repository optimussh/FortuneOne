"""Mock provider — full checkout test without Toss keys."""

from __future__ import annotations

from app.services.payments.base import ConfirmPaymentResult, CreatePaymentResult


class MockPaymentProvider:
    name = "mock"

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
        # Frontend can call confirm immediately with paymentKey=mock_...
        return CreatePaymentResult(
            order_id=order_id,
            amount_krw=amount_krw,
            provider="mock",
            client_key="mock_client_key",
            customer_key=customer_key,
            success_url=success_url,
            fail_url=fail_url,
            mock_auto_confirm=True,
            extra={
                "order_name": order_name,
                "hint": "Mock mode: call POST /api/payments/confirm with payment_key=mock_{order_id}",
            },
        )

    def confirm_payment(
        self,
        *,
        payment_key: str,
        order_id: str,
        amount_krw: int,
    ) -> ConfirmPaymentResult:
        if not payment_key.startswith("mock_"):
            # still accept for simplicity in tests
            payment_key = f"mock_{order_id}"
        return ConfirmPaymentResult(
            ok=True,
            order_id=order_id,
            payment_key=payment_key,
            method="mock_card",
            amount_krw=amount_krw,
            raw={"provider": "mock", "status": "DONE", "totalAmount": amount_krw},
        )
