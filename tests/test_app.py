from fastapi.testclient import TestClient

from niyat.app import create_app
from niyat.settings import Settings


def client():
    return TestClient(create_app(Settings(_env_file=None, openai_api_key="", warmup_rounds=0)))


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


def test_trading_flow_buy_hold_sell_and_portfolio():
    c = TestClient(create_app(Settings(_env_file=None, openai_api_key="", warmup_rounds=3)))
    inst = c.get("/api/instruments").json()["instruments"]
    m400 = next(i for i in inst if i["id"] == "cement_325")
    assert len(m400["history"]) == 3 and m400["plants"]
    preview = c.post(
        "/api/order",
        json={
            "session": "t",
            "product": "cement_325",
            "tonnes": 5,
            "limit": 1_500_000,
            "preview": True,
        },
    ).json()
    assert not preview["submitted"] and any(n["code"] == "hold_info" for n in preview["notices"])
    placed = c.post(
        "/api/order",
        json={"session": "t", "product": "cement_325", "tonnes": 5, "limit": 1_500_000},
    ).json()
    assert placed["submitted"] and placed["intent"]["hold"]
    c.post("/api/round")
    folio = c.get("/api/portfolio", params={"session": "t"}).json()
    assert folio["holdings"] and folio["intents"][0]["status"] == "matched"
    h = folio["holdings"][0]
    sold = c.post(
        "/api/sell",
        json={"session": "t", "receipt": h["id"], "tonnes": h["free"], "min_price": 400_000},
    ).json()
    assert sold["sell"]["status"] == "waiting"
    c.post(
        "/api/alerts",
        json={"session": "t", "product": "cement_325", "direction": "above", "price": 1},
    )
    c.post("/api/round")
    folio = c.get("/api/portfolio", params={"session": "t", "lang": "ru"}).json()
    assert folio["sells"][0]["status"] == "sold"
    assert folio["alerts"][0]["status"] == "fired"


def test_order_without_money_is_blocked():
    c = client()
    r = c.post(
        "/api/order",
        json={"session": "p", "product": "cement_325", "tonnes": 100, "limit": 1_000_000},
    ).json()
    assert not r["submitted"] and r["notices"][0]["level"] == "block"
