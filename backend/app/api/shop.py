"""Shop / wallet / unlocks — mock payments for local MVP."""

from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.user import User
from app.services import monetization as mon

router = APIRouter()


@router.get("/catalog")
async def get_catalog():
    return mon.catalog()


@router.get("/wallet")
async def get_wallet(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    wallet = await mon.get_or_create_wallet(session, current_user.id)
    year = date.today().year
    # show 2026 product status as primary for product
    y = 2026
    unlocked = await mon.has_unlock(session, current_user.id, mon.wealth_product_key(y))
    return {
        "beads": wallet.beads,
        "starter_beads": mon.STARTER_BEADS,
        "catalog": mon.catalog(),
        "unlocks": {
            mon.wealth_product_key(y): unlocked,
        },
        "costs": mon.COSTS,
        "mock_payment": True,
        "note": "로컬 MVP · 실제 결제 연동 전 모의 구매입니다.",
    }


class BuyPackBody(BaseModel):
    pack_id: str = Field(..., description="pack_100 | pack_200 | pack_500")


@router.post("/buy/beads")
async def buy_bead_pack(
    body: BuyPackBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    pack = mon.BEAD_PACKS.get(body.pack_id)
    if not pack:
        raise HTTPException(status_code=400, detail="알 수 없는 구슬 팩입니다")
    wallet = await mon.add_beads(
        session,
        current_user.id,
        int(pack["total_beads"]),
        reason="purchase_pack",
        meta=body.pack_id,
    )
    return {
        "ok": True,
        "mock": True,
        "pack": pack,
        "beads": wallet.beads,
        "message": f"모의 구매 완료 · 구슬 +{pack['total_beads']} (보유 {wallet.beads})",
    }


class UnlockWealthBody(BaseModel):
    year: int = 2026


@router.post("/buy/wealth-year")
async def buy_wealth_year(
    body: UnlockWealthBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    key = mon.wealth_product_key(body.year)
    if await mon.has_unlock(session, current_user.id, key):
        wallet = await mon.get_or_create_wallet(session, current_user.id)
        return {
            "ok": True,
            "already": True,
            "product_key": key,
            "beads": wallet.beads,
            "message": "이미 해금된 연간 부자되기입니다.",
        }
    await mon.grant_unlock(session, current_user.id, key, source="mock_purchase")
    wallet = await mon.get_or_create_wallet(session, current_user.id)
    return {
        "ok": True,
        "mock": True,
        "product_key": key,
        "price_krw": mon.WEALTH_YEAR_PRICE_KRW,
        "beads": wallet.beads,
        "message": f"{body.year} 부자되기 전체 해금 (모의 결제 {mon.WEALTH_YEAR_PRICE_KRW:,}원)",
    }


class SpendBody(BaseModel):
    action: Literal["tarot_extra", "ask", "profile_deep"]
    year: int = 2026
    profile_id: Optional[int] = None
    force_paid: bool = False  # skip free quota


@router.post("/spend")
async def spend_action(
    body: SpendBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    today = date.today()
    cost = mon.COSTS.get(body.action)
    if cost is None:
        raise HTTPException(status_code=400, detail="알 수 없는 액션")

    # free ask once per day
    if body.action == "ask" and not body.force_paid:
        used = await mon.get_daily_free_count(session, current_user.id, "ask", today)
        if used < mon.FREE_ASK_PER_DAY:
            await mon.bump_daily_free(session, current_user.id, "ask", today)
            wallet = await mon.get_or_create_wallet(session, current_user.id)
            return {
                "ok": True,
                "charged": 0,
                "free": True,
                "beads": wallet.beads,
                "message": "오늘 무료 질문 1회를 사용했습니다.",
            }

    if body.action == "profile_deep":
        if not body.profile_id:
            raise HTTPException(status_code=400, detail="profile_id 필요")
        key = mon.profile_deep_key(body.year, body.profile_id)
        if await mon.has_unlock(session, current_user.id, key):
            wallet = await mon.get_or_create_wallet(session, current_user.id)
            return {
                "ok": True,
                "already": True,
                "charged": 0,
                "beads": wallet.beads,
                "message": "이미 해금된 프로필입니다.",
            }
        try:
            wallet = await mon.spend_beads(
                session,
                current_user.id,
                cost,
                reason="profile_deep",
                meta=key,
            )
        except ValueError as exc:
            raise HTTPException(status_code=402, detail=str(exc)) from exc
        await mon.grant_unlock(session, current_user.id, key, source="beads")
        return {
            "ok": True,
            "charged": cost,
            "beads": wallet.beads,
            "product_key": key,
            "message": f"다른 사람 프로필 심화 해금 (-{cost} 구슬)",
        }

    try:
        wallet = await mon.spend_beads(
            session,
            current_user.id,
            cost,
            reason=body.action,
            meta="",
        )
    except ValueError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc

    return {
        "ok": True,
        "charged": cost,
        "free": False,
        "beads": wallet.beads,
        "message": f"{body.action} · 구슬 -{cost} (잔액 {wallet.beads})",
    }


@router.get("/access/wealth/{year}")
async def wealth_access(
    year: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    key = mon.wealth_product_key(year)
    unlocked = await mon.has_unlock(session, current_user.id, key)
    wallet = await mon.get_or_create_wallet(session, current_user.id)
    return {
        "year": year,
        "product_key": key,
        "unlocked": unlocked,
        "price_krw": mon.WEALTH_YEAR_PRICE_KRW,
        "beads": wallet.beads,
    }
