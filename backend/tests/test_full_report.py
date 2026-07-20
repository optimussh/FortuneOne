from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import fortune
from app.services.saju_engine import SajuEngine
from app.services.saju_report import build_full_report

app = FastAPI()
app.include_router(fortune.router, prefix="/api/fortune")
client = TestClient(app)


def test_build_full_report_has_long_sections():
    r = SajuEngine().calculate(date(1990, 5, 15), 14, 30, "male")
    rep = build_full_report(r, date(1990, 5, 15), "male")
    assert rep["new_year_2026"]["year"] == 2026
    assert len(rep["daily"]["sections"]) >= 4
    assert len(rep["five_element"]["groups"]) == 3
    assert len(rep["life_reading"]["groups"]) == 4
    body = rep["life_reading"]["groups"][0]["sections"][0]["body"]
    assert len(body) > 80
    assert "tojeong" in rep
    assert len(rep["tojeong"]["months"]) == 12
    assert "mingshi" in rep


def test_full_report_endpoint():
    res = client.post(
        "/api/fortune/full-report",
        json={
            "solar_date": "1990-05-15",
            "hour": 14,
            "minute": 30,
            "gender": "male",
            "time_unknown": False,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "report" in data
    assert data["report"]["new_year_2026"]["year"] == 2026
    assert data["report"]["tojeong"]["year"] == 2026
    assert len(data["report"]["tojeong"]["months"]) == 12
