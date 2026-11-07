import hashlib
import json
import re
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uzcom.goods import GOODS
from uzcom.regions import REGISTRY

DEMO_STOCK = {"sugar": [5, 3, 3, 2]}

WEEKS = """
select strftime(date_trunc('week', deal_date), '%Y-%m-%d') as week, round(median(amount_uzs / mass_t), -2) as price
from registry
where product_family = $family and deal_date >= date '2025-11-03' and not is_cancelled and mass_t > 0
group by 1 order by 1
"""

SELLERS = """
select seller_name, seller_region,
       count(*) filter (where deal_date >= date '2026-01-01') as deals,
       median(amount_uzs / mass_t) filter (where deal_date >= date '2026-08-01') as recent,
       median(amount_uzs / mass_t) filter (where deal_date >= date '2026-01-01') as year,
       sum(mass_t) filter (where deal_date >= date '2026-01-01') as tonnes,
       median(mass_t) filter (where deal_date >= date '2026-01-01') as lot,
       avg(case when delivered_on <= delivery_due then 1.0 else 0.0 end)
         filter (where deal_date >= date '2026-01-01' and delivered_on is not null and delivery_due is not null) as on_time,
       min(year(deal_date)) as since,
       mode(product_name) filter (where deal_date >= date '2026-01-01') as product,
       mode(packaging) filter (where deal_date >= date '2026-01-01') as packaging,
       mode(warehouse_address) filter (where deal_date >= date '2026-01-01') as warehouse
from registry
where product_family = $family and not is_cancelled and mass_t > 0
group by all
having deals >= 20
order by tonnes desc
limit 6
"""

CYRILLIC = dict(
    zip(
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяўқғҳ",
        "a b v g d e yo j z i y k l m n o p r s t u f x ts ch sh sh ’ i _ e yu ya o‘ q g‘ h".split(
            " "
        ),
        strict=True,
    )
)
LEGAL = {
    "мчж": "MChJ",
    "mchj": "MChJ",
    "аж": "AJ",
    "aj": "AJ",
    "хк": "XK",
    "xk": "XK",
    "ок": "OK",
    "ok": "OK",
    "қк": "QK",
    "qk": "QK",
}
PACKAGING = {
    "в мешках по 50 кг": "qopda, 50 kg",
    "в мешках по 25 кг": "qopda, 25 kg",
    "в мешках": "qopda",
    "навалом": "to‘kma",
    "в бутылках": "butilkada",
    "в цистернах": "sisternada",
}


def latin(word: str) -> str:
    out = "".join(CYRILLIC.get(ch, ch) for ch in word.lower()).replace("_", "")
    return "ye" + out[1:] if word[:1].lower() == "е" else out


def tidy(name: str) -> str:
    name = re.sub(
        r"MAS[’'`ʼ]ULIYATI CHEKLANGAN JAMIYATI|МАСЪУЛИЯТИ ЧЕКЛАНГАН ЖАМИЯТИ",
        "MChJ",
        name,
        flags=re.I,
    )
    words = []
    for word in re.sub(r"[\"«»“”]", " ", name).split():
        key = word.lower()
        if key in LEGAL:
            words.append(LEGAL[key])
            continue
        words.append("-".join(part[:1].upper() + part[1:] for part in latin(word).split("-")))
    legal = [w for w in words if w in LEGAL.values()]
    return " ".join([w for w in words if w not in LEGAL.values()] + legal[:1])


def grade(text: str) -> str:
    t = text.lower()
    parts = []
    if m := re.search(r"цем\s*([ivх/а-я-]*)\s*(\d{2},\d)\s*н?", t):
        parts.append(f"ЦЕМ {m.group(1).upper()} {m.group(2)}Н".replace("  ", " "))
    if m := re.search(r"ø\s*(\d+)", t):
        parts.append(f"Ø{m.group(1)} mm")
    if "а500с" in t:
        parts.append("A500C")
    for pattern, label in (
        (r"г-(\d)", "G-{}"),
        (r"кс-(\d+)", "KS-{}"),
        (r"\b((?:hd|ll|pe)-\d+)", "{}"),
    ):
        if m := re.search(pattern, t):
            parts.append(label.format(m.group(1).upper()))
    if re.search(r"в/с|высш", t):
        parts.append("oliy nav")
    elif re.search(r"\b1\b|1-|перв|\bi сорт", t):
        parts.append("1-nav")
    elif re.search(r"\b2\b|втор", t):
        parts.append("2-nav")
    for word, label in (
        ("рафинир", "rafinatsiyalangan"),
        ("йодир", "yodlangan"),
        ("обогащ", "vitaminlashtirilgan"),
        ("хлебопекар", "novvoylik uchun"),
        ("строит", "qurilish uchun"),
        ("негаш", "so‘ndirilmagan"),
    ):
        if word in t:
            parts.append(label)
    return ", ".join(dict.fromkeys(parts))


def city(address: str) -> str:
    if m := re.search(r",\s*([^,()]+?)\s+sh\.", address):
        return m.group(1).strip()
    parts = [p.strip() for p in address.split(",")]
    return parts[1] if len(parts) > 1 else ""


def money(value: float) -> int:
    return int(round(value, -3 if value >= 1_000_000 else -2))


def stock(seller: str, lot: float) -> int:
    share = 0.5 + int(hashlib.sha256(seller.encode()).hexdigest()[:6], 16) / 0xFFFFFF
    return max(2, round(min(max(lot, 5), 60) * share))


def main() -> None:
    registry, output = Path(sys.argv[1]), Path(sys.argv[2])
    con = duckdb.connect(str(registry), read_only=True)
    goods = []
    for good in GOODS.values():
        weeks = con.execute(WEEKS, {"family": good.family}).fetchall()
        sellers = []
        for i, row in enumerate(con.execute(SELLERS, {"family": good.family}).fetchall()):
            (
                name,
                region,
                deals,
                recent,
                year,
                _,
                lot,
                on_time,
                since,
                product,
                packaging,
                warehouse,
            ) = row
            available = DEMO_STOCK[good.id][i] if good.id in DEMO_STOCK else stock(name, float(lot))
            sellers.append(
                {
                    "id": f"{good.id}-{i + 1}",
                    "name": tidy(name),
                    "region": REGISTRY[region],
                    "city": city(warehouse or ""),
                    "grade": grade(product or ""),
                    "packaging": PACKAGING.get(packaging or "", packaging or ""),
                    "price": money(float(recent or year)),
                    "available": available,
                    "deals": int(deals),
                    "on_time": round(float(on_time or 0), 3),
                    "since": int(since),
                }
            )
        goods.append({"id": good.id, "weeks": [[w, int(p)] for w, p in weeks], "sellers": sellers})
    data = {"as_of": "2026-10-30", "source": "UZEX hackathon registry (fictional)", "goods": goods}
    output.write_text(json.dumps(data, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
