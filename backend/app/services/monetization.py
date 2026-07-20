"""
Hybrid monetization (local mock payments).

Free: hub daily + wealth overview teaser + month grade chips + 7 calendar days
Paid one-shot: full wealth year unlock
Beads: tarot extra, ask (after free 1/day), other-profile deep unlock (year)
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from typing import Any

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.monetization import BeadLedger, ContentUnlock, DailyFreeUse, UserWallet

# ── Catalog ──────────────────────────────────────────────────────────────

STARTER_BEADS = 15

BEAD_PACKS: dict[str, dict[str, Any]] = {
    "pack_100": {
        "id": "pack_100",
        "count": 100,
        "bonus_pct": 0,
        "bonus_count": 0,
        "total_beads": 100,
        "price_krw": 10000,
        "label": "구슬 100개",
    },
    "pack_200": {
        "id": "pack_200",
        "count": 200,
        "bonus_pct": 10,
        "bonus_count": 20,
        "total_beads": 220,
        "price_krw": 20000,
        "label": "구슬 200개 +10% 보너스",
    },
    "pack_500": {
        "id": "pack_500",
        "count": 500,
        "bonus_pct": 15,
        "bonus_count": 75,
        "total_beads": 575,
        "price_krw": 50000,
        "label": "구슬 500개 +15% 보너스",
    },
}

WEALTH_YEAR_PRICE_KRW = 3900

COSTS = {
    "tarot_extra": 3,
    "ask": 2,
    "profile_deep": 5,  # unlock wealth for other person's profile (same year)
    "month_unlock": 5,  # optional future
    "day_long": 1,
    "pdf_export": 10,
}

FREE_ASK_PER_DAY = 1
FREE_CALENDAR_DAYS = 7
OVERVIEW_TEASER_CHARS = 320


def wealth_product_key(year: int) -> str:
    return f"wealth_{year}"


def profile_deep_key(year: int, profile_id: int) -> str:
    return f"wealth_{year}_profile_{profile_id}"


def catalog() -> dict[str, Any]:
    return {
        "enabled": True,
        "mode": "hybrid",
        "message": (
            "무료로 미리보기를 충분히 본 뒤, 필요할 때 단건 해금 또는 구슬로 이용하세요. "
            "로컬 MVP는 결제 없이 ‘모의 구매’로 충전·해금됩니다."
        ),
        "disclaimer": (
            "점수·등급은 참고 지표이며 투자·재테크 권유가 아닙니다. "
            "중요한 금전 결정은 전문가 상담을 권합니다."
        ),
        "starter_beads": STARTER_BEADS,
        "bead_unit_price_krw": 100,
        "packs": list(BEAD_PACKS.values()),
        "wealth_year": {
            "price_krw": WEALTH_YEAR_PRICE_KRW,
            "label": "부자되기 연간 전체 해금",
            "covers": "해당 연도 총론 전문·월별 본문·365일·장문·export",
        },
        "costs": COSTS,
        "free": {
            "hub_daily": True,
            "wealth_overview_teaser": True,
            "month_grade_chips": True,
            "calendar_days": FREE_CALENDAR_DAYS,
            "ask_per_day": FREE_ASK_PER_DAY,
            "tarot_daily_one": True,
        },
    }


async def get_or_create_wallet(session: AsyncSession, user_id: int) -> UserWallet:
    result = await session.exec(select(UserWallet).where(UserWallet.user_id == user_id))
    wallet = result.first()
    if wallet:
        return wallet
    wallet = UserWallet(user_id=user_id, beads=STARTER_BEADS)
    session.add(wallet)
    session.add(
        BeadLedger(
            user_id=user_id,
            delta=STARTER_BEADS,
            balance_after=STARTER_BEADS,
            reason="starter_grant",
            meta="welcome",
        )
    )
    await session.commit()
    await session.refresh(wallet)
    return wallet


async def has_unlock(session: AsyncSession, user_id: int, product_key: str) -> bool:
    result = await session.exec(
        select(ContentUnlock).where(
            ContentUnlock.user_id == user_id,
            ContentUnlock.product_key == product_key,
        )
    )
    return result.first() is not None


async def grant_unlock(
    session: AsyncSession,
    user_id: int,
    product_key: str,
    source: str = "purchase",
) -> ContentUnlock:
    existing = await session.exec(
        select(ContentUnlock).where(
            ContentUnlock.user_id == user_id,
            ContentUnlock.product_key == product_key,
        )
    )
    row = existing.first()
    if row:
        return row
    row = ContentUnlock(user_id=user_id, product_key=product_key, source=source)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def add_beads(
    session: AsyncSession,
    user_id: int,
    amount: int,
    reason: str,
    meta: str = "",
) -> UserWallet:
    wallet = await get_or_create_wallet(session, user_id)
    wallet.beads = int(wallet.beads) + amount
    wallet.updated_at = datetime.utcnow()
    session.add(wallet)
    session.add(
        BeadLedger(
            user_id=user_id,
            delta=amount,
            balance_after=wallet.beads,
            reason=reason,
            meta=meta[:255],
        )
    )
    await session.commit()
    await session.refresh(wallet)
    return wallet


async def spend_beads(
    session: AsyncSession,
    user_id: int,
    amount: int,
    reason: str,
    meta: str = "",
) -> UserWallet:
    if amount <= 0:
        return await get_or_create_wallet(session, user_id)
    wallet = await get_or_create_wallet(session, user_id)
    if wallet.beads < amount:
        raise ValueError(f"구슬이 부족합니다. 필요 {amount}개 · 보유 {wallet.beads}개")
    wallet.beads -= amount
    wallet.updated_at = datetime.utcnow()
    session.add(wallet)
    session.add(
        BeadLedger(
            user_id=user_id,
            delta=-amount,
            balance_after=wallet.beads,
            reason=reason,
            meta=meta[:255],
        )
    )
    await session.commit()
    await session.refresh(wallet)
    return wallet


async def get_daily_free_count(
    session: AsyncSession, user_id: int, kind: str, day: date
) -> int:
    key = day.isoformat()
    result = await session.exec(
        select(DailyFreeUse).where(
            DailyFreeUse.user_id == user_id,
            DailyFreeUse.use_date == key,
            DailyFreeUse.kind == kind,
        )
    )
    row = result.first()
    return int(row.count) if row else 0


async def bump_daily_free(
    session: AsyncSession, user_id: int, kind: str, day: date
) -> int:
    key = day.isoformat()
    result = await session.exec(
        select(DailyFreeUse).where(
            DailyFreeUse.user_id == user_id,
            DailyFreeUse.use_date == key,
            DailyFreeUse.kind == kind,
        )
    )
    row = result.first()
    if not row:
        row = DailyFreeUse(user_id=user_id, use_date=key, kind=kind, count=1)
    else:
        row.count = int(row.count) + 1
    session.add(row)
    await session.commit()
    return int(row.count)


def _teaser(text: str, n: int = OVERVIEW_TEASER_CHARS) -> str:
    t = (text or "").strip()
    if len(t) <= n:
        return t
    return t[:n].rstrip() + "…\n\n【미리보기】 이어서 보려면 부자되기 연간 해금이 필요합니다."


def apply_wealth_access(
    wealth: dict[str, Any],
    *,
    unlocked: bool,
    as_of: date | None = None,
    profile_is_self: bool = True,
    profile_unlocked: bool = False,
) -> dict[str, Any]:
    """Mutate a copy of wealth_year for free tier vs full unlock."""
    data = deepcopy(wealth)
    year = int(data.get("year") or 2026)
    today = as_of or date.today()
    # other profile needs either global year unlock or profile-deep unlock
    full = unlocked or (not profile_is_self and profile_unlocked) or (
        profile_is_self and unlocked
    )
    if profile_is_self:
        full = unlocked
    else:
        full = unlocked or profile_unlocked

    cat = catalog()
    data["monetization"] = {
        **cat,
        "enabled": True,
        "product_key": wealth_product_key(year),
        "unlocked": full,
        "profile_is_self": profile_is_self,
        "price_krw": WEALTH_YEAR_PRICE_KRW,
        "costs": COSTS,
    }

    if full:
        data["access"] = {
            "unlocked": True,
            "tier": "full",
            "message": "전체 해금됨 · 점수·등급은 참고 지표입니다 (투자 권유 아님).",
        }
        # reinforce disclaimer
        note = data.get("calendar", {}).get("note", "")
        if "참고 지표" not in note:
            data.setdefault("calendar", {})["note"] = (
                note + " 점수·등급은 참고 지표이며 투자 권유가 아닙니다."
            ).strip()
        return data

    # ── Free preview ────────────────────────────────────────────────────
    data["access"] = {
        "unlocked": False,
        "tier": "preview",
        "message": (
            f"무료 미리보기: 총론 일부 · 월 등급 · {FREE_CALENDAR_DAYS}일 캘린더. "
            f"전체(월 본문·365일·장문·저장)는 {WEALTH_YEAR_PRICE_KRW:,}원 단건 해금 "
            f"(로컬은 모의 구매)."
        ),
        "price_krw": WEALTH_YEAR_PRICE_KRW,
        "free_calendar_days": FREE_CALENDAR_DAYS,
    }

    if "overview" in data and data["overview"].get("body"):
        data["overview"] = {
            **data["overview"],
            "body": _teaser(data["overview"]["body"]),
            "locked": True,
        }
    if "year_money" in data and data["year_money"].get("body"):
        data["year_money"] = {
            **data["year_money"],
            "body": _teaser(data["year_money"]["body"], 220),
            "locked": True,
        }

    mg = data.get("month_guide") or {}
    months = []
    for m in mg.get("months") or []:
        months.append(
            {
                **m,
                "body": "【잠김】 월별 상세 활용법은 연간 해금 후 확인할 수 있습니다.",
                "locked": True,
                "body_preview": False,
            }
        )
    if mg:
        data["month_guide"] = {
            **mg,
            "intro": _teaser(mg.get("intro") or "", 180),
            "months": months,
        }

    cal = data.get("calendar") or {}
    free_months = []
    focus_month = today.month if today.year == year else 1
    for cm in cal.get("months") or []:
        if cm.get("month") != focus_month:
            # keep month shell without days for chip UI navigation lock
            free_months.append(
                {
                    **cm,
                    "days": [],
                    "locked": True,
                    "lock_reason": "미리보기에서는 이번 달만 일부 공개됩니다.",
                }
            )
            continue
        days_all = cm.get("days") or []
        # free: from today for 7 days within month, else first 7 days
        free_days = []
        if today.year == year and today.month == focus_month:
            start = today.day
            end = min(start + FREE_CALENDAR_DAYS - 1, len(days_all))
            for d in days_all:
                if start <= d.get("day", 0) <= end:
                    dd = {**d, "body_long": None, "long_locked": True}
                    free_days.append(dd)
        else:
            for d in days_all[:FREE_CALENDAR_DAYS]:
                free_days.append({**d, "body_long": None, "long_locked": True})
        free_months.append(
            {
                **cm,
                "days": free_days,
                "locked": False,
                "preview": True,
                "preview_note": f"무료 {len(free_days)}일 · 장문·나머지 날짜는 해금 후",
            }
        )
    data["calendar"] = {
        **cal,
        "months": free_months,
        "note": (
            "날짜는 양력 기준입니다. 점수·등급은 참고 지표이며 투자 권유가 아닙니다. "
            f"(무료 미리보기: 최대 {FREE_CALENDAR_DAYS}일)"
        ),
    }

    # export locked
    data["export"] = {
        **(data.get("export") or {}),
        "body": "",
        "locked": True,
        "message": "TXT/인쇄는 연간 해금 후 이용할 수 있습니다.",
    }
    data["subtitle"] = (data.get("subtitle") or "") + " · 무료 미리보기"
    return data


async def resolve_wealth_for_user(
    session: AsyncSession,
    user_id: int | None,
    wealth: dict[str, Any],
    *,
    profile_id: int | None = None,
    profile_is_self: bool = True,
    as_of: date | None = None,
) -> dict[str, Any]:
    year = int(wealth.get("year") or 2026)
    if user_id is None:
        return apply_wealth_access(
            wealth, unlocked=False, as_of=as_of, profile_is_self=True
        )
    unlocked = await has_unlock(session, user_id, wealth_product_key(year))
    profile_unlocked = False
    if profile_id is not None and not profile_is_self:
        profile_unlocked = await has_unlock(
            session, user_id, profile_deep_key(year, profile_id)
        )
    return apply_wealth_access(
        wealth,
        unlocked=unlocked,
        as_of=as_of,
        profile_is_self=profile_is_self,
        profile_unlocked=profile_unlocked,
    )
