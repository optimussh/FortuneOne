# 2026 부자되기 (재물 연간 리포트)

**Date:** 2026-07-20  
**Status:** Implemented (P1–P4 + hybrid freemium gate + mock shop)

## Placement

- `/me` tab **`wealth`** · UI label **2026 부자되기** · deep link `/me?tab=wealth`
- Hub CTA (amber card)
- API: `full-report.wealth_year` via `build_wealth_year`

## Layers

| Phase | Feature | Status |
|-------|---------|--------|
| P1 | 총론 · 재물운 · 월 12 + 활용등급(5단) | ✅ |
| P2 | 월 피커 · 일자별 점수·짧은 문장 | ✅ |
| P3 | 음력 · 신살 태그 · 대운 스트립 · 오행 비중·신강/신약 | ✅ |
| P4 | 일자 장문 · TXT/인쇄 PDF · 수익화 미리보기 메타 | ✅ |

## Content policy

- Self-generated deterministic templates (seed = day_master + pillars + birth + `wealth_{year}`)
- Do **not** copy commercial copy
- Disclaimer: entertainment / not investment advice

## Monetization (later — design only)

Currently `monetization.enabled = false` (all content free).

Concepts stored in API for UI preview:

1. **구슬 (cyber currency)** ~100원/개 · packs 100/200/500 with bonus %
2. **단건 결제** ~3,900원 for full year wealth unlock
3. Spend hints: month unlock, day long, full calendar, PDF

### Product recommendation (for later discussion)

- **Hybrid**: free teaser (overview + grade chips + 7 days of current month) + 구슬 or one-shot unlock
- Prefer **one-shot report purchase** for first revenue (simpler trust) + beads later for tarot/extra draws
- Beads good for: daily tarot re-draw, ask questions, day-long unlocks
- Avoid hard paywall on core daily hub while growing users

## Roles vs other tabs

| Module | Focus |
|--------|--------|
| 오늘 / topics money | Today only |
| 토정 | Multi-domain year story |
| **부자되기** | Wealth only · months · day calendar |
