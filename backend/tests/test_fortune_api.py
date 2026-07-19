"""Fortune API tests — mounts fortune router only (no DB lifespan)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import fortune

app = FastAPI()
app.include_router(fortune.router, prefix="/api/fortune", tags=["fortune"])
client = TestClient(app)


def test_saju_endpoint_ok():
    r = client.post(
        "/api/fortune/saju",
        json={
            "solar_date": "1990-05-15",
            "hour": 14,
            "minute": 30,
            "gender": "male",
            "time_unknown": False,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "pillars" in body
    assert "daily" in body
    assert body["day_master"]
    assert body["input"]["time_assumed"] is False
    assert body["input"]["solar_date"] == "1990-05-15"
    assert body["pillars"]["year"]["stem"]
    assert body["pillars"]["hour"]["branch"]
    assert set(body["elements"]) == {"wood", "fire", "earth", "metal", "water"}
    assert "scores" in body["daily"]
    assert "lucky" in body["daily"]


def test_saju_time_unknown_assumes_noon():
    r = client.post(
        "/api/fortune/saju",
        json={
            "solar_date": "1990-05-15",
            "hour": 3,
            "minute": 0,
            "gender": "female",
            "time_unknown": True,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["input"]["time_assumed"] is True
    assert body["input"]["hour"] == 12
    assert body["input"]["minute"] == 0


def test_saju_validation_bad_hour():
    r = client.post(
        "/api/fortune/saju",
        json={
            "solar_date": "1990-05-15",
            "hour": 25,
            "minute": 0,
            "gender": "male",
            "time_unknown": False,
        },
    )
    assert r.status_code == 422


def test_saju_validation_bad_gender():
    r = client.post(
        "/api/fortune/saju",
        json={
            "solar_date": "1990-05-15",
            "hour": 12,
            "minute": 0,
            "gender": "other",
            "time_unknown": False,
        },
    )
    assert r.status_code == 422
