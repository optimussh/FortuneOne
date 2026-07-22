# FortuneOne 배포 가이드

## 로컬 (개발)

```bash
# API
cd backend
pip install -r requirements.txt
# optional: copy .env.example → .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Web
cd frontend
npm install
set NEXT_PUBLIC_API_URL=http://127.0.0.1:8000   # Windows
npm run dev   # :6100
```

또는 `scripts/start-dev.ps1`

## Docker Compose

```bash
docker compose up --build
```

| 서비스 | URL |
|--------|-----|
| Web | http://localhost:6100 |
| API | http://localhost:8000/docs |

환경변수는 `docker-compose.yml` 및 각 서비스 `.env`로 주입합니다.

### 권장 환경변수 (프로덕션)

```env
# backend
DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST:5432/fortuneone
SECRET_KEY=<long-random>
FRONTEND_URL=https://your-domain.com
PAYMENT_PROVIDER=toss   # or mock
PAYMENT_TEST_MODE=false
TOSS_CLIENT_KEY=live_ck_...
TOSS_SECRET_KEY=live_sk_...
BUSINESS_NAME=...
BUSINESS_CEO=...
BUSINESS_NUMBER=...
BUSINESS_MAIL_ORDER=...
BUSINESS_ADDRESS=...
BUSINESS_PHONE=...
BUSINESS_EMAIL=...

# frontend build
NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

## CI

GitHub Actions: `.github/workflows/ci.yml`

- backend pytest  
- frontend `tsc --noEmit`  
- docker image build (push 없음)

## 스테이징 체크리스트

1. [ ] HTTPS 도메인
2. [ ] API CORS에 프론트 도메인 추가 (`main.py`)
3. [ ] 약관·사업자·환불 페이지 실정보
4. [ ] `PAYMENT_PROVIDER=mock` 으로 결제 E2E
5. [ ] 토스 테스트 키 스모크
6. [ ] 웹훅 URL `https://api.../api/payments/webhook`

## 다시보기 정책 (코드 반영)

| 채널 | 기간 |
|------|------|
| 웹 (로그인) | 결제 후 **7일** |
| 이메일 링크 `?token=` | 결제 후 **30일** |

상수: `backend/app/services/monetization.py` → `WEB_VIEW_DAYS`, `EMAIL_VIEW_DAYS`
