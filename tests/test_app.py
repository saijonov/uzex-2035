from fastapi.testclient import TestClient

from niyat.app import create_app
from niyat.settings import Settings


def client():
    return TestClient(create_app(Settings(_env_file=None, openai_api_key="")))


def test_full_buyer_flow_through_the_api():
    c = client()
    r = c.post(
        "/api/chat",
        json={
            "session": "s1",
            "message": "Qarshiga 3 tonna M400 sement, tonnasi 1,6 mln",
            "lang": "uz",
        },
    ).json()
    assert r["can_submit"] and r["card"]["quantity"] == 3
    submitted = c.post("/api/submit", json={"session": "s1", "lang": "uz"}).json()
    assert submitted["intent"]["status"] == "waiting"
    assert c.get("/api/market").json()["waiting_live"] == 1
    assert c.post("/api/round").json()["round"] == 1
    mine = c.get("/api/intents", params={"session": "s1"}).json()["intents"]
    assert mine[0]["status"] == "matched"
    assert mine[0]["explanation"]["lines"]
    done = c.post(f"/api/intents/{mine[0]['id']}/delivered").json()
    assert done["intent"]["status"] == "delivered"


def test_market_view_after_a_round_has_prices_and_a_curve():
    c = client()
    c.post("/api/round")
    m = c.get("/api/market", params={"lang": "ru", "region": "tashkent_city"}).json()
    assert len(m["zones"]) == 14
    assert m["stats"]["traded"] > 0
    assert m["curve"]["supply"] and m["curve"]["price"]


def test_pages_are_served():
    c = client()
    assert c.get("/").status_code == 200
    assert c.get("/market").status_code == 200
