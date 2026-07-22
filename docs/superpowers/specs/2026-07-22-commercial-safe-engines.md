# Commercial-safe multi-engine fact layer

**Date:** 2026-07-22  
**Status:** Implemented

## Allowed engines (commercial SaaS OK)

| Engine | Package | License | Role | Notes |
|--------|---------|---------|------|--------|
| **sajupy** | `sajupy>=0.2.0` | **MIT** | Primary | https://github.com/0ssw1/sajupy |
| **lunar_python** (6tail) | `lunar_python>=1.3.0` | **MIT** | Cross-check | https://github.com/6tail/lunar-python |

Both allow commercial use, modification, and private SaaS without copyleft obligation (standard MIT attribution).

## Explicitly not integrated (this phase)

| Candidate | Why skipped |
|-----------|-------------|
| **sxtwl** | Needs native C++ build on Windows; install friction |
| Unlicensed / unknown GitHub gists | No clear commercial grant |
| GPL/AGPL engines | Copyleft risk for proprietary product distribution |
| Scraped commercial unse copy | Copyright risk |

## Merge policy

1. Run all registered **MIT/Apache/BSD** adapters.
2. **Primary = sajupy** when OK.
3. If secondary differs → keep primary, set `agreement=false`, list `warnings[]`.
4. Never silently average stems/branches.
5. Narrative (product text) stays FO-owned templates — engines only supply **facts**.

## Code

- `backend/app/services/engines/sajupy_adapter.py`
- `backend/app/services/engines/lunar_python_adapter.py`
- `backend/app/services/engines/merge.py`
- `SajuResult.chart_facts` + `full-report.chart_facts`

## Attribution (ship with product)

Include MIT notice for sajupy and lunar-python/6tail in distribution docs or About page.
