# FortuneOne

사주 · 운세 · 타로 · 궁합 웹 앱 (Next.js 15 + FastAPI + PostgreSQL)

## Ports

| Service  | Port | 비고 |
|----------|------|------|
| Frontend | **6100** | Chrome이 6000을 `ERR_UNSAFE_PORT`로 차단 |
| API      | **8000** | Swagger `/docs` |
| Postgres | **5432** | |

## 빠른 실행 (로컬 권장)

DB만 Docker로 켠 뒤 앱은 로컬:

```bash
docker compose up -d db

# terminal 1
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# terminal 2
cd frontend
npm install
npm run dev   # http://localhost:6100
```

전체 Docker:

```bash
docker compose up --build
```

- App: http://localhost:6100  
- API: http://localhost:8000/docs  

## 기능

| 기능 | 경로 / API |
|------|------------|
| 사주 원국 + 일운 + 용신 + 대운 + 행운 아이템 | `/` → `/fortune/result` · `POST /api/fortune/saju` |
| 띠별 오늘의 운세 | `/today` · `GET /api/fortune/zodiac/today` |
| 타로 1/3/5장 | `/tarot` · `POST /api/fortune/tarot` |
| 궁합 | `/compatibility` · `POST /api/fortune/compatibility` |
| 이메일 가입/로그인 · 사주 프로필 저장 | `/login` `/register` `/me` |
| 제휴 추천(mock) | 사주 결과 하단 · `GET /api/fortune/affiliate/recommendations` |

게스트는 로그인 없이 사주/타로/띠/궁합 이용 가능. 프로필 저장만 JWT 필요.

## Tests

```bash
cd backend
python -m pytest -v
```

## Docs

- Design: `docs/superpowers/specs/2026-07-19-fortuneone-local-mvp-design.md`
- Plan: `docs/superpowers/plans/2026-07-19-fortuneone-local-mvp.md`

## Repo

https://github.com/optimussh/FortuneOne
