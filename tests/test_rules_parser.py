from datetime import date

import pytest

from niyat.draft import Draft
from niyat.rules_parser import parse

SATURDAY = date(2026, 11, 7)


def test_uzbek_sentence_with_everything():
    d = parse(
        "Qarshida uy quryapman, juma kunigacha 3 tonna M400 sement kerak, tonnasi 1,1 mln dan oshmasin",
        SATURDAY,
    )
    assert d.product == "cement_325"
    assert d.quantity == 3
    assert d.region == "kashkadarya"
    assert d.deadline_days == 6
    assert d.limit == pytest.approx(1_100_000)


def test_russian_bags_and_total_budget():
    d = parse("Нужно 100 мешков цемента М500 в Самарканд, бюджет 6 млн, за 5 дней", SATURDAY)
    assert d.product == "cement_425"
    assert d.quantity == pytest.approx(5)
    assert d.region == "samarkand"
    assert d.deadline_days == 5
    assert d.budget == pytest.approx(6_000_000)
    merged = Draft().merge(d)
    assert merged.limit == pytest.approx(1_200_000)


def test_cement_without_grade_asks_for_grade():
    d = Draft().merge(parse("Toshkentga 10 tonna sement kerak", SATURDAY))
    assert d.cement and d.product is None
    assert d.missing() == ["product", "limit"]


def test_restricted_goods_are_detected():
    assert parse("AI-80 benzin 20 tonna kerak", SATURDAY).restricted == "ai80"
    assert parse("Нужна пшеница 30 тонн", SATURDAY).restricted == "wheat"


def test_merge_keeps_earlier_answers():
    first = Draft().merge(parse("M400 sement 5 tonna", SATURDAY))
    second = first.merge(parse("Namanganga", SATURDAY))
    assert (second.product, second.quantity, second.region) == ("cement_325", 5, "namangan")
