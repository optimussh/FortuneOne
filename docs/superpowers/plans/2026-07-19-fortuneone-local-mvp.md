# FortuneOne Local MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a local FortuneOne MVP: guest saju pillars + daily fortune on port 6000, plus local email login and profile save, on FastAPI + Next.js with commits pushed to FortuneOne.

**Architecture:** Strip course domain from saas-template; add `SajuEngine` (sajupy wrapper) behind public `POST /api/fortune/saju`; keep JWT auth for `fortune_profiles` only. Frontend on **6000**, API on **8000**.

**Tech Stack:** Next.js 15, React 19, Tailwind 4, FastAPI, SQLModel, PostgreSQL, Docker Compose, sajupy (or equivalent), pytest

**Design spec:** `docs/superpowers/specs/2026-07-19-fortuneone-local-mvp-design.md`

---

## File structure (target)

| Path | Responsibility |
|------|----------------|
| `backend/app/services/saju_engine.py` | Library wrapper + daily rules |
| `backend/app/api/fortune.py` | Public saju endpoint |
| `backend/app/api/profiles.py` | Auth-only profile CRUD |
| `backend/app/models/fortune_profile.py` | DB model |
| `backend/app/models/user.py` | Keep; drop course FKs if any |
| `backend/app/main.py` | Routers, CORS for :6000 |
| `backend/app/core/config.py` | PROJECT_NAME FortuneOne, FRONTEND_URL |
| `frontend/app/(marketing)/page.tsx` | Guest form landing |
| `frontend/app/fortune/result/page.tsx` | Result UI |
| `frontend/app/(user)/me/page.tsx` | Saved profiles |
| `frontend/components/fortune/*` | Form + result components |
| `docker-compose.yml` | frontend `6000:3000` or `6000:6000` |
| `PROGRESS.md` | Per-commit log |
| `CLAUDE.md` | Project agent rules |

---

### Task 0: Repo bootstrap (FortuneOne remote, docs, ports, naming)

**Files:**
- Create: `PROGRESS.md`, `CLAUDE.md` (minimal pointer to rules if full template copy deferred)
- Modify: `docker-compose.yml`, `backend/app/core/config.py`, `frontend/package.json` (dev port), `.env.example` if present
- Docs: already created under `docs/superpowers/`

- [ ] **Step 1: Set git remote to FortuneOne**

```bash
git remote rename origin knowbridge 2>nul; git remote remove origin 2>nul
git remote add origin https://github.com/optimussh/FortuneOne.git
git remote -v
```

If `knowbridge` remote should be kept: `git remote add knowbridge <old-url>` then `git remote set-url origin https://github.com/optimussh/FortuneOne.git`.

- [ ] **Step 2: Write root PROGRESS.md**

```markdown
# Progress

## 2026-07-19
- docs: FortuneOne local MVP design + implementation plan
- chore: bootstrap ports (frontend 6000), product rename pending in code
```

- [ ] **Step 3: Update config product name and FRONTEND_URL default**

In `backend/app/core/config.py`:

```python
PROJECT_NAME: str = "FortuneOne"
FRONTEND_URL: str = "http://localhost:6000"
```

- [ ] **Step 4: Docker Compose frontend port 6000**

```yaml
  frontend:
    build: ./frontend
    ports:
      - "6000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 5: package.json dev script**

```json
"dev": "next dev --turbopack -p 6000"
```

- [ ] **Step 6: CORS in main.py**

Ensure `allow_origins` includes `settings.FRONTEND_URL` and `http://localhost:6000`.

- [ ] **Step 7: Commit and push**

```bash
# update PROGRESS.md first
git add docs/superpowers PROGRESS.md docker-compose.yml backend/app/core/config.py frontend/package.json backend/app/main.py CLAUDE.md
git commit -m "chore: bootstrap FortuneOne docs and port 6000 — 문서·포트 6000 부트스트랩"
git push -u origin main
```

If FortuneOne is empty/non-fast-forward, resolve with user before force-push (never force main without ask).

---

### Task 1: Strip course domain

**Files:**
- Delete or stop importing: `backend/app/api/courses.py`, `payments.py`, `mentoring.py`, `admin.py`, `dashboard.py`
- Delete models only referenced by courses (course, clip, category, mentor, payment, review, roadmap) if safe
- Modify: `backend/app/main.py` — remove those routers
- Delete frontend routes under courses/instructor/admin
- Modify marketing home later in Task 3; for now leave a placeholder page if needed

- [ ] **Step 1: Remove course routers from main.py**

Keep only auth (and later fortune/profiles). Add temporary:

```python
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FortuneOne"}
```

- [ ] **Step 2: Remove frontend course/admin routes**

Delete directories:
- `frontend/app/(marketing)/courses`
- `frontend/app/(user-dashboard)/instructor`
- `frontend/app/admin`

Fix any broken imports in layout/Header links (point to `/` and `/login` only).

- [ ] **Step 3: Drop unused models from create_all import graph**

Ensure `main.py` / models package no longer import Course tables. Prefer deleting model files that are course-only.

- [ ] **Step 4: Run backend import check**

```bash
cd backend
python -c "from app.main import app; print('ok', app.title)"
```

Expected: `ok FortuneOne` (or similar)

- [ ] **Step 5: Commit**

```bash
git add -A  # prefer specific paths; exclude backend/123.pdf and claude_Template-main if not wanted
git commit -m "refactor: strip course domain for FortuneOne — 강의 도메인 제거"
git push origin main
```

Do **not** commit `backend/123.pdf` or nested `claude_Template-main` zip junk unless intentional. Prefer copying needed rules into root `CLAUDE.md` / `rules/` later.

---

### Task 2: Saju engine + public API

**Files:**
- Create: `backend/app/services/__init__.py`, `backend/app/services/saju_engine.py`
- Create: `backend/app/api/fortune.py`
- Create: `backend/tests/test_saju_engine.py`, `backend/tests/test_fortune_api.py`
- Modify: `backend/requirements.txt`, `backend/app/main.py`

- [ ] **Step 1: Add dependency**

```text
sajupy>=0.2.0
pytest>=8.0.0
httpx>=0.27.0
```

```bash
cd backend
pip install sajupy pytest httpx
```

If `sajupy` install fails, stop and pick documented fallback library; keep the same `SajuResult` shape.

- [ ] **Step 2: Write failing engine test**

`backend/tests/test_saju_engine.py`:

```python
from datetime import date
from app.services.saju_engine import SajuEngine

def test_calculate_returns_four_pillars():
    engine = SajuEngine()
    result = engine.calculate(
        solar_date=date(1990, 5, 15),
        hour=12,
        minute=0,
        gender="male",
    )
    assert result.pillars.year.stem
    assert result.pillars.year.branch
    assert result.pillars.day.stem
    assert result.day_master
    assert sum(result.elements.values()) >= 4
```

- [ ] **Step 3: Run test — expect fail**

```bash
cd backend
pytest tests/test_saju_engine.py -v
```

Expected: import/collection error or FAIL

- [ ] **Step 4: Implement SajuEngine**

Implement `calculate` mapping library output to:

```python
@dataclass
class StemBranch:
    stem: str
    branch: str

@dataclass
class Pillars:
    year: StemBranch
    month: StemBranch
    day: StemBranch
    hour: StemBranch | None

@dataclass
class DailyFortune:
    date: date
    summary: str
    scores: dict  # overall, love, money, health
    lucky: dict   # color, direction

@dataclass
class SajuResult:
    pillars: Pillars
    day_master: str
    elements: dict[str, int]
    daily: DailyFortune
    time_assumed: bool = False
```

Daily: deterministic template from `day_master` + `as_of.toordinal()`.

- [ ] **Step 5: Run engine tests — expect pass**

```bash
pytest tests/test_saju_engine.py -v
```

- [ ] **Step 6: Implement fortune router**

Pydantic models matching design spec; call `SajuEngine`; register `prefix="/api/fortune"`.

- [ ] **Step 7: API test with TestClient**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_saju_endpoint_ok():
    r = client.post("/api/fortune/saju", json={
        "solar_date": "1990-05-15",
        "hour": 14,
        "minute": 30,
        "gender": "male",
        "time_unknown": False,
    })
    assert r.status_code == 200
    body = r.json()
    assert "pillars" in body
    assert "daily" in body
```

- [ ] **Step 8: Commit**

```bash
git commit -m "feat(fortune): saju pillars and daily rule engine API — 사주 원국·일운 API"
git push origin main
```

---

### Task 3: Guest UI on port 6000

**Files:**
- Create: `frontend/components/fortune/SajuForm.tsx`, `SajuResult.tsx`
- Modify: `frontend/app/(marketing)/page.tsx`
- Create: `frontend/app/fortune/result/page.tsx`
- Modify: `frontend/lib/api.ts` — `postFortuneSaju`
- Modify: Header links

- [ ] **Step 1: API helper**

```typescript
export async function postFortuneSaju(body: {
  solar_date: string;
  hour: number;
  minute: number;
  gender: "male" | "female";
  time_unknown: boolean;
}) {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const res = await fetch(`${base}/api/fortune/saju`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
```

- [ ] **Step 2: Landing form**

Date input, optional time + “시간 모름”, gender select, submit → store JSON in `sessionStorage` key `fortune:last` → `router.push("/fortune/result")`.

- [ ] **Step 3: Result page**

Read `sessionStorage`, render pillars + elements + daily card; empty state → link home.

- [ ] **Step 4: Manual verify**

```bash
# terminal 1
cd backend; uvicorn app.main:app --reload --port 8000
# terminal 2
cd frontend; npm run dev
```

Open `http://localhost:6000`, submit birth data, see result.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(web): guest saju form and result page — 게스트 사주 입력·결과"
git push origin main
```

---

### Task 4: Local auth + profiles

**Files:**
- Create: `backend/app/models/fortune_profile.py`, `backend/app/api/profiles.py`
- Modify: `backend/app/api/auth.py` (remove course side effects)
- Modify: `backend/app/main.py`
- Create: `frontend/app/(user)/me/page.tsx` or reuse dashboard layout simplified
- Modify: result page “저장” button when logged in

- [ ] **Step 1: FortuneProfile model**

SQLModel table `fortune_profiles` with fields from design spec; FK to `user.id`.

- [ ] **Step 2: profiles router**

CRUD list/create/get/delete with `get_current_user` dependency; 401 without token; 404 other user’s id.

- [ ] **Step 3: Test profiles 401**

```python
def test_profiles_requires_auth():
    r = client.get("/api/profiles")
    assert r.status_code in (401, 403)
```

- [ ] **Step 4: Frontend /me + save from result**

Use existing auth context token in `Authorization: Bearer …`.

- [ ] **Step 5: Manual verify guest still works without login**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(auth): local login and fortune profiles — 로컬 로그인·사주 프로필"
git push origin main
```

---

### Task 5: Local quality gate

**Files:**
- Modify: `README.md` — FortuneOne local run (ports 6000/8000)
- Modify: `PROGRESS.md`
- Ensure tests green

- [ ] **Step 1: Run full backend tests**

```bash
cd backend
pytest -v
```

Expected: all PASS

- [ ] **Step 2: Compose (if Docker available)**

```bash
docker compose up --build
```

Verify:
- `http://localhost:6000` loads
- `http://localhost:8000/api/health` ok
- `http://localhost:8000/docs` shows fortune + auth + profiles

- [ ] **Step 3: README rewrite (minimal)**

Document env, ports, guest path, login path, pytest command.

- [ ] **Step 4: Final commit**

```bash
git commit -m "docs(test): local MVP verification and README — 로컬 MVP 검증 정리"
git push origin main
```

---

## Spec coverage check

| Design section | Tasks |
|----------------|-------|
| Domain strip | Task 1 |
| Engine + public API | Task 2 |
| Guest UI :6000 | Task 0 ports + Task 3 |
| Auth + profiles | Task 4 |
| Verification | Task 5 |
| FortuneOne git | Task 0 + every commit push |
| Out of scope affiliate/LLM/etc. | Not scheduled |

## Placeholder scan

No TBD steps; library fallback path is explicit stop-and-choose, not silent skip.

## Type consistency

- Request: `solar_date`, `hour`, `minute`, `gender`, `time_unknown`
- Response: `pillars`, `day_master`, `elements`, `daily`, `input.time_assumed`
- Profile: `label`, `solar_date`, `hour`, `minute`, `time_unknown`, `gender`
