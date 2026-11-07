import json
import random
from dataclasses import dataclass
from pathlib import Path

from niyat.catalog import PRODUCTS, freight_per_tonne
from niyat.clearing import Intent, Offer
from niyat.regions import REGIONS, distance_km

SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "cement_market.json"
ROUNDS_PER_YEAR = 2400.0
SMALL_SHARE = 0.8


@dataclass(frozen=True)
class SellerLine:
    id: str
    name: str
    region: str
    product: str
    median_price: float
    tonnes: float


@dataclass(frozen=True)
class Seed:
    sellers: list[SellerLine]
    buyer_weights: dict[str, float]


def load_seed(path: Path = SEED_PATH) -> Seed:
    raw = json.loads(path.read_text())
    sellers = [
        SellerLine(f"s{k}", s["name"], s["region"], s["product"], s["median_price"], s["tonnes"])
        for k, s in enumerate(raw["sellers"])
    ]
    weights = {region: float(v["deals"]) for region, v in raw["buyers"].items()}
    return Seed(sellers, weights)


def reference_prices(seed: Seed) -> dict[tuple[str, str], float]:
    prices: dict[tuple[str, str], float] = {}
    for product in PRODUCTS:
        lines = [s for s in seed.sellers if s.product == product]
        for region in REGIONS:
            if lines:
                prices[(region, product)] = round(
                    min(
                        s.median_price + freight_per_tonne(distance_km(s.region, region))
                        for s in lines
                    ),
                    -3,
                )
    return prices


def round_offers(seed: Seed, number: int) -> list[Offer]:
    rng = random.Random(number * 7919)
    offers = []
    for s in seed.sellers:
        capacity = max(5, round(s.tonnes / ROUNDS_PER_YEAR * rng.uniform(0.6, 1.4)))
        ask = round(s.median_price * rng.uniform(0.95, 1.03), -3)
        offers.append(Offer(f"r{number}-{s.id}", s.name, s.region, s.product, float(capacity), ask))
    return offers


def round_background(seed: Seed, number: int, offers: list[Offer]) -> list[Intent]:
    rng = random.Random(number * 104729)
    reference = reference_prices(seed)
    regions = list(seed.buyer_weights)
    weights = [seed.buyer_weights[r] for r in regions]
    intents: list[Intent] = []
    for product in PRODUCTS:
        supply = sum(o.capacity for o in offers if o.product == product)
        target = supply * rng.uniform(0.85, 1.1)
        demand = 0.0
        k = 0
        while demand < target:
            region = rng.choices(regions, weights)[0]
            small = rng.random() < SMALL_SHARE
            quantity = float(rng.randint(2, 10) if small else rng.randint(20, 60))
            limit = round(reference[(region, product)] * rng.uniform(0.97, 1.16), -3)
            intents.append(
                Intent(
                    f"r{number}-bg-{product}-{k}",
                    "builder" if small else "company",
                    region,
                    product,
                    quantity,
                    limit,
                    rng.randint(3, 10),
                )
            )
            demand += quantity
            k += 1
    return intents
