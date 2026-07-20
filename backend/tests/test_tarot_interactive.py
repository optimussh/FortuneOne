from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import fortune

app = FastAPI()
app.include_router(fortune.router, prefix="/api/fortune")
client = TestClient(app)


def test_shuffle_and_reveal():
    r = client.post(
        "/api/fortune/tarot/shuffle",
        json={"spread": "three", "question": "테스트"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["need"] == 3
    assert len(data["deck_face_down"]) == 18
    assert "card_id" not in data["deck_face_down"][0]
    slots = [d["slot_id"] for d in data["deck_face_down"][:3]]
    rev = client.post(
        "/api/fortune/tarot/reveal",
        json={"session_id": data["session_id"], "picked_slot_ids": slots},
    )
    assert rev.status_code == 200
    body = rev.json()
    assert len(body["cards"]) == 3
    assert body["cards"][0]["image_key"]
    assert body["cards"][0]["color"]
    assert body["cards"][0]["symbol"]


def test_topic_love():
    r = client.post(
        "/api/fortune/topic",
        json={
            "topic": "love",
            "solar_date": "1990-05-15",
            "hour": 12,
            "minute": 0,
            "gender": "female",
            "time_unknown": True,
        },
    )
    assert r.status_code == 200
    assert r.json()["score"] >= 0
    assert len(r.json()["sections"]) >= 3
