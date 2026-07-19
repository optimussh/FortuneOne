# FortuneOne — Agent Working Rules

## Working Style (highest priority)

Behavioral guidelines (Karpathy-inspired): think before coding, simplicity first, surgical changes, goal-driven verification.

- Language: **Korean** for explanation; **English** for code, identifiers, commits.
- No speculative features. MVP scope: design/plan under `docs/superpowers/`.
- Verification = run commands, not just read code.
- Before every commit: update `PROGRESS.md`, then stage specific files.

## Git

```
type(scope): English summary — 한국어 요약
```

- One logical change per commit; push to `origin` (FortuneOne) after each phase.
- Never force-push `main` without explicit user request.

## Stack

- Frontend: Next.js 15 — **port 6100** (not 6000: Chrome ERR_UNSAFE_PORT)
- Backend: FastAPI — port 8000
- DB: PostgreSQL 5432
- Design: `docs/superpowers/specs/2026-07-19-fortuneone-local-mvp-design.md`
- Plan: `docs/superpowers/plans/2026-07-19-fortuneone-local-mvp.md`

## Full template rules (optional deep dive)

Source copy: `claude_Template-main/claude_Template-main/rules/`
