import json
import math
import re

from openai import OpenAI

from .settings import Settings

EXCHANGE_FEE = 0.0013
CLEARING_FEE = 0.0005
TRUCK_TONNES = 20

GOODS = {
    "cement": {
        "name": "Цемент М400",
        "words": ("цемент", "sement", "cement"),
        "index": 965_900,
        "month": "−3,2%",
        "year_low": 921_300,
        "year_high": 1_033_400,
        "sellers": 6,
        "seller": "Qabechuz Stroy",
        "city": "Самарканд",
        "price": 907_700,
        "deals": 214,
        "on_time": "97%",
        "shared": 18_000,
        "own": 36_000,
        "days": 1,
    },
    "flour": {
        "name": "Мука высшего сорта",
        "words": ("мук", "un ", "unga", "flour"),
        "index": 5_980_000,
        "month": "+1,5%",
        "year_low": 5_610_000,
        "year_high": 6_120_000,
        "sellers": 6,
        "seller": "Zarafshon Un",
        "city": "Самарканд",
        "price": 5_900_000,
        "deals": 156,
        "on_time": "95%",
        "shared": 18_000,
        "own": 36_000,
        "days": 1,
    },
    "sugar": {
        "name": "Сахар",
        "words": ("сахар", "shakar", "sugar"),
        "index": 15_800_000,
        "month": "+1,7%",
        "year_low": 14_900_000,
        "year_high": 16_100_000,
        "sellers": 4,
        "seller": "Shirin Savdo",
        "city": "Ургенч",
        "price": 15_650_000,
        "deals": 98,
        "on_time": "93%",
        "shared": 40_000,
        "own": 80_000,
        "days": 3,
    },
    "rebar": {
        "name": "Арматура",
        "words": ("арматур", "armatura", "rebar"),
        "index": 12_200_000,
        "month": "+0,8%",
        "year_low": 11_700_000,
        "year_high": 12_650_000,
        "sellers": 6,
        "seller": "Temir Qurilish",
        "city": "Бекабад",
        "price": 12_050_000,
        "deals": 187,
        "on_time": "96%",
        "shared": 8_000,
        "own": 16_000,
        "days": 1,
    },
}

RULES = (
    "Доставка в Ташкент. Общая машина дешевле в 2 раза; если за 2 дня не наберётся, едет отдельно без доплаты. "
    "Комиссия биржи 0,13% и клиринг 0,05% от стоимости товара. Деньги замораживаются на бирже и уходят "
    "продавцу только после приёмки груза; если груз плохой, его проверяет инспектор. Оплата Click, Payme "
    "или счёт фирмы, подтверждение через MyID. Договор и счёт-фактура появляются в заказе. "
    "Есть функция «Купить, когда подешевеет»: цель, тонны и срок; деньги списываются только при покупке. "
    "Брокер, ЭЦП и поездки не нужны: сделку проводит UzCom как член биржи."
)

INSTRUCTIONS = (
    "Ты AI-брокер в приложении UzCom для покупки товаров на бирже UZEX. Ты делаешь работу брокера: "
    "советуешь, когда и что выгодно купить, объясняешь правила, проверяешь продавцов и цены, готовишь заказ. "
    "Отвечай на языке покупателя (русский или узбекский), коротко: 1–3 предложения, просто, без жаргона. "
    "Суммы пиши с пробелами между тысячами: «сум» по-русски, «soʻm» по-узбекски. Используй только данные ниже, "
    "не называй их демо-данными; если данных нет, "
    "скажи прямо. Не обещай рост или падение цены. Если покупатель просит купить или заказать и понятны "
    "товар и тонны, заполни order_good и order_tonnes, а в reply кратко скажи, что заказ собран и его нужно "
    "подтвердить. Иначе оставь их null.\n"
    f"Товары (цены за тонну): {json.dumps(GOODS, ensure_ascii=False)}\n"
    f"Правила: {RULES}"
)

TOOL = {
    "type": "function",
    "name": "answer",
    "description": "Reply to the buyer and, when they asked to buy, the order to prepare.",
    "strict": True,
    "parameters": {
        "type": "object",
        "additionalProperties": False,
        "required": ["reply", "order_good", "order_tonnes"],
        "properties": {
            "reply": {"type": "string"},
            "order_good": {"type": ["string", "null"], "enum": [*GOODS, None]},
            "order_tonnes": {"type": ["integer", "null"]},
        },
    },
}


def money(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def quote(good: str, tonnes: int) -> dict:
    g = GOODS[good]
    goods = tonnes * g["price"]
    delivery = tonnes * g["shared"]
    exchange = math.floor(goods * EXCHANGE_FEE)
    clearing = math.floor(goods * CLEARING_FEE)
    return {
        "good": good,
        "title": f"{g['name']}, {tonnes} тонн",
        "seller": f"Продавец {g['seller']}, {g['city']}, проверен биржей",
        "goods": money(goods),
        "delivery": money(delivery),
        "exchange": money(exchange),
        "clearing": money(clearing),
        "total": money(goods + delivery + exchange + clearing),
        "trucks": math.ceil(tonnes / TRUCK_TONNES),
        "days": g["days"],
    }


def find_good(text: str) -> str | None:
    return next((k for k, g in GOODS.items() if any(w in text for w in g["words"])), None)


def rules(text: str) -> tuple[str, str | None, int | None]:
    text = f" {text.lower()} "
    good = find_good(text)
    g = GOODS[good or "cement"]
    tonnes = re.search(r"(\d+)\s*(т\b|тонн|tonna|t\b)", text)
    if good and tonnes and re.search(r"закаж|купи|оформ|нужн|kerak|buyurtma|sotib", text):
        return (
            "Собрал заказ у лучшего продавца. Проверьте сумму и подтвердите.",
            good,
            int(tonnes[1]),
        )
    if re.search(r"провер|продав|tekshir|sotuvchi", text):
        diff = round((1 - g["price"] / g["index"]) * 100, 1)
        return (
            f"{g['seller']} проверен биржей: {g['deals']} сделок, {g['on_time']} вовремя. "
            f"Цена {money(g['price'])} сум на {str(diff).replace('.', ',')}% ниже средней на бирже.",
            None,
            None,
        )
    if re.search(r"документ|бумаг|hujjat", text):
        return (
            "Договор и счёт-фактура появятся в заказе сами. Брокер, ЭЦП и поездки не нужны.",
            None,
            None,
        )
    if re.search(r"комисс|сколько|komissiya|qancha", text):
        return (
            "Комиссия биржи 0,13% и клиринг 0,05%. Доставка в общей машине вдвое дешевле.",
            None,
            None,
        )
    if re.search(r"когда|выгод|цен|qachon|narx", text):
        return (
            f"{g['name']} сейчас {money(g['index'])} сум за тонну, за месяц {g['month']}. "
            f"Минимум за год {money(g['year_low'])}. Можно купить сейчас или включить «Купить, когда подешевеет».",
            None,
            None,
        )
    return (
        "Я подскажу, когда выгодно купить, проверю продавца и цену и соберу заказ. "
        "Например: «Закажи 10 тонн цемента».",
        None,
        None,
    )


def ask_model(messages: list[dict], settings: Settings) -> tuple[str, str | None, int | None]:
    client = OpenAI(
        api_key=settings.openai_api_key.get_secret_value(), timeout=settings.ai_timeout_seconds
    )
    response = client.responses.create(
        model=settings.openai_model,
        reasoning={"effort": settings.openai_reasoning_effort},
        instructions=INSTRUCTIONS,
        input=[{"role": m["role"], "content": m["text"]} for m in messages],
        tools=[TOOL],
        tool_choice={"type": "function", "name": "answer"},
        store=False,
    )
    call = next(item for item in response.output if item.type == "function_call")
    fields = json.loads(call.arguments)
    return fields["reply"], fields["order_good"], fields["order_tonnes"]


def answer(messages: list[dict], settings: Settings, use_model: bool) -> dict:
    reply = good = tonnes = None
    if use_model:
        try:
            reply, good, tonnes = ask_model(messages, settings)
        except Exception:
            reply = None
    if reply is None:
        reply, good, tonnes = rules(messages[-1]["text"])
    order = quote(good, max(1, min(tonnes, 1000))) if good in GOODS and tonnes else None
    return {"reply": reply, "order": order}
