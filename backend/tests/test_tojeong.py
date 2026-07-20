from datetime import date

from app.services.saju_engine import SajuEngine
from app.services.saju_report import build_full_report
from app.services.sipsung import mingshi_table, ten_god
from app.services.tojeong import build_tojeong


def test_ten_god_day_master_same_stem():
    assert ten_god("甲", "甲") == "비견"
    assert ten_god("甲", "乙") == "겁재"
    assert ten_god("甲", "丙") == "식신"
    assert ten_god("甲", "戊") == "편재"


def test_mingshi_has_four_columns():
    r = SajuEngine().calculate(date(1990, 8, 27), 8, 0, "male")
    table = mingshi_table(r)
    assert table["day_master"] == r.day_master
    assert len(table["columns"]) == 4
    keys = [c["key"] for c in table["columns"]]
    assert keys == ["hour", "day", "month", "year"]
    day_col = table["columns"][1]
    assert day_col["stem_god"] == "일간"


def test_tojeong_stable_and_complete():
    r = SajuEngine().calculate(date(1990, 8, 27), 8, 0, "male")
    birth = date(1990, 8, 27)
    a = build_tojeong(
        r,
        birth,
        "male",
        year=2026,
        display_name="테스트",
        calendar_type="solar",
        time_slot="chen",
        hour=8,
        time_unknown=False,
    )
    b = build_tojeong(
        r,
        birth,
        "male",
        year=2026,
        display_name="테스트",
        calendar_type="solar",
        time_slot="chen",
        hour=8,
        time_unknown=False,
    )
    assert a["year"] == 2026
    assert a["overall"]["body"] == b["overall"]["body"]
    assert a["lucky"]["lucky_number"] == b["lucky"]["lucky_number"]
    assert len(a["months"]) == 12
    assert len(a["domains"]) == 6
    assert len(a["overall"]["body"]) > 200
    assert a["header"]["display_name"] == "테스트"
    assert a["mingshi"]["columns"]
    # different year → different seed content
    c = build_tojeong(r, birth, "male", year=2025, display_name="테스트")
    assert c["overall"]["body"] != a["overall"]["body"]


def test_full_report_includes_tojeong():
    r = SajuEngine().calculate(date(1990, 5, 15), 14, 30, "male")
    rep = build_full_report(
        r,
        date(1990, 5, 15),
        "male",
        display_name="회원",
        time_slot="wei",
        hour=14,
        time_unknown=False,
    )
    assert "tojeong" in rep
    assert "mingshi" in rep
    assert len(rep["tojeong"]["months"]) == 12
    assert rep["tojeong"]["year"] == 2026
