"""Resolve payment provider from settings."""

from __future__ import annotations

from app.core.config import settings
from app.services.payments.mock_provider import MockPaymentProvider
from app.services.payments.toss_provider import TossPaymentProvider


def get_payment_provider():
    name = (settings.PAYMENT_PROVIDER or "mock").lower().strip()
    if name == "toss":
        # If keys missing, fall back to mock so local still works
        if not (settings.TOSS_CLIENT_KEY and settings.TOSS_SECRET_KEY):
            return MockPaymentProvider()
        return TossPaymentProvider()
    return MockPaymentProvider()


def payment_public_config() -> dict:
    provider = get_payment_provider()
    configured_toss = bool(settings.TOSS_CLIENT_KEY and settings.TOSS_SECRET_KEY)
    return {
        "provider": provider.name,
        "test_mode": settings.PAYMENT_TEST_MODE,
        "toss_configured": configured_toss,
        "client_key": (
            settings.TOSS_CLIENT_KEY
            if provider.name == "toss" and settings.TOSS_CLIENT_KEY
            else ("mock_client_key" if provider.name == "mock" else None)
        ),
        "frontend_url": settings.FRONTEND_URL,
        "business": {
            "name": settings.BUSINESS_NAME,
            "ceo": settings.BUSINESS_CEO,
            "business_number": settings.BUSINESS_NUMBER,
            "mail_order": settings.BUSINESS_MAIL_ORDER,
            "address": settings.BUSINESS_ADDRESS,
            "phone": settings.BUSINESS_PHONE,
            "email": settings.BUSINESS_EMAIL,
        },
        "ready_for_live": (
            provider.name == "toss"
            and configured_toss
            and not (settings.TOSS_CLIENT_KEY or "").startswith("test_")
            and not settings.PAYMENT_TEST_MODE
        ),
        "instructions": {
            "mock": "PAYMENT_PROVIDER=mock — 키 없이 전체 결제 플로우 테스트",
            "toss_test": "PAYMENT_PROVIDER=toss + test_ck_/test_sk_ 키 — 토스 샌드박스",
            "toss_live": "live_ck_/live_sk_ + PAYMENT_TEST_MODE=false",
        },
    }
