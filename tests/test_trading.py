import pytest

from niyat.catalog import freight_per_tonne
from niyat.clearing import Intent, Offer, clear
from niyat.exchange import FEE_RATE, SELL_FEE_RATE, START_BALANCE, Exchange
from niyat.regions import distance_km


def test_holding_buyer_pays_the_plant_price_without_delivery():
    result = clear(
        [Offer("o", "Plant", "samarkand", "cement_325", 50, 900_000)],
        [Intent("h", "me", None, "cement_325", 5, 1_000_000, 0)],
    )
    fill = result.fills["h"]
    assert fill.filled == 5
    assert fill.price == pytest.approx(900_000)
    assert result.shipments == []


@pytest.fixture
def exchange():
    return Exchange()


def buy_and_hold(exchange, tonnes=5, limit=1_400_000):
    live = exchange.submit("me", None, "cement_325", tonnes, limit, 0)
    exchange.clear_round()
    assert live.status == "matched"
    return live


def test_buy_and_hold_creates_receipts_at_plants(exchange):
    live = buy_and_hold(exchange)
    receipts = [exchange.receipts[r] for r in live.receipts]
    assert sum(r.tonnes for r in receipts) == pytest.approx(5)
    assert all(r.status == "stored" for r in receipts)
    assert exchange.accounts["me"].balance == pytest.approx(
        START_BALANCE - live.cost * (1 + FEE_RATE)
    )
    rows = exchange.portfolio("me")
    assert rows and all(row["mark"] for row in rows)


def test_selling_a_receipt_pays_the_seller_after_the_round(exchange):
    live = buy_and_hold(exchange)
    receipt = exchange.receipts[live.receipts[0]]
    before = exchange.accounts["me"].balance
    order = exchange.sell("me", receipt.id, receipt.tonnes, 500_000)
    assert receipt.free == pytest.approx(0)
    exchange.clear_round()
    assert order.status == "sold"
    assert order.price >= 500_000
    assert exchange.accounts["me"].balance == pytest.approx(
        before + order.proceeds * (1 - SELL_FEE_RATE)
    )
    assert receipt.status == "sold"


def test_a_too_high_ask_stays_unsold_and_unlocks(exchange):
    live = buy_and_hold(exchange)
    receipt = exchange.receipts[live.receipts[0]]
    order = exchange.sell("me", receipt.id, receipt.tonnes, 50_000_000)
    exchange.clear_round()
    assert order.status == "unsold" and order.proceeds == 0
    assert receipt.free == pytest.approx(receipt.tonnes)


def test_cannot_sell_more_than_you_hold(exchange):
    live = buy_and_hold(exchange)
    receipt = exchange.receipts[live.receipts[0]]
    with pytest.raises(ValueError):
        exchange.sell("me", receipt.id, receipt.tonnes + 1, 900_000)
    with pytest.raises(ValueError):
        exchange.sell("someone", receipt.id, 1, 900_000)


def test_delivery_from_the_warehouse_charges_the_route(exchange):
    live = buy_and_hold(exchange)
    receipt = exchange.receipts[live.receipts[0]]
    before = exchange.accounts["me"].balance
    exchange.deliver("me", receipt.id, "kashkadarya")
    cost = freight_per_tonne(distance_km(receipt.region, "kashkadarya")) * receipt.tonnes
    assert exchange.accounts["me"].balance == pytest.approx(before - cost)
    assert receipt.status == "delivering" and receipt.eta


def test_warmup_builds_a_price_history():
    ex = Exchange(warmup=5)
    history = ex.history("cement_325")
    assert [h["round"] for h in history] == [1, 2, 3, 4, 5]
    assert all(h["price"] > 0 for h in history)
