from datetime import date

from app.services.saju_engine import SajuEngine


def test_calculate_returns_four_pillars():
    engine = SajuEngine()
    result = engine.calculate(
        solar_date=date(1990, 5, 15),
        hour=12,
        minute=0,
        gender="male",
    )
    assert result.pillars.year.stem
    assert result.pillars.year.branch
    assert result.pillars.day.stem
    assert result.day_master
    assert sum(result.elements.values()) >= 4


def test_calculate_day_master_matches_day_stem():
    engine = SajuEngine()
    result = engine.calculate(
        solar_date=date(1990, 5, 15),
        hour=14,
        minute=30,
        gender="male",
    )
    assert result.day_master == result.pillars.day.stem
    assert result.pillars.hour is not None
    assert result.pillars.hour.stem
    assert result.pillars.hour.branch


def test_daily_fortune_is_deterministic():
    engine = SajuEngine()
    as_of = date(2026, 7, 19)
    a = engine.calculate(
        solar_date=date(1990, 5, 15),
        hour=14,
        minute=30,
        gender="male",
        as_of=as_of,
    )
    b = engine.calculate(
        solar_date=date(1990, 5, 15),
        hour=14,
        minute=30,
        gender="male",
        as_of=as_of,
    )
    assert a.daily.summary == b.daily.summary
    assert a.daily.scores == b.daily.scores
    assert a.daily.lucky == b.daily.lucky
    assert a.daily.date == as_of
    for key in ("overall", "love", "money", "health"):
        assert key in a.daily.scores
        assert 0 <= a.daily.scores[key] <= 100
    assert "color" in a.daily.lucky
    assert "direction" in a.daily.lucky


def test_elements_keys():
    engine = SajuEngine()
    result = engine.calculate(
        solar_date=date(1990, 5, 15),
        hour=14,
        minute=30,
        gender="female",
    )
    assert set(result.elements) == {"wood", "fire", "earth", "metal", "water"}
