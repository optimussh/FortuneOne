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
        await mon.grant_unlock(session, order.user_id, pk, source=f"pay_{order.provider}")
        return {"unlock": pk, **meta}

    if kind == "wealth_year":
        year = 2026
        if "wealth_" in order.product_key:
            try:
                year = int(order.product_key.split("_")[-1])
            except ValueError:
                year = 2026
        key = mon.wealth_product_key(year)
        await mon.grant_unlock(session, order.user_id, key, source=f"pay_{order.provider}")
        return {"unlock": key, **meta}

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
