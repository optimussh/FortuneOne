from datetime import date

from app.services.monetization import apply_wealth_access, catalog
from app.services.saju_engine import SajuEngine
from app.services.wealth_year import build_wealth_year


def test_catalog_hybrid():
    c = catalog()
    assert c["enabled"] is True
    assert c["mode"] == "hybrid"
    assert len(c["packs"]) == 3
    assert c["wealth_year"]["price_krw"] == 3900


def test_wealth_free_preview_gates():
    r = SajuEngine().calculate(date(1990, 8, 27), 8, 0, "male")
    full = build_wealth_year(r, date(1990, 8, 27), "male", year=2026, display_name="T")
    locked = apply_wealth_access(full, unlocked=False, as_of=date(2026, 3, 15))
    assert locked["access"]["unlocked"] is False
    assert locked["overview"].get("locked") is True
    assert "미리보기" in locked["overview"]["body"] or "…" in locked["overview"]["body"]
    # month bodies locked
    assert all(m.get("locked") for m in locked["month_guide"]["months"])
    # March has free days, others empty/locked
    mar = next(m for m in locked["calendar"]["months"] if m["month"] == 3)
    assert 1 <= len(mar["days"]) <= 7
    assert locked["export"].get("locked") is True

    open_ = apply_wealth_access(full, unlocked=True, as_of=date(2026, 3, 15))
    assert open_["access"]["unlocked"] is True
    assert len(open_["calendar"]["months"][0]["days"]) >= 28
    assert open_["export"].get("body")
