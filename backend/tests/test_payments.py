from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import payments
from app.services.payments.factory import payment_public_config
from app.services.payments.mock_provider import MockPaymentProvider


def test_payment_config_public():
    cfg = payment_public_config()
    assert cfg["provider"] in ("mock", "toss")
    assert "business" in cfg
    assert "instructions" in cfg


def test_mock_provider_confirm():
    p = MockPaymentProvider()
    c = p.create_payment(
        order_id="fo_test_1",
        amount_krw=1000,
        order_name="test",
        customer_key="user_1",
        success_url="http://localhost/ok",
        fail_url="http://localhost/fail",
    )
    assert c.mock_auto_confirm is True
    conf = p.confirm_payment(
        payment_key=f"mock_{c.order_id}",
        order_id=c.order_id,
        amount_krw=1000,
    )
    assert conf.ok is True


def test_payments_config_endpoint():
    app = FastAPI()
    app.include_router(payments.router, prefix="/api/payments")
    client = TestClient(app)
    r = client.get("/api/payments/config")
    assert r.status_code == 200
    assert "provider" in r.json()
