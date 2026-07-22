"""After paid: grant unlocks (store product, wealth, beads)."""

from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.payment import PaymentOrder
from app.services import monetization as mon
from app.services.product_catalog import product_unlock_key


async def fulfill_order(session: AsyncSession, order: PaymentOrder) -> dict:
    kind = order.kind
    meta = {"order_id": order.order_id, "amount": order.amount_krw}

    if kind == "store_product":
        # product_key like "product:p123" or raw product id
        pk = order.product_key
        if not pk.startswith("product:"):
            pk = product_unlock_key(pk.replace("product:", ""))
        row = await mon.grant_unlock(
            session,
            order.user_id,
            pk,
            source=f"pay_{order.provider}",
            profile_id=order.profile_id,
            partner_profile_id=order.partner_profile_id,
            renew=True,
        )
        return {
            "unlock": pk,
            "web_expires_at": row.web_expires_at.isoformat() if row.web_expires_at else None,
            "email_expires_at": row.email_expires_at.isoformat() if row.email_expires_at else None,
            "email_token": row.email_token,
            "web_view_days": mon.WEB_VIEW_DAYS,
            "email_view_days": mon.EMAIL_VIEW_DAYS,
            **meta,
        }

    if kind == "wealth_year":
        year = 2026
        if "wealth_" in order.product_key:
            try:
                year = int(order.product_key.split("_")[-1])
            except ValueError:
                year = 2026
        key = mon.wealth_product_key(year)
        row = await mon.grant_unlock(
            session, order.user_id, key, source=f"pay_{order.provider}", renew=True
        )
        return {
            "unlock": key,
            "web_expires_at": row.web_expires_at.isoformat() if row.web_expires_at else None,
            "email_expires_at": row.email_expires_at.isoformat() if row.email_expires_at else None,
            "email_token": row.email_token,
            **meta,
        }

    if kind == "beads_pack":
        from app.services.monetization import BEAD_PACKS

        pack_id = order.product_key.replace("beads:", "")
        pack = BEAD_PACKS.get(pack_id)
        if not pack:
            return {"error": "unknown pack", **meta}
        wallet = await mon.add_beads(
            session,
            order.user_id,
            int(pack["total_beads"]),
            reason="purchase_pack",
            meta=order.order_id,
        )
        return {"beads": wallet.beads, "added": pack["total_beads"], **meta}

    return {"skipped": True, **meta}
