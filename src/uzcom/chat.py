import json
import math
import re
from dataclasses import asdict, dataclass

from openai import OpenAI

from .goods import GOODS, RESTRICTED
from .market import Market
from .regions import REGIONS, find_region, normalize
from .settings import Settings

BAG_KG = 50
WHOLE_YES = r"hammasi bo'lsa|hammasini birdan|faqat hammasi|bittada hammasi|to'liq bo'lsa|все сразу|только все|целиком|только полностью"
WHOLE_NO = r"bori|borini|qancha bo'lsa|bor+icha|сколько есть|что есть"


@dataclass
class Draft:
    good: str | None = None
    tonnes: int | None = None
    region: str | None = None
    whole: bool = False
    restricted: str | None = None
    other: str | None = None
    price: int | None = None


def word_match(text: str, words: tuple[str, ...]) -> bool:
    return any(
        re.search(rf"(?<![\w']){re.escape(w)}" + (r"(?![\w'])" if len(w) <= 3 else ""), text)
        for w in words
    )


def rules(message: str, asked: str | None) -> dict:
    text = normalize(message)
    found: dict = {}
    good = next((g.id for g in GOODS.values() if word_match(text, g.words)), None)
    if good:
        found["good"] = good
    elif bad := next((r.id for r in RESTRICTED if word_match(text, r.words)), None):
        found["restricted"] = bad
    number = r"(\d+(?:[.,]\d+)?)"
    if m := re.search(number + r"\s*(?:qop|мешк|мешок)", text):
        found["tonnes"] = math.ceil(float(m.group(1).replace(",", ".")) * BAG_KG / 1000)
    elif m := re.search(number + r"\s*(?:kg|кг|kilo)", text):
        found["tonnes"] = max(1, math.ceil(float(m.group(1).replace(",", ".")) / 1000))
    elif m := re.search(number + r"\s*(?:t\b|tn\b|tonna|тонн|т\b)", text):
        found["tonnes"] = math.ceil(float(m.group(1).replace(",", ".")))
    elif asked == "tonnes" and (m := re.fullmatch(r"\s*" + number + r"\s*", text)):
        found["tonnes"] = math.ceil(float(m.group(1).replace(",", ".")))
    joined = re.sub(r"(?<=\d)[ \u00a0](?=\d{3}\b)", "", text)
    if m := re.search(number + r"\s*(?:mln|million|млн)", joined):
        found["price"] = round(float(m.group(1).replace(",", ".")) * 1_000_000)
    elif m := re.search(number + r"\s*(?:ming|минг|тыс)", joined):
        found["price"] = round(float(m.group(1).replace(",", ".")) * 1000)
    elif m := re.search(r"(?<![\d.,])(\d{5,})(?![\d.,])", joined):
        found["price"] = int(m.group(1))
    elif asked == "price" and (m := re.fullmatch(r"\s*(\d+)\s*", joined)):
        found["price"] = int(m.group(1)) * (1000 if int(m.group(1)) < 10_000 else 1)
    if region := find_region(text):
        found["region"] = region
    if re.search(WHOLE_YES, text):
        found["whole"] = True
    elif re.search(WHOLE_NO, text):
        found["whole"] = False
    return found


TOOL = {
    "type": "function",
    "name": "update_order",
    "description": "Fields of a commodity buy or sell request read from the user's message. Null when the message does not say it.",
    "strict": True,
    "parameters": {
        "type": "object",
        "additionalProperties": False,
        "required": ["good", "restricted", "other", "tonnes", "region", "whole", "price"],
        "properties": {
            "good": {
                "type": ["string", "null"],
                "enum": [*GOODS, None],
                "description": "; ".join(f"{g.id}={g.name}" for g in GOODS.values()),
            },
            "restricted": {
                "type": ["string", "null"],
                "enum": [r.id for r in RESTRICTED] + [None],
                "description": "; ".join(f"{r.id}={r.name}" for r in RESTRICTED)
                + ". Cottonseed oil is not cotton.",
            },
            "other": {
                "type": ["string", "null"],
                "description": "Name of a requested product that is in neither list, in Uzbek.",
            },
            "tonnes": {
                "type": ["number", "null"],
                "description": "Quantity in tonnes. One bag (qop, мешок) is 50 kg.",
            },
            "region": {
                "type": ["string", "null"],
                "enum": [*REGIONS, None],
                "description": "Delivery region for a buyer, warehouse region for a seller. "
                + "; ".join(f"{r.id}={r.name}, {r.city}" for r in REGIONS.values()),
            },
            "whole": {
                "type": ["boolean", "null"],
                "description": "True if the user wants all of it at once or nothing; false if a partial amount is fine.",
            },
            "price": {
                "type": ["number", "null"],
                "description": "Price per tonne in so'm if stated. '950 ming' is 950000, '1,2 mln' is 1200000.",
            },
        },
    },
}


def ai(
    message: str, draft: Draft, asked: str | None, settings: Settings, role: str = "buyer"
) -> dict:
    client = OpenAI(
        api_key=settings.openai_api_key.get_secret_value(), timeout=settings.ai_timeout_seconds
    )
    response = client.responses.create(
        model=settings.openai_model,
        reasoning={"effort": settings.openai_reasoning_effort},
        instructions=(
            f"Read a {role}'s message in Uzbek or Russian for a commodity marketplace and call update_order. "
            f"Current order: {json.dumps(asdict(draft))}. Last question asked: {asked or 'none'}. "
            "A bare number answers the last question."
        ),
        input=message,
        tools=[TOOL],
        tool_choice={"type": "function", "name": "update_order"},
        store=False,
    )
    call = next(item for item in response.output if item.type == "function_call")
    fields = json.loads(call.arguments)
    if fields["tonnes"] is not None:
        fields["tonnes"] = max(1, math.ceil(fields["tonnes"]))
    if fields["price"] is not None:
        fields["price"] = round(fields["price"])
    return {k: v for k, v in fields.items() if v is not None}


def money(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " so‘m"


def reply(draft: Draft, market: Market) -> tuple[str, str | None, dict | None]:
    if draft.restricted:
        r = next(r for r in RESTRICTED if r.id == draft.restricted)
        return f"{r.name} birjada {r.who} sotiladi. Bu ilovada uni sotib bo‘lmaydi.", None, None
    if not draft.good:
        if draft.other:
            return (
                f"«{draft.other}» hozircha demo bozorda yo‘q. Bor tovarlar: sement, armatura, shakar, un, guruch, yog‘ va boshqalar.",
                "good",
                None,
            )
        return "Qaysi tovar kerak? Masalan: sement, shakar, un yoki armatura.", "good", None
    name = GOODS[draft.good].name
    if not draft.tonnes:
        return f"{name} — necha tonna kerak?", "tonnes", None
    plan = market.plan(draft.good, draft.tonnes, draft.region, draft.whole)
    sellers = len(plan["parts"])
    if not sellers:
        return f"Hozir {name} sotuvchisi yo‘q.", None, plan
    if plan["short"] and draft.whole:
        text = f"Bozorda hozir faqat {plan['filled']} t {name.lower()} bor. Siz {draft.tonnes} tonnani birdan so‘radingiz. {plan['filled']} t olasizmi yoki kutamizmi?"
        return text, None, plan
    elif plan["short"]:
        text = (
            f"Bozorda hozir faqat {plan['filled']} t bor. Shuni {sellers} ta sotuvchidan yig‘dim."
        )
    elif sellers == 1:
        text = f"Bitta sotuvchida {draft.tonnes} t bor. Yetkazish bilan eng arzoni shu."
    else:
        text = f"Bitta sotuvchida {draft.tonnes} t yo‘q. {sellers} ta sotuvchidan yig‘dim — yetkazish bilan eng arzon yo‘l."
    return text + f" Jami: {money(plan['total'])}.", None, plan


def percent(value: float) -> str:
    return f"{value * 100:+.1f}%".replace(".", ",").replace("-", "−")


def listing_reply(draft: Draft, market: Market) -> tuple[str, str | None, dict | None]:
    if draft.restricted:
        r = next(r for r in RESTRICTED if r.id == draft.restricted)
        return f"{r.name} bu ilovada sotilmaydi: birjada u {r.who} sotiladi.", None, None
    if not draft.good:
        return "Nima sotasiz? Masalan: «50 t sement, 950 ming».", "good", None
    name, index = GOODS[draft.good].name, market.index(draft.good)
    if not draft.tonnes:
        return f"{name} — necha tonna sotasiz?", "tonnes", None
    if not draft.price:
        return f"1 tonnasini necha so‘mdan sotasiz? Bozorda o‘rtacha {money(index)}.", "price", None
    diff = round(draft.price / index - 1, 3)
    near = next((r for r in market.requests(draft.region) if r["good"] == draft.good), None)
    advice = (
        "Narx bozorga mos."
        if abs(diff) <= 0.05
        else "Bozordan qimmat, sotilishi sekin bo‘lishi mumkin."
        if diff > 0
        else "Bozordan ancha arzon, narxni ko‘tarsangiz ham sotiladi."
    )
    text = f"Bozor o‘rtachasi {money(index)}, sizniki {percent(diff)}. {advice}"
    if near:
        text += f" Eng yaqin talab: {near['city']}, {near['tonnes']} t."
    listing = {
        "good": draft.good,
        "good_name": name,
        "tonnes": draft.tonnes,
        "price": draft.price,
        "region": draft.region,
        "city": REGIONS[draft.region].city,
        "index": index,
        "diff": diff,
        "request": near,
    }
    return text, None, listing
