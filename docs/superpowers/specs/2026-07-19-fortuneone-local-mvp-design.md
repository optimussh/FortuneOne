# FortuneOne Local MVP Design

**Date:** 2026-07-19  
**Product:** FortuneOne (운세 플랫폼)  
**Repo:** https://github.com/optimussh/FortuneOne  
**Base:** saas-template (Next.js 15 + FastAPI + Postgres + Docker)  
**Process rules:** `claude_Template-main` (guidelines, git, testing)

---

## 1. Goal

로컬에서 끝까지 검증 가능한 최소 제품:

1. **게스트**: 생년월일시 입력 → 사주 원국 + 오늘의 운세 (인증 없음)
2. **회원**: 이메일 가입/로그인 → 사주 프로필 저장 → 재조회
3. `docker compose` 또는 로컬 2프로세스로 재현
4. 작업 단위마다 FortuneOne에 커밋·푸시

**명시적 비범위 (이번 MVP):**  
쿠팡/알리 제휴, RAG/LLM, 소셜 로그인, PG 결제, PWA, 네이티브 앱, 푸시, Redis, Pinecone, 타로, B2B API 과금

위 항목은 **폴더/스키마/주석으로 자리만 남기지 않음**. 확장 시 별도 스펙. 다만 API 계약·모듈 경계는 이후 기능을 방해하지 않게 잡는다.

---

## 2. Decisions (locked)

| 항목 | 결정 |
|------|------|
| 기존 강의 도메인 | **도메인 교체** — courses/mentoring/payments UI·API 제거 |
| 첫 수직 슬라이스 | **사주 원국 + 오늘의 운세** |
| 엔진 | **오픈소스 라이브러리** (`sajupy` 우선, 실패 시 동급 만세력 라이브러리) |
| 인증 | **게스트 + 로컬 이메일 로그인 병행** |
| 프론트 포트 | **6000** (`http://localhost:6000`) |
| 백엔드 포트 | **8000** (`http://localhost:8000`, Swagger `/docs`) |
| DB 포트 | **5432** |
| 접근 방식 | 모듈형 클린 슬레이트 + 수직 슬라이스 (Approach A) |

---

## 3. Architecture

```
Browser → http://localhost:6000 (Next.js)
              │
              │ NEXT_PUBLIC_API_URL=http://localhost:8000
              ▼
         FastAPI :8000
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
 fortune   auth     profiles
    │
    ▼
 SajuEngine (sajupy wrapper)
    │
    ▼
 Postgres (users, fortune_profiles)
```

### 3.1 Principles

- **계산은 공개**: `POST /api/fortune/saju` 는 인증 불필요 (게스트 보장)
- **저장만 보호**: `/api/profiles/*` 는 Bearer JWT 필수
- **엔진 격리**: `app/services/saju_engine.py` 가 라이브러리를 감쌈. API 스키마 ≠ 라이브러리 타입
- **일운 1차**: 규칙 기반 템플릿 (일간 × 오늘 간지). LLM 없음
- **Surgical domain swap**: 강의 관련 파일 제거, auth/security/database 셸 유지

### 3.2 Ports & env

| 변수 | 값 |
|------|-----|
| `FRONTEND_URL` | `http://localhost:6000` |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` |
| `DATABASE_URL` | `postgresql+asyncpg://user:password@localhost:5432/saasdb` (compose: host `db`) |
| Frontend host port | `6000` |
| Backend host port | `8000` |

CORS `allow_origins` 에 `http://localhost:6000` 포함.

---

## 4. Modules & file map

### 4.1 Remove / deactivate

**Backend**

- `app/api/courses.py`, `payments.py`, `mentoring.py`, `admin.py`, `dashboard.py` (or strip to empty health-only if needed)
- Models: `course`, `clip`, `category`, `mentor`, `payment`, `review`, `roadmap`, course-related `profile` fields if any

**Frontend**

- `(marketing)/courses/**`, `(user-dashboard)/instructor/**`, `admin/**`
- Charts/KPI that only serve course admin (optional keep if unused later — prefer delete)

### 4.2 Keep & adapt

- `app/api/auth.py`, `deps.py`, `core/security.py`, `core/database.py`, `core/config.py`
- `models/user.py` (email, hashed_password, is_superuser, is_verified)
- Frontend `lib/auth-context.tsx`, `lib/api.ts`, login/register pages
- Dockerfiles, `docker-compose.yml` (ports updated)

### 4.3 Create

```
backend/app/api/fortune.py
backend/app/api/profiles.py
backend/app/services/saju_engine.py
backend/app/models/fortune_profile.py
backend/app/schemas/fortune.py          # request/response DTOs if not inline
backend/tests/test_saju_engine.py
backend/tests/test_fortune_api.py
backend/tests/test_profiles_api.py

frontend/app/(marketing)/page.tsx       # guest 입력 랜딩
frontend/app/fortune/result/page.tsx    # 결과
frontend/app/(user)/me/page.tsx         # 저장된 프로필 (auth)
frontend/components/fortune/SajuForm.tsx
frontend/components/fortune/SajuResult.tsx

CLAUDE.md                               # from template, project-tuned
PROGRESS.md
docs/superpowers/specs/... (this file)
docs/superpowers/plans/...
```

---

## 5. API contracts

### 5.1 Health

`GET /api/health` → `{ "status": "ok", "service": "FortuneOne" }`

### 5.2 Fortune (public)

`POST /api/fortune/saju`

**Request**

```json
{
  "solar_date": "1990-05-15",
  "hour": 14,
  "minute": 30,
  "gender": "male",
  "time_unknown": false
}
```

- `solar_date`: `YYYY-MM-DD`, 양력
- `hour`/`minute`: 0–23 / 0–59; `time_unknown: true` 이면 시주 생략 또는 기본 정오 정책 명시 (구현: **정오 12:00 가정**, 응답에 `time_assumed: true`)
- `gender`: `male` | `female` (대운 방향 예약; MVP 일운에는 선택 사용)

**Response 200**

```json
{
  "input": {
    "solar_date": "1990-05-15",
    "hour": 14,
    "minute": 30,
    "gender": "male",
    "time_assumed": false
  },
  "pillars": {
    "year":  { "stem": "庚", "branch": "午" },
    "month": { "stem": "辛", "branch": "巳" },
    "day":   { "stem": "甲", "branch": "子" },
    "hour":  { "stem": "辛", "branch": "未" }
  },
  "day_master": "甲",
  "elements": {
    "wood": 1,
    "fire": 2,
    "earth": 1,
    "metal": 2,
    "water": 2
  },
  "daily": {
    "date": "2026-07-19",
    "summary": "…",
    "scores": {
      "overall": 72,
      "love": 60,
      "money": 80,
      "health": 70
    },
    "lucky": {
      "color": "청색",
      "direction": "동"
    }
  }
}
```

**Errors**

- `422` validation (bad date, hour out of range)
- `400` engine failure (unparseable / out of library range) with message

### 5.3 Auth (local email)

Reuse existing JWT patterns:

- `POST /api/auth/register` `{ email, password, full_name? }`
- `POST /api/auth/login` → access token
- `GET /api/auth/me` Bearer

Strip any course-enrollment side effects from register/login.

### 5.4 Profiles (auth required)

`FortuneProfile`

| field | type | notes |
|-------|------|--------|
| id | uuid/int | PK |
| user_id | FK users | owner |
| label | str | e.g. "나", "엄마" |
| solar_date | date | |
| hour | int \| null | |
| minute | int \| null | |
| time_unknown | bool | |
| gender | str | male/female |
| created_at | datetime | |

Endpoints:

- `GET /api/profiles` — list mine
- `POST /api/profiles` — create
- `GET /api/profiles/{id}` — get one (owner only)
- `DELETE /api/profiles/{id}` — delete (owner only)

Optional convenience: `POST /api/profiles/{id}/saju` → load profile fields and call engine (auth). Guest flow does not need this.

---

## 6. Engine design

### 6.1 Wrapper interface

```python
# conceptual
class SajuEngine:
    def calculate(
        self,
        solar_date: date,
        hour: int,
        minute: int,
        gender: str,
        *,
        as_of: date | None = None,  # for daily fortune target day
    ) -> SajuResult: ...
```

- Library-specific import only inside `saju_engine.py`
- Map library output → `SajuResult` DTO (pillars, day_master, elements)
- `daily_fortune(day_master, as_of)` rule table lives in same module or `daily_rules.py`

### 6.2 Daily fortune (rule-based MVP)

- Deterministic: same day_master + calendar day → same scores/summary
- Simple hash or 60-gapja index into template pool (not random per request)
- No external API calls

### 6.3 Library selection

1. Try `sajupy` (PyPI) — 1900–2100 만세력
2. If API unfit or broken on Python target: document fallback in PROGRESS and switch to next candidate (`fortuneteller` / fork) without changing HTTP contract

---

## 7. Frontend UX

### 7.1 Guest path

1. `/` — form: solar date, time (optional “모름”), gender, submit
2. `POST /api/fortune/saju`
3. `/fortune/result` — pillars grid, elements bars, daily card  
   (state via query/sessionStorage or client state; avoid putting PII in public logs)

### 7.2 Auth path

1. `/register`, `/login` (port 6000)
2. After login: “결과 저장” → `POST /api/profiles`
3. `/me` — list profiles, “다시 보기” → same result UI with prefilled calc

### 7.3 UI stack

Keep Tailwind + existing shadcn button/input/card. No new design system.

---

## 8. Data & migrations

- Prefer SQLModel `create_all` for local MVP speed **or** Alembic new revision that drops course tables and adds `fortune_profiles`
- Decision for implementation: **Alembic revision** if existing migrations must stay coherent; otherwise clean slate DB volume for local is acceptable
- Local wipe OK: `docker compose down -v` documented in README

---

## 9. Testing & verification

| Layer | What |
|-------|------|
| Unit | Engine: fixed birth datetime → expected pillars (2–3 golden cases) |
| API | fortune happy path, validation 422, profiles 401 without token |
| Manual | Guest form → result on :6000; register → save → list on /me |
| Compose | `docker compose up --build` → frontend 6000, API 8000 |

No claim of “done” without running commands (template guidelines).

---

## 10. Git workflow

- Remote: `https://github.com/optimussh/FortuneOne.git` as `origin` for this product
- Commit format: `type(scope): English summary — 한국어 요약`
- Before each commit: update root `PROGRESS.md`
- One logical change per commit; push after each phase gate
- Never force-push `main`

---

## 11. Phased delivery (implementation order)

| Phase | Outcome |
|-------|---------|
| 0 | Repo bootstrap: FortuneOne remote, CLAUDE/PROGRESS, ports 6000, rename product |
| 1 | Strip course domain; health + empty fortune router |
| 2 | SajuEngine + `POST /api/fortune/saju` + unit tests |
| 3 | Guest UI form + result page on :6000 |
| 4 | Local auth cleanup + FortuneProfile CRUD + /me |
| 5 | pytest suite, compose E2E, README local guide |

Post-MVP (out of this design): 대운/용신, SEO pages, affiliate mock, social login, RAG, payments, PWA, app.

---

## 12. Success criteria (MVP done)

- [ ] Guest: birth datetime only → pillars + daily fortune at `http://localhost:6000`
- [ ] Member: register/login → save profile → reload after re-login
- [ ] Engine unit tests + fortune API tests pass
- [ ] Compose (or documented local run) works: UI 6000, API 8000
- [ ] FortuneOne has phase commits pushed

---

## 13. Open risks

| Risk | Mitigation |
|------|------------|
| `sajupy` API mismatch / license | Wrapper + golden tests; swap library without HTTP change |
| Course models leave orphan FK | Full domain delete + DB volume reset in Phase 1 |
| knowbridge remote still set | Phase 0 switch origin to FortuneOne only |

---

## 14. Self-review checklist

- [x] No TBD placeholders for MVP scope
- [x] Guest vs auth boundaries consistent
- [x] Port 6000 frontend / 8000 backend explicit
- [x] Out-of-scope listed; post-MVP not mixed into Phase 0–5 tasks
- [x] API field names consistent across sections
