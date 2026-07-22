"""
Payment API — mock-testable + Toss-ready.

Flow:
1. POST /api/payments/orders  → create order + provider payload
2. (mock) POST /api/payments/confirm with payment_key=mock_{orderId}
   (toss) Widget pays → success URL → POST /api/payments/confirm
3. POST /api/payments/webhook  → optional Toss events (logged)
"""

from __future__ import annotations

import json
import secrets
import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_session
from app.models.payment import PaymentOrder
from app.models.user import User
from app.services.payments.factory import get_payment_provider, payment_public_config
from app.services.payments.fulfill import fulfill_order
from app.services.product_catalog import get_product, product_unlock_key
from app.services import monetization as mon

router = APIRouter()


def _new_order_id() -> str:
    # Toss: 6–64 chars, no special except - _
    return f"fo_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"


@router.get("/config")
async def payments_config():
    """Public config for frontend (no secrets)."""
    return payment_public_config()


class CreateOrderBody(BaseModel):
    kind: Literal["store_product", "wealth_year", "beads_pack"] = "store_product"
    product_id: str = Field(..., description="store product id | pack_200 | wealth_2026")
    profile_id: Optional[int] = None
    partner_profile_id: Optional[int] = None
    buyer_name: str = ""
    email: str = ""
    phone: str = ""
    agree_privacy: bool = False
    agree_age14: bool = False


@router.post("/orders")
async def create_order(
    body: CreateOrderBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not body.agree_privacy or not body.agree_age14:
        raise HTTPException(status_code=400, detail="필수 약관에 동의해 주세요")

    amount = 0
    product_name = body.product_id
    product_key = body.product_id
    result_path = "/hub"

    if body.kind == "store_product":
        p = get_product(body.product_id)
        if not p:
            raise HTTPException(status_code=404, detail="상품 없음")
        amount = 0 if p.get("is_free") else int(p.get("price_krw") or 0)
        product_name = p.get("title") or body.product_id
        product_key = product_unlock_key(body.product_id)
        if not body.profile_id:
            raise HTTPException(status_code=400, detail="사주 프로필을 선택해 주세요")
        result_path = (
            f"/store/{body.product_id}/result?profile_id={body.profile_id}"
            + (f"&partner_id={body.partner_profile_id}" if body.partner_profile_id else "")
        )
        # free → grant immediately (long window)
        if amount == 0:
            row = await mon.grant_unlock(
                session,
                current_user.id,
                product_key,
                source="free",
                profile_id=body.profile_id,
                partner_profile_id=body.partner_profile_id,
            )
            return {
                "ok": True,
                "free": True,
                "order_id": None,
                "amount_krw": 0,
                "message": "무료 상품 · 바로 결과 확인",
                "result_path": result_path,
                "access": {
                    "web_expires_at": row.web_expires_at.isoformat() if row.web_expires_at else None,
                    "email_expires_at": row.email_expires_at.isoformat() if row.email_expires_at else None,
                    "email_token": row.email_token,
                    "web_view_days": mon.WEB_VIEW_DAYS,
                    "email_view_days": mon.EMAIL_VIEW_DAYS,
                },
            }

    elif body.kind == "wealth_year":
        year = 2026
        if body.product_id.startswith("wealth_"):
            try:
                year = int(body.product_id.split("_")[-1])
            except ValueError:
                year = 2026
        amount = mon.WEALTH_YEAR_PRICE_KRW
        product_name = f"{year} 부자되기 연간 해금"
        product_key = mon.wealth_product_key(year)
        result_path = "/me?tab=wealth"

    elif body.kind == "beads_pack":
        pack = mon.BEAD_PACKS.get(body.product_id)
        if not pack:
            raise HTTPException(status_code=400, detail="알 수 없는 구슬 팩")
        amount = int(pack["price_krw"])
        product_name = pack.get("label") or body.product_id
        product_key = f"beads:{body.product_id}"
        result_path = "/shop"

    order_id = _new_order_id()
    provider = get_payment_provider()
    fe = settings.FRONTEND_URL.rstrip("/")
    success_url = f"{fe}/payments/success?orderId={order_id}"
    fail_url = f"{fe}/payments/fail?orderId={order_id}"
    customer_key = f"user_{current_user.id}"

    try:
        created = provider.create_payment(
            order_id=order_id,
            amount_krw=amount,
            order_name=product_name[:100],
            customer_key=customer_key,
            success_url=success_url,
            fail_url=fail_url,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    row = PaymentOrder(
        order_id=order_id,
        user_id=current_user.id,
        kind=body.kind,
        product_key=product_key,
        product_name=product_name,
        amount_krw=amount,
        status="ready",
        provider=created.provider,
        profile_id=body.profile_id,
        partner_profile_id=body.partner_profile_id,
        buyer_name=body.buyer_name or "",
        buyer_email=body.email or current_user.email,
        buyer_phone=body.phone or "",
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)

    return {
        "ok": True,
        "free": False,
        "order_id": order_id,
        "amount_krw": amount,
        "product_name": product_name,
        "provider": created.provider,
        "client_key": created.client_key,
        "customer_key": created.customer_key,
        "success_url": created.success_url,
        "fail_url": created.fail_url,
        "mock_auto_confirm": created.mock_auto_confirm,
        "result_path": result_path,
        "extra": created.extra,
        "message": (
            "Mock: confirm with payment_key=mock_" + order_id
            if created.provider == "mock"
            else "Toss: open widget then confirm on success page"
        ),
    }


class ConfirmBody(BaseModel):
    payment_key: str
    order_id: str
    amount: int


@router.post("/confirm")
async def confirm_payment(
    body: ConfirmBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(PaymentOrder).where(PaymentOrder.order_id == body.order_id)
    )
    order = result.first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    if order.status == "paid":
        return {
            "ok": True,
            "already": True,
            "order_id": order.order_id,
            "status": order.status,
            "result_path": _result_path(order),
        }
    if order.amount_krw != body.amount:
        raise HTTPException(status_code=400, detail="결제 금액이 주문과 다릅니다")

    provider = get_payment_provider()
    # mock payment_key convenience
    pk = body.payment_key
    if order.provider == "mock" and not pk.startswith("mock_"):
        pk = f"mock_{order.order_id}"

    conf = provider.confirm_payment(
        payment_key=pk,
        order_id=order.order_id,
        amount_krw=order.amount_krw,
    )
    if not conf.ok:
        order.status = "failed"
        order.fail_reason = conf.error or "confirm failed"
        order.updated_at = datetime.utcnow()
        session.add(order)
        await session.commit()
        raise HTTPException(status_code=400, detail=order.fail_reason)

    order.status = "paid"
    order.payment_key = conf.payment_key
    order.method = conf.method
    order.paid_at = datetime.utcnow()
    order.updated_at = datetime.utcnow()
    order.raw_confirm = json.dumps(conf.raw, ensure_ascii=False)[:4000]
    session.add(order)
    await session.commit()

    fulfilled = await fulfill_order(session, order)

    return {
        "ok": True,
        "order_id": order.order_id,
        "status": "paid",
        "provider": order.provider,
        "amount_krw": order.amount_krw,
        "fulfilled": fulfilled,
        "result_path": _result_path(order),
        "message": "결제 확인 완료",
    }


def _result_path(order: PaymentOrder) -> str:
    if order.kind == "store_product":
        pid = order.product_key.replace("product:", "")
        q = f"profile_id={order.profile_id or 0}"
        if order.partner_profile_id:
            q += f"&partner_id={order.partner_profile_id}"
        return f"/store/{pid}/result?{q}"
    if order.kind == "wealth_year":
        return "/me?tab=wealth"
    if order.kind == "beads_pack":
        return "/shop"
    return "/hub"


@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(PaymentOrder).where(PaymentOrder.order_id == order_id)
    )
    order = result.first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="주문 없음")
    return {
        "order_id": order.order_id,
        "status": order.status,
        "amount_krw": order.amount_krw,
        "product_name": order.product_name,
        "kind": order.kind,
        "provider": order.provider,
        "result_path": _result_path(order),
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
    }


@router.post("/webhook")
async def payment_webhook(request: Request):
    """
    Toss webhook receiver (template).
    Configure URL in Toss dashboard when going live.
    For now: accept JSON and return 200 (idempotent logging only).
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": (await request.body()).decode("utf-8", errors="ignore")[:2000]}
    # Future: verify signature, update order by orderId/paymentKey
    return {
        "ok": True,
        "received": True,
        "event": payload.get("eventType") or payload.get("type") or "unknown",
        "note": "Webhook template — wire order status updates when live",
    }


@router.post("/mock/pay")
async def mock_one_click_pay(
    body: ConfirmBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Dev helper: confirm mock order in one call (payment_key optional)."""
    if (settings.PAYMENT_PROVIDER or "mock").lower() not in ("mock",):
        # still allow if order is mock provider
        pass
    body.payment_key = body.payment_key or f"mock_{body.order_id}"
    return await confirm_payment(body, current_user, session)
