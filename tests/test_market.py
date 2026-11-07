from pathlib import Path

import pytest

from bozor.goods import CLEARING_FEE, EXCHANGE_FEE, FREIGHT_PER_TONNE_KM
from bozor.market import Market

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="module")
def market() -> Market:
    return Market(DATA)


def test_sugar_needs_several_sellers(market):
    plan = market.plan("sugar", 10, "samarkand")
    assert plan["filled"] == 10 and plan["ready"]
    assert len(plan["parts"]) >= 3
    assert max(p["tonnes"] for p in plan["parts"]) < 10


def test_parts_are_cheapest_delivered_first(market):
    plan = market.plan("sugar", 10, "samarkand")
    used = [p["price"] + p["freight"] for p in plan["parts"]]
    assert used == sorted(used)
    unused = [
        o
        for o in market.offers("sugar", "samarkand")
        if o["id"] not in {p["seller"]["id"] for p in plan["parts"]}
    ]
    assert all(o["delivered"] >= used[-1] for o in unused)


def test_short_supply_with_all_or_nothing_is_not_ready(market):
    stock = sum(o["available"] for o in market.offers("sugar", "bukhara"))
    whole = market.plan("sugar", stock + 5, "bukhara", whole=True)
    partial = market.plan("sugar", stock + 5, "bukhara")
    assert whole["filled"] == stock and whole["short"] == 5 and not whole["ready"]
    assert partial["ready"] and partial["filled"] == stock


def test_money_adds_up(market):
    plan = market.plan("cement", 25, "khorezm")
    cost = sum(p["tonnes"] * p["price"] for p in plan["parts"])
    delivery = sum(p["tonnes"] * p["freight"] for p in plan["parts"])
    assert plan["cost"] == cost and plan["delivery"] == delivery
    assert plan["total"] == cost + delivery + round(cost * EXCHANGE_FEE) + round(
        cost * CLEARING_FEE
    )


def test_freight_follows_road_distance(market):
    offer = market.offers("sugar", "surkhandarya")[0]
    assert offer["freight"] == round(offer["km"] * FREIGHT_PER_TONNE_KM, -2)
    assert offer["days"] == 1 + offer["km"] // 450


def test_route_runs_from_seller_to_buyer(market):
    there, back = market.route("navoi", "andijan"), market.route("andijan", "navoi")
    assert there["km"] == back["km"]
    assert there["line"][0] == back["line"][-1]
    assert abs(there["line"][0][0] - 40.103) < 0.1 and abs(there["line"][-1][1] - 72.344) < 0.1


def test_one_seller_plan(market):
    seller = market.offers("rice", "tashkent_city")[-1]
    plan = market.plan("rice", 2, "tashkent_city", seller=seller["id"])
    assert [p["seller"]["id"] for p in plan["parts"]] == [seller["id"]]
