# Progress

프로젝트 진행 현황 로그. 커밋 직전 갱신 (`claude_Template` git 규칙).

## 2026-07-23 (catalog copy v3 — 3x 주제별 상세)

- **catalog v3:** 전 상품(128) `intro_blurbs`·`for_whom`·`diff_from_free_tabs`·`subtitle` 주제별 구체화·설득 문안
- **avg:** intro ~259→~778자, for_whom·기본탭 차이도 카테고리별 분기 (동일 문구 제거)
- **report:** 결과 섹션 본문 장면·실천 문단 추가 (장문)
- **script:** `python -m app.data.polish_catalog` · copy_version 3
- **web:** 상품 상세 소개/기본탭 차이 가독성

## 2026-07-23 (copy + UX polish)

- **narrative v3:** `product_report.py` — 문단 분리, 톤별 서문, 구간 역할(open/mid/action/close), FO 스탬프 제거, 카테고리 초점 키워드
- **store UX:** 목록 카드 티저·클릭 영역, 상세 sticky 결제 바, 체크아웃 스텝 표시
- **result UX:** 목차·문단 줄바꿈·메일 링크 복사 버튼·다시보기 안내
- **hub:** 프로필/상세/다시보기 빠른 링크, 역할 문구 단순화
- **test:** store report v3 assertions · pytest full

## 2026-07-23 (library entry + review)

- **web:** `/me`에 **내 구매 · 다시보기** CTA (웹 7일 · 메일 30일 안내)
- **web:** 결과 페이지 하단 라이브러리 링크 · profile_id 생략 시 unlock 행 복원(FE 게이트 제거)
- **smoke:** `backend/scripts/smoke_library_flow.py` — 결제→my-unlocks→웹/토큰 결과
- **verify:** pytest 42 · tsc · e2e smoke OK (API 재시작 후 my-unlocks items 형식 확인)

## 2026-07-23 (deploy CI + legal FO + re-view 7/30)

- **ci:** `.github/workflows/ci.yml` — pytest, tsc, docker build
- **docs:** `docs/DEPLOY.md` 배포·환경변수·스테이징 체크리스트
- **legal:** 이용약관·개인정보 FortuneOne 전면 교체 · 푸터 사업자 고지 템플릿
- **access:** 유료 다시보기 웹 **7일** · 이메일 토큰 **30일** (`content_unlocks` 컬럼)
- **shop:** 구슬·부자되기 → `/api/payments` 주문 플로우 통일

## 2026-07-22 (payment ready — mock + Toss template)

- **feat(payments):** provider `mock` | `toss` · orders/confirm/webhook/config
- **DB:** `payment_orders` · fulfill → store unlock / wealth / beads
- **web:** checkout → `/payments/success|fail` · Toss SDK hook
- **legal templates:** `/policy/refund` · `/policy/business`
- **env:** PAYMENT_* · TOSS_* · BUSINESS_* in `.env.example`
- **docs:** `2026-07-22-payment-ready.md`

## 2026-07-22 (product content quality pack)

- **catalog v2:** FO 제목·소개·이런분께·8단 구성 · money/career FO 상품 보강 (128종)
- **report:** 스토어 결과 장문(섹션당 ~300자+) · role_guide 포함
- **UX:** 스토어/허브/상세 사주에 **기본 탭 vs 스토어 심화** 역할 안내
- **script:** `backend/app/data/polish_catalog.py`

## 2026-07-22 (next: catalog UX + verification badge)

- **catalog:** 카테고리 스코어링 재분류 (money/career 키워드 보강) · 섹션 템플릿 6단 확장
- **feat(ui):** `ChartFactsBadge` — 상세 사주·스토어 결과에 교차검증 OK 뱃지
- **feat(report):** 상품 결과 문단 보강 (톤별 opener/mid/action/closer)
- **feat(web):** `/about/engines` MIT 고지 · 푸터/허브 링크
- **data:** product_catalog.json 재생성

## 2026-07-22 (commercial-safe multi-engine)

- **feat(engines):** MIT only multi-engine fact layer
  - primary `sajupy` · cross-check `lunar_python` (6tail)
  - disagreement → primary + warnings (no silent merge)
- **deps:** `lunar_python>=1.3.0`
- **API:** `GET /api/fortune/engines`, `chart_facts` on saju/full-report
- **docs:** `2026-07-22-commercial-safe-engines.md`
- **skip:** sxtwl (native build), GPL/unknown license, scraped copy

## 2026-07-22 (unsin benchmark store)

- **feat(store):** 샘플 IA 벤치마크 상품 카탈로그 **110** · `/store` 목록·상세·모의결제·결과
- **flow:** 사주 프로필 선택 → mock checkout → `product:{id}` unlock → 프로필 기반 리포트
- **copy:** 상용 문구 미복제 · 제목 치환 · FO 템플릿 본문 (추후 교체 가능)
- **docs:** `2026-07-22-unsin-benchmark-store.md` · multi-engine fact/narrative 권장
- **data:** `backend/app/data/product_catalog.json`

## 2026-07-20 (hybrid monetization)

- **feat(shop):** 구슬 지갑 · 팩 모의구매 · 부자되기 단건 해금 · spend API
- **feat(gate):** 부자되기 무료 미리보기(총론 일부·월 등급·7일) / 해금 시 전체
- **feat:** 타로 일일 추가 뽑기 구슬 3 · 질문 무료 1/일 후 구슬 2 · 타 프로필 심화 5
- **web:** `/shop` · 헤더 구슬 뱃지 · WealthYearPanel 해금 CTA
- **note:** 실제 PG 없음 · mock purchase · 점수=참고 지표 면책

## 2026-07-20 (wealth year P1–P4 — 부자되기)

- **feat(wealth):** `wealth_year.py` — 2026 부자되기 총론·재물운·월등급12·일자캘린더·장문
- **P3:** 음력(sajupy)·신살 태그·대운 스트립·오행 비중·신강/신약
- **P4:** TXT/인쇄 export · monetization preview 메타(구슬/단건, enabled=false)
- **feat(web):** `/me?tab=wealth` · `WealthYearPanel` · 허브 CTA
- **API:** `full-report.wealth_year`
- **test:** `tests/test_wealth_year.py`
- **docs:** `2026-07-20-wealth-rich-year.md`

## 2026-07-20 (tojeong tab — full proposal)

- **feat(tojeong):** 십성 명식표 `sipsung.py` · 연간 토정 리포트 `tojeong.py` (종합·월12·영역6·행운)
- **feat(report):** `build_full_report`에 `mingshi` + `tojeong` 포함 (프로필 이름·시진 반영)
- **feat(web):** `/me` 탭 **2026 토정** (서브탭 종합/월별/영역/숫자·색) · `?tab=tojeong`
- **feat(hub):** CTA 「2026 토정 보기」 → `/me?tab=tojeong`
- **test:** `tests/test_tojeong.py` 안정 시드·12개월·full-report 연동
- **docs:** `2026-07-20-tojeong-tab-proposal.md` → Implemented

## 2026-07-19 (retention A + tarot UX + p2/p3)

- **feat:** 데일리 허브 `/hub` · 출석 스트릭 · 운세 일기 · 주제 운세 4종
- **feat:** 타로 인터랙션 — 섞기 → 18장 뒷면 펼침 → 직접 선택 → 카드 비주얼 공개
- **feat:** 오늘의 타로 1회 · 공유 카드 · 질문형 운세(규칙) · PWA manifest · start-dev.ps1
- **API:** engagement, journal, tarot/shuffle|reveal, fortune/topic

## 2026-07-19 (member full report)

- **feat(auth):** 회원가입 시 필수 사주 정보(생년월일·성별·시간) 등록 + 프로필 자동 생성
- **feat(report):** 오늘의 운세(장문) · 2026 신년 · 오행 3그룹 · 인생풀이 4그룹 상세 리포트
- **feat(web):** `/me` 대시보드 탭 UI, 로그인 후 `/me` 이동, 사주 미등록 시 온보딩
- **API:** `POST /api/fortune/full-report`, `GET /api/profiles/primary/full-report`

## 2026-07-19 (product features)

- **fix/ops:** 포트 **6100** 기동 (Next dev). 백엔드는 로컬 uvicorn :8000 (compose 백엔드 재빌드 전 코드 반영)
- **feat:** 용신·대운·부족한 오행·행운 아이템(제휴 mock) 사주 응답 확장
- **feat:** 타로 / 띠별 일운 / 궁합 API + 페이지 (`/tarot` `/today` `/compatibility`)
- **feat:** 네비·홈 제품 랜딩, FortuneOne 브랜딩, OAuth 데드 버튼 제거
- **test:** pytest **18 passed**
- **verify:** `GET /` 6100 → 200, health/zodiac 200

## 2026-07-19 (port fix)

- **fix:** 프론트 포트 6000 → **6100** — Chromium `ERR_UNSAFE_PORT` (X11 예약 포트 차단)

## 2026-07-19

- **docs(test):** Task 5 로컬 MVP 품질 게이트
  - `cd backend; python -m pytest -v` → **13 passed**
  - `python -c "from app.main import app"` → import ok FortuneOne
  - `frontend`: `.next` clear 후 `npx tsc --noEmit` → exit 0
  - `docker compose up --build` → **OK**
    - db healthy :5432, frontend :6000 → HTTP 200
    - backend :8000 → `GET /api/health` `{"status":"ok","service":"FortuneOne"}`
    - `POST /api/fortune/saju` → HTTP 200
  - Compose 기동 픽스 (테스트 게이트용, 기능 추가 아님):
    - `frontend/.dockerignore` (node_modules 제외 — 컨텍스트 470MB 완화)
    - alembic `002` `down_revision` → `001_initial` (KeyError: '001')
    - `database.py` SQLModel `AsyncSession` (`.exec` 지원)
    - `bcrypt>=4.0.1,<4.1` pin (passlib × bcrypt 5.x 기동 실패)
  - README.md FortuneOne 최소 문서 (ports 6000/8000/5432, guest/auth, pytest, design/plan 링크)
- **feat(auth):** Task 4 로컬 로그인·사주 프로필
  - `FortuneProfile` 모델 + `GET/POST/GET/DELETE /api/profiles` (JWT 필수)
  - 선택: `POST /api/profiles/{id}/saju` 프로필 기반 재계산
  - Frontend `/me` 목록·다시 보기·삭제; 결과 화면 로그인 시 「프로필 저장」
  - 게스트 플로우는 무인증 유지; 미로그인 시 결과에서 「로그인 후 저장」 링크만
  - pytest: `tests/test_profiles_api.py` 401 커버 (전체 13 passed)
- **feat(web):** Task 3 게스트 사주 입력·결과 UI (port 6000)
  - `SajuForm` 랜딩: 양력 날짜, 선택 시각 + 시간 모름, 성별 → `POST /api/fortune/saju`
  - 성공 응답 `sessionStorage` key `fortune:last` 저장 후 `/fortune/result`
  - `SajuResult`: 사주 4주, 오행 바, 일운(요약·점수·행운 색/방향)
  - `postFortuneSaju` + 타입 (`lib/api.ts`); `tsc --noEmit` 통과
- **feat(fortune):** Task 2 사주 원국·일운 공개 API
  - `SajuEngine` (sajupy 래퍼) + 규칙 기반 일운 (`day_master` + `as_of` 결정론)
  - `POST /api/fortune/saju` 공개(무인증); `time_unknown` → 정오 12:00, `time_assumed`
  - pytest: `tests/test_saju_engine.py`, `tests/test_fortune_api.py` (8 passed)
  - deps: `sajupy>=0.2.0`, `pytest>=8.0.0`
- **refactor:** Task 1 잔여 강의 UI/미사용 컴포넌트 제거
  - Frontend: `(user-dashboard)/my-learning` 전체 삭제, charts / KPICard / DataTable 삭제
  - Backend: Follow 모델(`profile.py`) 및 base/alembic import 정리
- **refactor:** 강의 도메인 제거 (Task 1)
  - Backend: courses/payments/mentoring/admin/dashboard 라우터 삭제, `/api/health` 추가
  - Models: course/clip/category/mentor/payment/review/roadmap 삭제, User 관계 정리
  - Frontend: courses / instructor / admin 라우트 삭제, Header/Footer → `/` · `/login`
  - 마케팅 홈은 플레이스홀더 (Task 3에서 교체)
- **docs:** FortuneOne 로컬 MVP 설계 스펙 + 구현 플랜 작성
  - `docs/superpowers/specs/2026-07-19-fortuneone-local-mvp-design.md`
  - `docs/superpowers/plans/2026-07-19-fortuneone-local-mvp.md`
- **chore:** 프론트 포트 **6000**, 제품명 FortuneOne, CORS/compose/README/.env.example 정렬
- **decisions:** 도메인 교체 / 사주원국+일운 / sajupy / 게스트+로컬로그인 병행

## 2026-07-22 (compatibility detail)

- **feat(compat):** 양력/음력·12시진 입력, 음력→양력 변환, 상세 섹션 8개·항목별 점수
- **web:** 궁합 페이지 SajuDetailForm 2인 입력 + 상세 결과 UI
