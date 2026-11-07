from pathlib import Path

from fastapi.testclient import TestClient

from bozor.app import create_app
from bozor.chat import rules
from bozor.settings import Settings

DATA = Path(__file__).resolve().parents[1] / "data"


def client() -> TestClient:
    return TestClient(create_app(Settings(openai_api_key="", data_dir=DATA)))


def test_reads_tonnes_bags_and_region():
    assert rules("Samarqandga 10 tonna shakar kerak", None) == {
        "good": "sugar",
        "tonnes": 10,
        "region": "samarkand",
    }
    assert rules("60 qop sement Qarshiga", None) == {
        "good": "cement",
        "tonnes": 3,
        "region": "kashkadarya",
    }
    assert rules("нужно 20 т муки в Наманган", None) == {
        "good": "flour",
        "tonnes": 20,
        "region": "namangan",
    }


def test_short_words_do_not_match_inside_other_words():
    assert "good" not in rules("uchun kerak", None)
    assert rules("12", "tonnes") == {"tonnes": 12}
    assert "tonnes" not in rules("12", None)


def test_cotton_is_refused_but_cottonseed_oil_is_not():
    assert rules("10 tonna paxta kerak", None)["restricted"] == "cotton"
    assert rules("paxta yog‘i 5 t", None)["good"] == "cottonseed_oil"
    assert rules("bug'doy uni 5 t", None)["good"] == "flour"


def test_all_or_nothing():
    assert rules("20 t sement, faqat hammasi bo'lsa", None)["whole"] is True


def test_chat_builds_a_split_order_without_ai():
    c = client()
    first = c.post("/api/chat", json={"message": "shakar kerak", "region": "samarkand"}).json()
    assert first["asked"] == "tonnes" and first["plan"] is None
    second = c.post(
        "/api/chat",
        json={"message": "10", "region": "samarkand", "draft": first["draft"], "asked": "tonnes"},
    ).json()
    assert second["plan"]["filled"] == 10 and len(second["plan"]["parts"]) >= 3
    assert "sotuvchidan yig‘dim" in second["reply"]


def test_chat_refuses_cotton():
    reply = (
        client()
        .post("/api/chat", json={"message": "10 tonna paxta kerak", "region": "tashkent_city"})
        .json()
    )
    assert reply["plan"] is None and "qayta ishlash" in reply["reply"]
    assert reply["draft"]["restricted"] is None


def test_market_endpoints():
    c = client()
    goods = c.get("/api/goods", params={"region": "tashkent_city"}).json()
    assert len(goods) == 12 and all(g["best"] > g["price"] * 0.8 for g in goods)
    detail = c.get("/api/goods/cement", params={"region": "tashkent_city"}).json()
    assert len(detail["weeks"]) == 52 and detail["offers"]
    assert c.get("/api/goods/cotton", params={"region": "tashkent_city"}).status_code == 404
    assert len(c.get("/api/demo", params={"region": "samarkand"}).json()) == 2


def test_reads_prices():
    assert rules("50 t sement, 950 ming", None)["price"] == 950_000
    assert rules("30 t guruch 23,5 mln", None)["price"] == 23_500_000
    assert rules("1 200 000 so'mdan", None)["price"] == 1_200_000
    assert rules("950", "price") == {"price": 950_000}


def test_seller_chat_makes_a_listing():
    c = client()
    first = c.post(
        "/api/chat", json={"message": "50 t sement sotaman", "region": "navoi", "role": "seller"}
    ).json()
    assert first["asked"] == "price" and "o‘rtacha" in first["reply"]
    second = c.post(
        "/api/chat",
        json={
            "message": "950 ming",
            "region": "navoi",
            "role": "seller",
            "draft": first["draft"],
            "asked": "price",
        },
    ).json()
    listing = second["listing"]
    assert listing["price"] == 950_000 and listing["tonnes"] == 50 and listing["city"] == "Navoiy"
    assert second["plan"] is None


def test_seller_endpoints():
    c = client()
    demand = c.post("/api/demand", json={"region": "navoi", "wants": []}).json()
    assert len(demand) == 24
    demo = c.get("/api/seller-demo", params={"region": "navoi"}).json()
    assert len(demo["deals"]) == 2 and demo["listings"]
    sale = c.post(
        "/api/sale",
        json={
            "good": "cement",
            "tonnes": 20,
            "price": 950000,
            "home": "navoi",
            "region": "samarkand",
        },
    ).json()
    assert sale["payout"] == 18_981_000
