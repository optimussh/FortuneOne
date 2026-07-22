"""Product store — catalog, mock checkout, saju-based results."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.api.deps import get_current_user, get_optional_user
from app.core.database import get_session
from app.models.fortune_profile import FortuneProfile
from app.models.user import User
from app.services import monetization as mon
from app.services.product_catalog import (
    get_product,
    list_products,
    load_catalog,
    product_unlock_key,
)
from app.services.product_report import build_product_report
from app.services.saju_engine import SajuEngine

router = APIRouter()
_engine = SajuEngine()


@router.get("/menu")
async def store_menu():
    cat = load_catalog()
    return {
        "menu": cat.get("menu") or [],
        "categories": cat.get("categories") or [],
        "payment_module": cat.get("payment_module") or {},
        "engine_plan": cat.get("engine_plan") or {},
        "role_guide": cat.get("role_guide"),
        "content_quality": cat.get("content_quality"),
    }


@router.get("/products")
async def store_products(category: Optional[str] = None):
    items = list_products(category)
    # public list without source_title
    public = []
    for p in items:
        public.append(_public_product(p))
    cat = load_catalog()
    return {
        "count": len(public),
        "products": public,
        "role_guide": cat.get("role_guide"),
        "category_counts": (cat.get("content_quality") or {}).get("category_counts"),
    }


def _public_product(p: dict) -> dict:
    return {
        "id": p["id"],
        "title": p["title"],
        "subtitle": p.get("subtitle"),
        "price_krw": p["price_krw"],
        "category_id": p["category_id"],
        "category_label": p["category_label"],
        "needs_profile": p.get("needs_profile", True),
        "needs_partner": p.get("needs_partner", False),
        "is_free": p.get("is_free", False),
        "preview_sections": p.get("preview_sections") or [],
        "result_sections": p.get("result_sections") or [],
        "intro_blurbs": p.get("intro_blurbs") or [],
        "for_whom": p.get("for_whom") or [],
        "diff_from_free_tabs": p.get("diff_from_free_tabs"),
        "tone": p.get("tone"),
        "copy_version": p.get("copy_version"),
    }


@router.get("/products/{product_id}")
async def store_product_detail(
    product_id: str,
    user: Optional[User] = Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
):
    p = get_product(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
    unlocked = False
    if user:
        unlocked = await mon.has_unlock(session, user.id, product_unlock_key(product_id))
        if p.get("is_free"):
            unlocked = True
    pub = _public_product(p)
    pub["payment"] = p.get("payment") or load_catalog().get("payment_module")
    if not pub.get("intro_blurbs"):
        pub["intro_blurbs"] = [
            f"「{p['title']}」는 회원님 사주 원국을 바탕으로 한 주제 심화 리포트입니다.",
            "상세 사주 탭(오늘·신년·토정·부자되기)은 기본 제공이고, 스토어는 한 주제를 깊게 파는 패키지입니다.",
            "결제 후 내 프로필로 결과가 생성되며, 웹 7일·메일 링크 30일 다시보기할 수 있습니다.",
        ]
    return {
        "product": pub,
        "unlocked": unlocked,
        "payment_module": load_catalog().get("payment_module") or {},
        "role_guide": load_catalog().get("role_guide"),
    }


class CheckoutBody(BaseModel):
    product_id: str
    profile_id: int
    partner_profile_id: Optional[int] = None
    buyer_name: str = ""
    email: str = ""
    phone: str = ""
    method: str = "mock_card"
    agree_privacy: bool = False
    agree_age14: bool = False


@router.post("/checkout")
async def store_checkout(
    body: CheckoutBody,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    p = get_product(body.product_id)
    if not p:
        raise HTTPException(status_code=404, detail="상품 없음")
    if not body.agree_privacy or not body.agree_age14:
        raise HTTPException(status_code=400, detail="필수 약관에 동의해 주세요")

    profile = await session.get(FortuneProfile, body.profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="사주 프로필을 선택해 주세요")

    if p.get("needs_partner") and body.partner_profile_id:
        partner = await session.get(FortuneProfile, body.partner_profile_id)
        if not partner or partner.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="상대 프로필을 확인하세요")

    key = product_unlock_key(body.product_id)
    already = await mon.has_unlock(session, current_user.id, key)
    if not already and not p.get("is_free"):
        await mon.grant_unlock(
            session, current_user.id, key, source=f"mock_{body.method}"
        )
    elif p.get("is_free") and not already:
        await mon.grant_unlock(session, current_user.id, key, source="free")

    return {
        "ok": True,
        "mock": True,
        "product_id": body.product_id,
        "price_krw": 0 if p.get("is_free") else p.get("price_krw"),
        "unlock_key": key,
        "message": (
            "모의 결제 완료 · 결과를 확인할 수 있습니다"
            if not p.get("is_free")
            else "무료 상품 · 결과를 확인할 수 있습니다"
        ),
        "result_path": f"/store/{body.product_id}/result?profile_id={body.profile_id}"
        + (
            f"&partner_id={body.partner_profile_id}"
            if body.partner_profile_id
            else ""
        ),
    }


def _calc_profile(profile: FortuneProfile):
    hour = profile.hour if profile.hour is not None else 12
    minute = profile.minute if profile.minute is not None else 0
    if profile.time_unknown:
        hour, minute = 12, 0
    return _engine.calculate(
        solar_date=profile.solar_date,
        hour=hour,
        minute=minute,
        gender=profile.gender,
        time_assumed=profile.time_unknown,
    )


@router.get("/products/{product_id}/result")
async def store_product_result(
    product_id: str,
    profile_id: Optional[int] = None,
    partner_id: Optional[int] = None,
    token: Optional[str] = None,
    current_user: User | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
):
    p = get_product(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="상품 없음")

    key = product_unlock_key(product_id)
    access_meta: dict = {}
    owner_id: int | None = None

    # Email magic link (30-day window)
    if token:
        row = await mon.get_unlock_by_email_token(session, token)
        if not row or row.product_key != key:
            raise HTTPException(status_code=404, detail="유효하지 않은 다시보기 링크입니다")
        access_meta = mon.unlock_access_info(row, channel="email")
        if not access_meta.get("ok"):
            raise HTTPException(status_code=402, detail=access_meta.get("message"))
        owner_id = row.user_id
        profile_id = profile_id or row.profile_id
        partner_id = partner_id or row.partner_profile_id
    elif p.get("is_free"):
        if not current_user:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")
        owner_id = current_user.id
        access_meta = {
            "ok": True,
            "channel": "web",
            "message": "무료 상품",
        }
    else:
        if not current_user:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")
        row = await mon.get_unlock_row(session, current_user.id, key)
        if not row:
            raise HTTPException(
                status_code=402,
                detail="결제가 필요합니다. 상품 페이지에서 결제 후 이용해 주세요.",
            )
        access_meta = mon.unlock_access_info(row, channel="web")
        if not access_meta.get("ok"):
            raise HTTPException(
                status_code=402,
                detail=access_meta.get("message")
                or "다시보기 기간이 만료되었습니다. 재구매해 주세요.",
            )
        owner_id = current_user.id
        if not profile_id and row.profile_id:
            profile_id = row.profile_id
        if partner_id is None and row.partner_profile_id:
            partner_id = row.partner_profile_id

    if not profile_id:
        raise HTTPException(status_code=400, detail="profile_id가 필요합니다")

    profile = await session.get(FortuneProfile, profile_id)
    if not profile or (owner_id is not None and profile.user_id != owner_id):
        raise HTTPException(status_code=404, detail="프로필 없음")

    eng = _calc_profile(profile)
    partner_eng = None
    partner_name = ""
    partner_birth = None
    if partner_id:
        pp = await session.get(FortuneProfile, partner_id)
        if pp and (owner_id is None or pp.user_id == owner_id):
            partner_eng = _calc_profile(pp)
            partner_name = getattr(pp, "display_name", "") or pp.label
            partner_birth = pp.solar_date

    report = build_product_report(
        p,
        eng,
        profile.solar_date,
        profile.gender,
        display_name=getattr(profile, "display_name", "") or profile.label,
        partner=partner_eng,
        partner_name=partner_name,
        partner_birth=partner_birth,
    )
    fe = __import__("app.core.config", fromlist=["settings"]).settings.FRONTEND_URL.rstrip("/")
    email_link = None
    if access_meta.get("email_token"):
        email_link = f"{fe}/store/{product_id}/result?token={access_meta['email_token']}"
    return {
        "unlocked": True,
        "profile_id": profile_id,
        "report": report,
        "access": {
            **access_meta,
            "web_view_days": mon.WEB_VIEW_DAYS,
            "email_view_days": mon.EMAIL_VIEW_DAYS,
            "email_result_link": email_link,
            "policy": f"웹 다시보기 {mon.WEB_VIEW_DAYS}일 · 이메일 링크 {mon.EMAIL_VIEW_DAYS}일",
        },
    }


@router.get("/my-unlocks")
async def my_product_unlocks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """구매·해금 목록 + 다시보기(웹 7일 / 메일 30일) 상태."""
    from app.models.monetization import ContentUnlock
    from app.core.config import settings

    result = await session.exec(
        select(ContentUnlock).where(ContentUnlock.user_id == current_user.id)
    )
    rows = list(result.all())
    fe = settings.FRONTEND_URL.rstrip("/")
    items = []
    for r in rows:
        access = mon.unlock_access_info(r, channel="web")
        email_access = mon.unlock_access_info(r, channel="email")
        pk = r.product_key
        kind = "other"
        title = pk
        result_path = "/hub"
        product_id = None
        if pk.startswith("product:"):
            kind = "store_product"
            product_id = pk.replace("product:", "", 1)
            p = get_product(product_id)
            title = (p or {}).get("title") or product_id
            q = []
            if r.profile_id:
                q.append(f"profile_id={r.profile_id}")
            if r.partner_profile_id:
                q.append(f"partner_id={r.partner_profile_id}")
            result_path = f"/store/{product_id}/result" + (
                ("?" + "&".join(q)) if q else ""
            )
        elif pk.startswith("wealth_"):
            kind = "wealth_year"
            title = f"{pk.replace('wealth_', '')} 부자되기 연간 해금"
            result_path = "/me?tab=wealth"
        elif pk.startswith("wealth_") is False and "profile_" in pk:
            kind = "profile_deep"
            title = "프로필 심화 해금"
        email_link = None
        if r.email_token and product_id:
            email_link = f"{fe}/store/{product_id}/result?token={r.email_token}"
            if r.profile_id:
                email_link += f"&profile_id={r.profile_id}"
        items.append(
            {
                "product_key": pk,
                "kind": kind,
                "title": title,
                "source": r.source,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "web_ok": access.get("ok"),
                "email_ok": email_access.get("ok"),
                "web_expires_at": access.get("web_expires_at"),
                "email_expires_at": access.get("email_expires_at"),
                "days_left_web": access.get("days_left_web"),
                "result_path": result_path,
                "email_result_link": email_link,
                "profile_id": r.profile_id,
                "policy": f"웹 {mon.WEB_VIEW_DAYS}일 · 이메일 링크 {mon.EMAIL_VIEW_DAYS}일",
            }
        )
    # newest first
    items.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return {
        "count": len(items),
        "policy": {
            "web_view_days": mon.WEB_VIEW_DAYS,
            "email_view_days": mon.EMAIL_VIEW_DAYS,
            "summary": (
                f"유료 결과 다시보기: 로그인 웹 {mon.WEB_VIEW_DAYS}일, "
                f"이메일 링크 {mon.EMAIL_VIEW_DAYS}일. 만료 후 재구매가 필요할 수 있습니다."
            ),
        },
        "items": items,
    }
