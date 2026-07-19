"""Product feature API tests (tarot, zodiac, affiliate, expanded saju)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import fortune

app = FastAPI()
app.include_router(fortune.router, prefix="/api/fortune", tags=["fortune"])
client = TestClient(app)


def test_saju_includes_yongsin_and_daeun():
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
    assert body["yongsin"] is not None
    assert body["yongsin"]["element"] in {"wood", "fire", "earth", "metal", "water"}
    assert len(body["daeun"]) >= 1
    assert len(body["lucky_items"]) >= 1
    assert body["weak_elements"]


def test_tarot_draw():
    r = client.post("/api/fortune/tarot", json={"count": 3, "question": "오늘 조언"})
    assert r.status_code == 200
    body = r.json()
    assert len(body["cards"]) == 3
    assert body["cards"][0]["name"]
    assert body["summary"]


def test_zodiac_today():
    r = client.get("/api/fortune/zodiac/today")
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 12


def test_compatibility():
    r = client.post(
        "/api/fortune/compatibility",
        json={
            "a": {"solar_date": "1990-05-15", "gender": "male", "time_unknown": True},
            "b": {"solar_date": "1992-08-20", "gender": "female", "time_unknown": True},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["score"] <= 100
    assert body["summary"]


def test_affiliate():
    r = client.get("/api/fortune/affiliate/recommendations?elements=water,metal")
    assert r.status_code == 200
    assert r.json()["items"]
