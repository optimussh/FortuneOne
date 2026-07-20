from datetime import date

from app.services.saju_engine import SajuEngine
from app.services.saju_report import build_full_report
from app.services.wealth_year import build_wealth_year


def test_wealth_year_p1_p4_structure():
    r = SajuEngine().calculate(date(1990, 8, 27), 8, 0, "male")
    birth = date(1990, 8, 27)
    a = build_wealth_year(
        r,
        birth,
        "male",
        year=2026,
        display_name="테스트",
        time_slot="chen",
        hour=8,
        time_unknown=False,
    )
    b = build_wealth_year(
        r,
        birth,
        "male",
        year=2026,
        display_name="테스트",
        time_slot="chen",
        hour=8,
        time_unknown=False,
    )
    assert a["title"] == "2026 부자되기"
    assert a["overview"]["body"] == b["overview"]["body"]
    assert len(a["month_guide"]["months"]) == 12
    assert all("grade_label" in m for m in a["month_guide"]["months"])
    assert len(a["calendar"]["months"]) == 12
    jan = a["calendar"]["months"][0]
    assert jan["month"] == 1
    assert len(jan["days"]) == 31
    assert "body" in jan["days"][0]
    assert "body_long" in jan["days"][0]
    assert jan["days"][0]["score"] in (30, 40, 50, 60, 70, 80, 90)
    assert a["header"]["lunar_text"] != "—"
    assert a["elements"]["strength"] in ("신강", "신약")
    assert len(a["daeun"]["periods"]) == 10
    assert a["export"]["body"]
    assert a["monetization"]["enabled"] is False
    # different year changes text
    c = build_wealth_year(r, birth, "male", year=2025, display_name="테스트")
    assert c["overview"]["body"] != a["overview"]["body"]


def test_full_report_has_wealth_year():
    r = SajuEngine().calculate(date(1990, 5, 15), 14, 30, "male")
    rep = build_full_report(r, date(1990, 5, 15), "male", display_name="회원")
    assert "wealth_year" in rep
    assert len(rep["wealth_year"]["calendar"]["months"]) == 12
