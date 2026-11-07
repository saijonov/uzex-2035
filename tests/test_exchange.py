import pytest

from niyat.exchange import FEE_RATE, START_BALANCE, Exchange
from niyat.explain import explain


@pytest.fixture
def exchange():
    return Exchange()


def test_generous_limit_buys_and_money_balances(exchange):
    live = exchange.submit("me", "kashkadarya", "cement_325", 3, 1_600_000, 7)
    account = exchange.accounts["me"]
    assert account.held == pytest.approx(3 * 1_600_000 * (1 + FEE_RATE))
    record = exchange.clear_round()
    assert live.status == "matched"
    assert live.fill.filled == 3
    assert live.cost == pytest.approx(3 * live.fill.price)
    assert account.held == pytest.approx(0)
    assert account.balance == pytest.approx(START_BALANCE - live.cost - live.fees)
    assert live.refund == pytest.approx(live.reserved - live.cost - live.fees)
    assert live.intent.id in record.live_ids
    text = explain(live, record, "uz")
    assert "3 t" in text["headline"] and text["lines"]


def test_low_limit_is_refunded_with_a_suggestion(exchange):
    live = exchange.submit("me", "kashkadarya", "cement_325", 3, 300_000, 7)
    record = exchange.clear_round()
    assert live.status == "unmatched"
    assert live.cost == 0 and live.refund == pytest.approx(live.reserved)
    assert exchange.accounts["me"].balance == pytest.approx(START_BALANCE)
    assert explain(live, record, "ru")["lines"]


def test_not_enough_money_is_refused(exchange):
    with pytest.raises(ValueError, match="insufficient_funds"):
        exchange.submit("me", "tashkent_city", "cement_325", 100, 1_000_000, 7)


def test_cancel_releases_the_hold(exchange):
    live = exchange.submit("me", "tashkent_city", "cement_325", 2, 1_200_000, 7)
    exchange.cancel(live.intent.id)
    assert exchange.accounts["me"].held == pytest.approx(0)
    assert live.status == "cancelled"


def test_delivery_confirmation_only_after_a_match(exchange):
    live = exchange.submit("me", "tashkent_city", "cement_325", 2, 1_600_000, 7)
    with pytest.raises(ValueError):
        exchange.confirm_delivery(live.intent.id)
    exchange.clear_round()
    exchange.confirm_delivery(live.intent.id)
    assert live.status == "delivered"


def test_rounds_are_numbered_and_reference_prices_follow_the_last_round(exchange):
    first = exchange.clear_round()
    second = exchange.clear_round()
    assert (first.number, second.number) == (1, 2)
    assert exchange.reference_price("tashkent_city", "cement_325") == pytest.approx(
        second.result.zone_prices[("tashkent_city", "cement_325")]
    )
