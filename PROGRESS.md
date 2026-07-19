# Progress

프로젝트 진행 현황 로그. 커밋 직전 갱신 (`claude_Template` git 규칙).

## 2026-07-19

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
