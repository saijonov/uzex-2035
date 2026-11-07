import pytest

from niyat.catalog import freight_per_tonne
from niyat.clearing import Intent, Offer, clear
from niyat.regions import distance_km


def offer(id="o1", region="tashkent_city", capacity=100, ask=900_000, product="cement_325"):
    return Offer(id, f"Seller {id}", region, product, capacity, ask)


def intent(
    id="b1", region="tashkent_city", quantity=10, limit=1_200_000, deadline=7, product="cement_325"
):
    return Intent(id, f"Buyer {id}", region, product, quantity, limit, deadline)


def freight(a, b):
    return freight_per_tonne(distance_km(a, b))


def test_enough_supply_price_is_ask_plus_delivery():
    result = clear([offer()], [intent()])
    fill = result.fills["b1"]
    assert fill.reason == "filled"
    assert fill.filled == 10
    assert fill.price == pytest.approx(900_000 + freight("tashkent_city", "tashkent_city"))
    assert result.plant_prices["o1"] == pytest.approx(900_000)


def test_scarcity_gives_cement_to_the_higher_limit_at_the_lowest_clearing_price():
    result = clear(
        [offer(capacity=10)],
        [intent("b1", limit=1_300_000), intent("b2", limit=1_100_000)],
    )
    winner, loser = result.fills["b1"], result.fills["b2"]
    assert winner.filled == 10 and loser.filled == 0
    assert loser.reason == "price_above_limit"
    assert winner.price == pytest.approx(1_100_000)
    assert result.seller_rents["o1"] == pytest.approx(
        1_100_000 - 900_000 - freight("tashkent_city", "tashkent_city")
    )


def test_raising_your_limit_does_not_raise_your_price_when_supply_is_enough():
    low = clear([offer(capacity=100)], [intent(limit=1_100_000)]).fills["b1"].price
    high = clear([offer(capacity=100)], [intent(limit=2_000_000)]).fills["b1"].price
    assert low == pytest.approx(high)


def test_far_buyer_pays_more_by_exactly_the_extra_delivery():
    result = clear(
        [offer(capacity=500)],
        [intent("near", region="tashkent_city"), intent("far", region="kashkadarya")],
    )
    near, far = result.fills["near"], result.fills["far"]
    assert near.reason == far.reason == "filled"
    assert far.price - near.price == pytest.approx(
        freight("tashkent_city", "kashkadarya") - freight("tashkent_city", "tashkent_city")
    )


def test_tight_deadline_excludes_far_plants():
    result = clear([offer(region="karakalpakstan")], [intent(region="surkhandarya", deadline=1)])
    assert result.fills["b1"].reason == "deadline"
    assert result.fills["b1"].filled == 0


def test_cheaper_nearby_plant_wins():
    result = clear(
        [
            offer("far", region="karakalpakstan", ask=850_000),
            offer("near", region="samarkand", ask=950_000),
        ],
        [intent(region="samarkand", limit=1_500_000)],
    )
    assert [a.offer_id for a in result.fills["b1"].allocations] == ["near"]


def test_money_balances_buyers_pay_sellers_and_carriers():
    offers = [
        offer("a", capacity=30, ask=900_000),
        offer("b", region="samarkand", capacity=40, ask=880_000),
    ]
    intents = [
        intent("x", quantity=20, limit=1_250_000),
        intent("y", region="kashkadarya", quantity=25, limit=1_300_000),
        intent("z", region="jizzakh", quantity=30, limit=1_150_000),
    ]
    result = clear(offers, intents)
    paid = sum(f.filled * f.price for f in result.fills.values() if f.filled)
    received = sum(
        a.tonnes * (a.plant_price + a.freight) for f in result.fills.values() for a in f.allocations
    )
    assert paid == pytest.approx(received, rel=1e-9)


def test_whole_tonnes_in_whole_tonnes_out():
    offers = [offer("a", capacity=37), offer("b", region="samarkand", capacity=23, ask=870_000)]
    intents = [
        intent(str(k), region=r, quantity=q, limit=1_200_000 + 10_000 * k)
        for k, (r, q) in enumerate(
            [
                ("tashkent_city", 7),
                ("samarkand", 13),
                ("jizzakh", 9),
                ("kashkadarya", 21),
                ("navoi", 18),
            ]
        )
    ]
    result = clear(offers, intents)
    for fill in result.fills.values():
        assert fill.filled == pytest.approx(round(fill.filled))


def test_unknown_product_has_no_seller():
    result = clear([offer()], [intent(product="cement_425")])
    assert result.fills["b1"].reason == "no_seller"
    assert result.fills["b1"].price is None


def test_small_buyers_are_pooled_into_trucks():
    intents = [intent(str(k), region="kashkadarya", quantity=3) for k in range(6)]
    result = clear([offer(capacity=100)], intents)
    (shipment,) = result.shipments
    assert shipment.buyers == 6 and shipment.tonnes == 18 and shipment.trucks == 1
