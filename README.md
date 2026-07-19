# FortuneOne

로컬 MVP 운세 플랫폼 — 사주 원국 + 오늘의 운세.  
Next.js 15 · FastAPI · PostgreSQL

## Ports

| Service  | Port |
|----------|------|
| Frontend | **6000** |
| API      | **8000** |
| Postgres | **5432** |

## Quick start (Docker)

```bash
cp .env.example .env   # 필요 시 값 수정
docker compose up --build
```

- App: http://localhost:6000  
- API docs: http://localhost:8000/docs  
- Health: http://localhost:8000/api/health  

## Local (without Docker)

**DB:** Postgres 5432, `DATABASE_URL` 설정 (예: `postgresql+asyncpg://user:password@localhost:5432/saasdb`)

**Backend**

```bash
cd backend
pip install -r requirements.txt
# optional: alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev   # port 6000
```

## Flows

### Guest (no login)

1. Open http://localhost:6000  
2. Enter birth (solar date, optional time / 시간 모름, gender)  
3. See result at `/fortune/result` (사주 4주 · 오행 · 일운)

### Auth + profiles

1. Register / Login (`/register`, `/login`)  
2. On result page, save profile (JWT)  
3. Manage profiles at `/me` (list, re-run saju, delete)

## Tests

```bash
cd backend
python -m pytest -v
```

## Docs

- Design: [docs/superpowers/specs/2026-07-19-fortuneone-local-mvp-design.md](docs/superpowers/specs/2026-07-19-fortuneone-local-mvp-design.md)  
- Plan: [docs/superpowers/plans/2026-07-19-fortuneone-local-mvp.md](docs/superpowers/plans/2026-07-19-fortuneone-local-mvp.md)  
- Progress log: [PROGRESS.md](PROGRESS.md)
