"""Smoke: register → mock pay → my-unlocks → result (web/email)."""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone

import httpx

BASE = "http://127.0.0.1:8000"


async def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    email = f"libtest_{stamp}@test.local"
    pw = "TestPass123!"
    errors: list[str] = []

    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as c:
        r = await c.get("/api/health")
        print("health", r.status_code)
        if r.status_code != 200:
            print("API down", r.text)
            return 1

        r = await c.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": pw,
                "password_confirm": pw,
                "saju": {
                    "display_name": "LibTester",
                    "label": "본인",
                    "birth_year": 1990,
                    "birth_month": 5,
                    "birth_day": 15,
                    "time_slot": "unknown",
                    "calendar_type": "solar",
                    "gender": "male",
                },
            },
        )
        print("register", r.status_code, r.text[:280])
        if r.status_code >= 400:
            r = await c.post(
                "/api/auth/login",
                data={"username": email, "password": pw},
            )
            print("login", r.status_code, r.text[:200])
            if r.status_code >= 400:
                print("FAIL auth")
                return 1
            token = r.json().get("access_token")
            pid = None
        else:
            data = r.json()
            token = data.get("access_token")
            pid = (data.get("profile") or {}).get("id")

        if not token:
            print("FAIL no token")
            return 1
        headers = {"Authorization": f"Bearer {token}"}

        r = await c.get("/api/store/my-unlocks", headers=headers)
        print("my-unlocks empty", r.status_code, r.text[:200])
        if r.status_code != 200:
            errors.append(f"my-unlocks empty {r.status_code}")

        if not pid:
            r = await c.get("/api/fortune/profiles", headers=headers)
            profiles = r.json() if r.status_code == 200 else []
            if isinstance(profiles, dict):
                profiles = profiles.get("items") or profiles.get("profiles") or []
            if not profiles:
                print("FAIL no profile", r.text[:200])
                return 1
            pid = profiles[0]["id"]
        pid = int(pid)
        print("pid", pid)

        r = await c.get("/api/store/products")
        prods = r.json()
        items = (
            prods
            if isinstance(prods, list)
            else prods.get("items") or prods.get("products") or []
        )
        paid = next(
            (
                p
                for p in items
                if isinstance(p, dict)
                and not p.get("is_free")
                and (p.get("price_krw") or 0) > 0
            ),
            None,
        )
        if not paid:
            print("FAIL no paid product")
            return 1
        print("product", paid.get("id"), str(paid.get("title", ""))[:40], paid.get("price_krw"))

        r = await c.post(
            "/api/payments/orders",
            headers=headers,
            json={
                "kind": "store_product",
                "product_id": paid["id"],
                "profile_id": pid,
                "agree_privacy": True,
                "agree_age14": True,
            },
        )
        print("order", r.status_code, r.text[:400])
        if r.status_code >= 400:
            errors.append(f"order {r.status_code}")
            print("ERRORS", errors)
            return 1
        od = r.json()
        order_id = od.get("order_id")
        amount = od.get("amount_krw") or paid.get("price_krw")
        r = await c.post(
            "/api/payments/confirm",
            headers=headers,
            json={
                "payment_key": f"mock_{order_id}",
                "order_id": order_id,
                "amount": amount,
            },
        )
        print("confirm", r.status_code, r.text[:500])
        if r.status_code >= 400:
            errors.append(f"confirm {r.status_code}")

        r = await c.get("/api/store/my-unlocks", headers=headers)
        print("my-unlocks after", r.status_code, r.text[:700])
        if r.status_code != 200:
            errors.append(f"my-unlocks after {r.status_code}")
        else:
            unlocks = r.json().get("items") or []
            if not unlocks:
                errors.append("unlocks empty after pay")
            else:
                it = unlocks[0]
                print(
                    "item title=",
                    it.get("title"),
                    "web_ok=",
                    it.get("web_ok"),
                    "path=",
                    it.get("result_path"),
                    "email_ok=",
                    it.get("email_ok"),
                )
                if not it.get("web_ok"):
                    errors.append("web_ok false")
                if not it.get("result_path"):
                    errors.append("no result_path")
                if not it.get("email_result_link") and not it.get("email_ok"):
                    errors.append("email link missing")

        rid = paid["id"]
        r = await c.get(
            f"/api/store/products/{rid}/result",
            headers=headers,
            params={"profile_id": pid},
        )
        print("result web", r.status_code)
        if r.status_code != 200:
            errors.append(f"result web {r.status_code}: {r.text[:150]}")
            print(r.text[:200])
        else:
            print("  sections", len((r.json().get("report") or {}).get("sections") or []))

        r = await c.get(f"/api/store/products/{rid}/result", headers=headers)
        print("result no profile_id", r.status_code)
        if r.status_code != 200:
            errors.append(f"result no profile {r.status_code}: {r.text[:150]}")
            print(r.text[:200])

        tok = None
        if r.status_code == 200:
            acc = r.json().get("access") or {}
            tok = acc.get("email_token")
            print("email_token", bool(tok), "link", str(acc.get("email_result_link") or "")[:90])
        if tok:
            r = await c.get(
                f"/api/store/products/{rid}/result",
                params={"token": tok},
            )
            print("result email token (no auth)", r.status_code)
            if r.status_code != 200:
                errors.append(f"email token {r.status_code}: {r.text[:150]}")
        else:
            errors.append("no email_token on access")

        # frontend pages
        fe = "http://localhost:6100"
        for path in ("/library", "/me", "/store"):
            try:
                fr = await c.get(f"{fe}{path}", follow_redirects=True)
                print(f"fe {path}", fr.status_code)
                if fr.status_code >= 500:
                    errors.append(f"fe {path} {fr.status_code}")
            except Exception as exc:
                print(f"fe {path} ERR", exc)
                errors.append(f"fe {path} {exc}")

    if errors:
        print("ERRORS:", errors)
        return 1
    print("ALL SMOKE OK")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
