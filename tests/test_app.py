import re

import pytest
from fastapi.testclient import TestClient

from uzcom import broker
from uzcom.app import create_app
from uzcom.settings import Settings

client = TestClient(create_app(Settings(openai_api_key="")))
SCREENS = {
    "Y1Home",
    "Y2Product",
    "N1Checkout",
    "N2Success",
    "N5AutoBuy",
    "Y3Orders",
    "Y4Track",
    "N3Details",
    "N4Arrived",
    "N6Assistant",
}


def ask(text: str, app_client: TestClient = client) -> dict:
    response = app_client.post("/api/ai", json={"messages": [{"role": "user", "text": text}]})
    assert response.status_code == 200
    return response.json()


def test_page_has_every_screen():
    page = client.get("/")
    assert page.status_code == 200
    assert "<title>UzCom</title>" in page.text
    assert set(re.findall(r'<template id="(\w+)">', page.text)) == SCREENS


def test_links_open_screens():
    links = set(re.findall(r'href="#(\w*)"', client.get("/").text))
    assert links == SCREENS


def test_files_load_without_cache():
    images = set(re.findall(r'src="(/img/[\w-]+\.png)"', client.get("/").text))
    assert len(images) == 3
    for path in {"/app.css", "/app.js", *images}:
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.headers["cache-control"] == "no-cache"


def test_order_matches_the_checkout_screen():
    order = ask("Закажи 10 тонн цемента")["order"]
    assert order["title"] == "Цемент М400, 10 тонн"
    assert order["goods"] == "9 077 000"
    assert order["delivery"] == "180 000"
    assert order["exchange"] == "11 800"
    assert order["clearing"] == "4 538"
    assert order["total"] == "9 273 338"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Проверь продавца цемента", "Qabechuz Stroy"),
        ("Когда выгодно купить сахар?", "Сахар сейчас 15 800 000"),
        ("Какие документы нужны?", "счёт-фактура"),
        ("Привет", "Закажи 10 тонн цемента"),
    ],
)
def test_rules_answer_without_the_model(text, expected):
    result = ask(text)
    assert expected in result["reply"]
    assert result["order"] is None


def test_model_failure_falls_back_to_rules(monkeypatch):
    def broken(messages, settings):
        raise TimeoutError

    monkeypatch.setattr(broker, "ask_model", broken)
    keyed = TestClient(create_app(Settings(openai_api_key="test")))
    assert ask("Нужно 5 тонн сахара", keyed)["order"]["title"] == "Сахар, 5 тонн"


def test_model_order_is_priced_by_the_server(monkeypatch):
    monkeypatch.setattr(broker, "ask_model", lambda messages, settings: ("Собрал.", "rebar", 3))
    keyed = TestClient(create_app(Settings(openai_api_key="test")))
    result = ask("3 tonna armatura kerak", keyed)
    assert result["reply"] == "Собрал."
    assert result["order"]["total"] == "36 239 070"
