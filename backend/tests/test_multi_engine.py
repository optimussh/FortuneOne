from datetime import date

from app.services.engines.merge import COMMERCIAL_SAFE_ENGINES, compute_chart_facts
from app.services.saju_engine import SajuEngine


def test_only_permissive_licenses_registered():
    for e in COMMERCIAL_SAFE_ENGINES:
        lic = (e.get("license") or "").upper()
        assert lic in ("MIT", "APACHE-2.0", "APACHE 2.0", "BSD", "BSD-2-CLAUSE", "BSD-3-CLAUSE")
        assert e.get("commercial_use") is True


def test_multi_engine_agreement_sample():
    facts = compute_chart_facts(date(1990, 8, 27), 8, 0)
    assert facts.day_master
    assert facts.year.stem and facts.day.branch
    ok = [e for e in facts.engines if e.ok]
    assert len(ok) >= 1
    # When both installed, expect agreement on this well-known sample
    if len(ok) >= 2:
        assert facts.agreement is True
        assert ok[0].signature() == ok[1].signature()


def test_saju_result_includes_chart_facts():
    r = SajuEngine().calculate(date(1990, 8, 27), 8, 0, "male")
    assert r.chart_facts is not None
    assert r.chart_facts.get("licenses")
    assert r.day_master == r.chart_facts.get("day_master")
