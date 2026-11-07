from datetime import date

import pytest

from niyat.exchange import Exchange
from niyat.intake import Intake
from niyat.settings import Settings


@pytest.fixture
def intake():
    return Intake(
        Exchange(), Settings(_env_file=None, openai_api_key=""), today=lambda: date(2026, 11, 7)
    )


def test_dialogue_asks_one_thing_at_a_time_then_shows_a_card(intake):
    r = intake.handle("s", "Qarshiga sement kerak", "uz")
    assert r["source"] == "rules"
    assert "M400" in r["question"] and r["card"] is None
    r = intake.handle("s", "M400, 60 qop", "uz")
    assert r["draft"]["quantity"] == 3
    assert "so‘m" in r["question"]
    r = intake.handle("s", "tonnasi 1,2 mln", "uz")
    assert r["question"] is None
    assert r["card"]["quantity"] == 3 and r["card"]["deadline_days"] == 7
    assert r["can_submit"]
    intent_id = intake.submit("s")
    assert intake.exchange.live[intent_id].status == "waiting"


def test_restricted_goods_are_blocked_without_questions(intake):
    r = intake.handle("s", "AI-80 benzin 10 tonna Toshkentga kerak", "uz")
    assert r["question"] is None and not r["can_submit"]
    assert r["notices"][0]["code"] == "restricted"


def test_russian_flow_and_low_limit_warning(intake):
    r = intake.handle("s", "Нужно 5 тонн цемента М400 в Самарканд, за тонну 500 тыс", "ru")
    assert r["lang"] == "ru"
    assert r["card"] is not None
    assert any(n["code"] == "low" for n in r["notices"])


def test_submit_refuses_an_incomplete_draft(intake):
    intake.handle("s", "sement kerak", "uz")
    with pytest.raises(ValueError):
        intake.submit("s")
