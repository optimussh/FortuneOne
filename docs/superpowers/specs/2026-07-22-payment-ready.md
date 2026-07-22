# Payment module (mock + Toss ready)

**Status:** Implemented template  
**Goal:** Test full flow now; flip to Toss live when keys ready.

## Modes

| `PAYMENT_PROVIDER` | Keys | Behavior |
|--------------------|------|----------|
| `mock` (default) | none | Full order → success → confirm → unlock |
| `toss` | missing | Falls back to mock |
| `toss` | `test_ck_` / `test_sk_` | Toss sandbox widget |
| `toss` | `live_ck_` / `live_sk_` + `PAYMENT_TEST_MODE=false` | Live |

## API

- `GET /api/payments/config` — public (no secrets)
- `POST /api/payments/orders` — create order
- `POST /api/payments/confirm` — confirm (Toss or mock)
- `GET /api/payments/orders/{id}`
- `POST /api/payments/webhook` — template receiver

## Frontend

- `/store/[id]/checkout` — creates order; mock auto or Toss SDK
- `/payments/success` — confirm + redirect to result
- `/payments/fail`
- `/policy/refund`, `/policy/business` — legal templates

## Env (backend `.env`)

```env
PAYMENT_PROVIDER=mock
PAYMENT_TEST_MODE=true
TOSS_CLIENT_KEY=
TOSS_SECRET_KEY=
FRONTEND_URL=http://localhost:6100
BUSINESS_NAME=FortuneOne
BUSINESS_CEO=
BUSINESS_NUMBER=
BUSINESS_MAIL_ORDER=
BUSINESS_ADDRESS=
BUSINESS_PHONE=
BUSINESS_EMAIL=
```

## Go-live checklist

1. Fill business disclosure + terms/refund
2. Deploy HTTPS site
3. Toss 가맹 심사 + test keys smoke
4. Set live keys, `PAYMENT_PROVIDER=toss`, `PAYMENT_TEST_MODE=false`
5. Webhook URL → `https://api.../api/payments/webhook`
