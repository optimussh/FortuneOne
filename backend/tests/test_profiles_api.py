"""Profiles API tests — auth required (no DB for 401)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import profiles

app = FastAPI()
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
client = TestClient(app)


def test_profiles_list_requires_auth():
    r = client.get("/api/profiles")
    assert r.status_code in (401, 403)


def test_profiles_create_requires_auth():
    r = client.post(
        "/api/profiles",
        json={
            "label": "나",
            "solar_date": "1990-05-15",
            "hour": 12,
            "minute": 0,
            "time_unknown": False,
            "gender": "male",
        },
    )
    assert r.status_code in (401, 403)


def test_profiles_get_requires_auth():
    r = client.get("/api/profiles/1")
    assert r.status_code in (401, 403)


def test_profiles_delete_requires_auth():
    r = client.delete("/api/profiles/1")
    assert r.status_code in (401, 403)


def test_profiles_saju_requires_auth():
    r = client.post("/api/profiles/1/saju")
    assert r.status_code in (401, 403)
