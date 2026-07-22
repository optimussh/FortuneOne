"""E2E: login → order → mock confirm → store result."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

API = "http://127.0.0.1:8000"


def req(method: str, path: str, data=None, token=None, form=False):
    headers = {}
    body = None
    if form:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urllib.parse.urlencode(data or {}).encode()
    elif data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(API + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as res:
            raw = res.read().decode()
            return res.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:800]


def main():
    st, cfg = req("GET", "/api/payments/config")
    print("1) payments/config", st, cfg.get("provider") if isinstance(cfg, dict) else cfg)
    if st != 200:
        print("FAIL: API missing payments routes — restart uvicorn with latest code")
        return

    st, login = req(
        "POST",
        "/api/auth/login",
        {"username": "admin@fortuneone.local", "password": "admin1234"},
        form=True,
    )
    if st != 200:
        print("login fail", st, login)
        return
    tok = login["access_token"]
    print("2) login ok")

    st, profiles = req("GET", "/api/profiles", token=tok)
    if st != 200:
        print("profiles fail", st, profiles)
        return
    if not profiles:
        st, _ = req(
            "POST",
            "/api/profiles",
            {
                "label": "본인",
                "display_name": "관리자",
                "solar_date": "1990-08-27",
                "hour": 8,
                "minute": 0,
                "time_unknown": False,
                "time_slot": "chen",
                "gender": "male",
                "calendar_type": "solar",
                "is_self": True,
            },
            token=tok,
        )
        print("create profile", st)
        st, profiles = req("GET", "/api/profiles", token=tok)
    pid = profiles[0]["id"]
    print("3) profile_id", pid)

    st, plist = req("GET", "/api/store/products")
    prod = plist["products"][0]
    print("4) product", prod["id"], prod["title"][:40], prod["price_krw"])

    st, order = req(
        "POST",
        "/api/payments/orders",
        {
            "kind": "store_product",
            "product_id": prod["id"],
            "profile_id": pid,
            "agree_privacy": True,
            "agree_age14": True,
            "buyer_name": "admin",
            "email": "admin@fortuneone.local",
        },
        token=tok,
    )
    print("5) order", st)
    if st != 200:
        print(order)
        return
    print("   ", {k: order.get(k) for k in ("ok", "order_id", "amount_krw", "provider", "result_path", "free")})

    if order.get("free"):
        path = order["result_path"]
    else:
        oid = order["order_id"]
        st, conf = req(
            "POST",
            "/api/payments/confirm",
            {
                "payment_key": f"mock_{oid}",
                "order_id": oid,
                "amount": order["amount_krw"],
            },
            token=tok,
        )
        print("6) confirm", st)
        if st != 200:
            print(conf)
            return
        print("   ", {k: conf.get(k) for k in ("ok", "status", "result_path")})
        path = conf.get("result_path")

    st, result = req(
        "GET",
        f"/api/store/products/{prod['id']}/result?profile_id={pid}",
        token=tok,
    )
    print("7) result", st)
    if st == 200:
        print("   sections", len(result["report"]["sections"]))
        print("   title", result["report"]["product"]["title"][:50])
        print("   access", result.get("access", {}).get("policy"))
        print("   intro[:100]", result["report"]["intro"][:100])
        print("OK — open in browser:")
        print("  http://localhost:6100" + (path or f"/store/{prod['id']}/result?profile_id={pid}"))
    else:
        print(result)


if __name__ == "__main__":
    main()
