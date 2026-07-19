# Progress

프로젝트 진행 현황 로그. 커밋 직전 갱신 (`claude_Template` git 규칙).

## 2026-07-19

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
