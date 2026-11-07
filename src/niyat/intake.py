import logging
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta

from niyat.ai_intake import ai_parse
from niyat.draft import Draft
from niyat.exchange import FEE_RATE, Exchange
from niyat.explain import money, product_name, region_name
from niyat.guardian import check
from niyat.rules_parser import parse
from niyat.settings import Settings

logger = logging.getLogger(__name__)

DEFAULT_DEADLINE = 7

QUESTIONS = {
    "uz": {
        "product": "Qaysi markali sement kerak: M400 (32,5) yoki M500 (42,5)? Bilmasangiz, uy qurish uchun odatda M400 yetadi.",
        "product_any": "Nima sotib olmoqchisiz? Hozircha pilotda sement bor: M400 yoki M500.",
        "quantity": "Qancha kerak? Tonnada yoki qopda yozing (1 qop = 50 kg).",
        "region": "Qaysi shahar yoki tumanga yetkazib berish kerak?",
        "limit": "Tonnasi uchun eng ko‘pi bilan qancha to‘lay olasiz? Hozir {region}da bozor narxi taxminan {ref} (yetkazib berish bilan).",
        "limit_plain": "Tonnasi uchun eng ko‘pi bilan qancha to‘lay olasiz?",
        "ready": "Hammasi tayyor. Tekshirib, tasdiqlang.",
    },
    "ru": {
        "product": "Какая марка цемента нужна: М400 (32,5) или М500 (42,5)? Если не знаете — для дома обычно хватает М400.",
        "product_any": "Что хотите купить? В пилоте пока цемент: М400 или М500.",
        "quantity": "Сколько нужно? Напишите в тоннах или мешках (1 мешок = 50 кг).",
        "region": "В какой город или район доставить?",
        "limit": "Сколько максимум готовы платить за тонну? Сейчас в регионе «{region}» рынок около {ref} с доставкой.",
        "limit_plain": "Сколько максимум готовы платить за тонну?",
        "ready": "Всё готово. Проверьте и подтвердите.",
    },
}


@dataclass
class Session:
    id: str
    lang: str = "uz"
    draft: Draft = field(default_factory=Draft)
    history: list[dict] = field(default_factory=list)


def guess_lang(text: str, fallback: str) -> str:
    cyr = sum(1 for ch in text if "а" <= ch.lower() <= "я" or ch in "ёЁ")
    uz_cyr = any(ch in text for ch in "ўқғҳЎҚҒҲ")
    if cyr > 3 and not uz_cyr:
        return "ru"
    return fallback


class Intake:
    def __init__(self, exchange: Exchange, settings: Settings, today=date.today):
        self.exchange = exchange
        self.settings = settings
        self.today = today
        self.sessions: dict[str, Session] = {}

    def session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(session_id)
        return self.sessions[session_id]

    def understand(self, message: str, previous: Draft) -> tuple[Draft, str]:
        rules = parse(message, self.today())
        if self.settings.openai_api_key.get_secret_value():
            try:
                update = ai_parse(message, previous, self.settings, self.today())
                return replace(update, restricted=rules.restricted), "ai"
            except Exception as error:
                logger.warning("AI intake failed, using rules: %s", error)
        return rules, "rules"

    def handle(self, session_id: str, message: str, lang: str = "uz") -> dict:
        s = self.session(session_id)
        s.lang = guess_lang(message, lang) if lang not in ("uz", "ru") else lang
        update, source = self.understand(message, s.draft)
        s.draft = s.draft.merge(update)
        if update.restricted:
            s.draft = replace(s.draft, restricted=update.restricted)
        s.history.append({"role": "user", "text": message})
        reply = self.reply(s)
        reply["source"] = source
        s.history.append(
            {"role": "assistant", "text": reply["question"] or QUESTIONS[s.lang]["ready"]}
        )
        return reply

    def reply(self, s: Session) -> dict:
        q = QUESTIONS[s.lang]
        draft = s.draft
        notices = check(draft, self.exchange, s.id, s.lang)
        blocked = any(n["level"] == "block" for n in notices)
        question = None
        missing = draft.missing()
        stopped = blocked and bool(draft.restricted or (draft.other_product and not draft.product))
        if missing and not stopped:
            first = missing[0]
            if first == "product":
                question = q["product"] if draft.cement else q["product_any"]
            elif first == "limit":
                ref = (
                    self.exchange.reference_price(draft.region, draft.product)
                    if draft.region and draft.product
                    else None
                )
                question = (
                    q["limit"].format(
                        region=region_name(draft.region, s.lang), ref=money(ref, s.lang)
                    )
                    if ref
                    else q["limit_plain"]
                )
            else:
                question = q[first]
        card = None if missing or stopped else self.card(s)
        return {
            "draft": draft.to_dict(),
            "question": question,
            "card": card,
            "notices": notices,
            "can_submit": card is not None and not blocked,
            "lang": s.lang,
        }

    def card(self, s: Session) -> dict:
        d = s.draft
        days = d.deadline_days or DEFAULT_DEADLINE
        hold = d.quantity * d.limit * (1 + FEE_RATE)
        ref = self.exchange.reference_price(d.region, d.product)
        return {
            "product": product_name(d.product, s.lang),
            "quantity": d.quantity,
            "bags": round(d.quantity / 0.05),
            "region": region_name(d.region, s.lang),
            "deadline_days": days,
            "deadline_date": (
                datetime.combine(self.today(), datetime.min.time()) + timedelta(days=days)
            ).strftime("%d.%m.%Y"),
            "limit": d.limit,
            "limit_text": money(d.limit, s.lang),
            "hold": round(hold, 2),
            "hold_text": money(hold, s.lang),
            "reference": ref,
            "reference_text": money(ref, s.lang) if ref else None,
            "next_round": self.exchange.next_round(),
        }

    def submit(self, session_id: str) -> str:
        s = self.session(session_id)
        reply = self.reply(s)
        if not reply["can_submit"]:
            raise ValueError("not_ready")
        d = s.draft
        live = self.exchange.submit(
            session_id,
            d.region,
            d.product,
            d.quantity,
            d.limit,
            d.deadline_days or DEFAULT_DEADLINE,
        )
        s.draft = Draft()
        return live.intent.id

    def reset(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)
