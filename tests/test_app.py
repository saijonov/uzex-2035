import re

from fastapi.testclient import TestClient

from uzcom.app import app

client = TestClient(app)
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
}


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
