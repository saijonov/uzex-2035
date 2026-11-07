import re
from datetime import date

from niyat.catalog import RESTRICTED
from niyat.draft import Draft
from niyat.regions import find_region, normalize

BAG_TONNES = 0.05

WEEKDAYS = {
    0: ("dushanba", "понедельник"),
    1: ("seshanba", "вторник"),
    2: ("chorshanba", "сред"),
    3: ("payshanba", "четверг"),
    4: ("juma", "пятниц"),
    5: ("shanba", "суббот"),
    6: ("yakshanba", "воскресен"),
}

NUMBER = r"(\d+(?:[.,]\d+)?)"


def to_float(text: str) -> float:
    return float(text.replace(",", ".").replace(" ", ""))


def parse_product(t: str) -> tuple[str | None, bool]:
    cement = bool(re.search(r"sement|цемент|semen", t))
    if re.search(r"[mм]\s*-?\s*500|42[.,]5|\b500\s*mark", t):
        return "cement_425", True
    if re.search(r"[mм]\s*-?\s*400|32[.,]5|\b400\s*mark", t):
        return "cement_325", True
    return None, cement


def parse_quantity(t: str) -> float | None:
    bags = re.search(NUMBER + r"\s*(?:ta\s*)?(?:qop|мешк|мешок|qopi)", t)
    if bags:
        return round(to_float(bags.group(1)) * BAG_TONNES, 3)
    tonnes = re.search(NUMBER + r"\s*(?:tonna|тонн|tn\b|t\b|т\b)", t)
    if tonnes:
        return to_float(tonnes.group(1))
    return None


COMPOUND = re.compile(NUMBER + r"\s*(?:mln|млн)\s*(\d+)\s*(?:ming|тыс)")


def parse_money(t: str, bare: bool = False) -> list[tuple[float, bool]]:
    found = []
    t = COMPOUND.sub(
        lambda m: f"{to_float(m.group(1)) * 1_000_000 + int(m.group(2)) * 1_000:.0f} so'm", t
    )
    for m in re.finditer(NUMBER + r"\s*(mln|млн|million|миллион|ming|тыс|k\b)?", t):
        raw, unit = m.group(1), m.group(2)
        tail = t[m.end() : m.end() + 25]
        if unit is None and not bare and not re.match(r"\s*(so'm|сум|sum|so‘m)", tail):
            continue
        value = to_float(raw)
        if unit in ("mln", "млн", "million", "миллион"):
            value *= 1_000_000
        elif unit in ("ming", "тыс", "k"):
            value *= 1_000
        if value < 10_000:
            continue
        context = t[max(0, m.start() - 25) : m.end() + 25]
        per_tonne = bool(re.search(r"tonnasi|tonnaga|har tonna|за тонну|за т\b|/t|/т", context))
        found.append((value, per_tonne))
    return found


def parse_deadline(t: str, today: date) -> int | None:
    m = re.search(r"(\d+)\s*(?:kun|дн|день|дней)", t)
    if m:
        return int(m.group(1))
    if re.search(r"ertaga|завтра", t):
        return 1
    m = re.search(r"(\d+)\s*(?:hafta|недел)", t)
    if m:
        return 7 * int(m.group(1))
    if re.search(r"hafta|недел", t):
        return 7
    for weekday, names in WEEKDAYS.items():
        if any(n in t for n in names):
            days = (weekday - today.weekday()) % 7
            return days or 7
    return None


def parse_restricted(t: str) -> str | None:
    for r in RESTRICTED:
        if any(k in t for k in r.keywords):
            return r.id
    return None


def parse(text: str, today: date | None = None, asked: str | None = None) -> Draft:
    today = today or date.today()
    t = normalize(text)
    product, cement = parse_product(t)
    quantity = parse_quantity(t)
    if quantity is None and asked == "quantity":
        bare = re.search(NUMBER, t)
        quantity = to_float(bare.group(1)) if bare else None
    limit = budget = None
    total = bool(re.search(r"hammasi|jami|всего|итого|бюджет|byudjet", t))
    for value, per_tonne in parse_money(t, bare=asked == "limit"):
        if per_tonne or (not total and (asked == "limit" or value < 3_000_000)):
            limit = value
        else:
            budget = value
    restricted = parse_restricted(t)
    other = None
    if (
        not cement
        and restricted is None
        and re.search(r"sotib ol|kerak|купить|нужн|нужен", t)
        and quantity
    ):
        other = text.strip()[:80]
    return Draft(
        product=product,
        quantity=quantity,
        region=find_region(text),
        deadline_days=parse_deadline(t, today),
        limit=limit,
        budget=budget,
        cement=cement,
        other_product=other,
        restricted=restricted,
    )
