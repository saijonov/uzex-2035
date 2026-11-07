import math
from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

from niyat.catalog import TRUCK_TONNES, delivery_days, freight_per_tonne
from niyat.regions import REGIONS, distance_km

EPS = 1e-6


@dataclass(frozen=True)
class Offer:
    id: str
    seller: str
    region: str
    product: str
    capacity: float
    ask: float


@dataclass(frozen=True)
class Intent:
    id: str
    owner: str
    region: str
    product: str
    quantity: float
    limit: float
    deadline_days: int
    live: bool = False


@dataclass(frozen=True)
class Allocation:
    offer_id: str
    intent_id: str
    tonnes: float
    km: float
    freight: float
    plant_price: float


@dataclass
class Fill:
    intent_id: str
    filled: float
    price: float | None
    reason: str
    rent: float = 0.0
    allocations: list[Allocation] = field(default_factory=list)


@dataclass(frozen=True)
class Shipment:
    offer_id: str
    region: str
    tonnes: float
    buyers: int
    trucks: int
    fill: float


@dataclass
class RoundResult:
    fills: dict[str, Fill]
    plant_prices: dict[str, float]
    seller_rents: dict[str, float]
    zone_prices: dict[tuple[str, str], float]
    shipments: list[Shipment]
    welfare: float
    traded: float


def route(offer: Offer, region: str) -> tuple[float, float, int]:
    km = distance_km(offer.region, region)
    return km, freight_per_tonne(km), delivery_days(km)


def feasible(offer: Offer, intent: Intent) -> bool:
    return (
        offer.product == intent.product and route(offer, intent.region)[2] <= intent.deadline_days
    )


def lowest_prices(
    offers: list[Offer],
    intents: list[Intent],
    pairs: list[tuple[int, int, float, float, float]],
    flows: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    n_o, n_b = len(offers), len(intents)
    sold = np.zeros(n_o)
    bought = np.zeros(n_b)
    for k, (i, j, *_rest) in enumerate(pairs):
        sold[i] += flows[k]
        bought[j] += flows[k]
    ub = lil_matrix((len(pairs), n_o + n_b))
    ub_rhs = np.zeros(len(pairs))
    used = [k for k in range(len(pairs)) if flows[k] > EPS]
    eq = lil_matrix((max(len(used), 1), n_o + n_b))
    eq_rhs = np.zeros(max(len(used), 1))
    for k, (i, j, surplus, *_rest) in enumerate(pairs):
        ub[k, i] = -1.0
        ub[k, n_o + j] = -1.0
        ub_rhs[k] = -surplus
    for row, k in enumerate(used):
        i, j, surplus = pairs[k][0], pairs[k][1], pairs[k][2]
        eq[row, i] = 1.0
        eq[row, n_o + j] = 1.0
        eq_rhs[row] = surplus
    bounds = [(0, 0) if sold[i] < offers[i].capacity - EPS else (0, None) for i in range(n_o)]
    bounds += [(0, 0) if bought[j] < intents[j].quantity - EPS else (0, None) for j in range(n_b)]
    result = linprog(
        c=np.concatenate([np.ones(n_o), np.zeros(n_b)]),
        A_ub=ub.tocsr(),
        b_ub=ub_rhs,
        A_eq=eq.tocsr() if used else None,
        b_eq=eq_rhs if used else None,
        bounds=bounds,
        method="highs-ds",
    )
    if result.status != 0:
        raise RuntimeError(f"Pricing failed: {result.message}")
    values = np.maximum(result.x, 0.0)
    return values[:n_o], values[n_o:]


def clear(offers: list[Offer], intents: list[Intent]) -> RoundResult:
    pairs: list[tuple[int, int, float, float, float]] = []
    for i, offer in enumerate(offers):
        for j, intent in enumerate(intents):
            if not feasible(offer, intent):
                continue
            km, freight, _ = route(offer, intent.region)
            surplus = intent.limit - offer.ask - freight
            if surplus > EPS:
                pairs.append((i, j, surplus, km, freight))

    flows = np.zeros(len(pairs))
    seller_rent = np.zeros(len(offers))
    buyer_rent = np.zeros(len(intents))
    welfare = 0.0
    if pairs:
        rows = len(offers) + len(intents)
        matrix = lil_matrix((rows, len(pairs)))
        for k, (i, j, *_rest) in enumerate(pairs):
            matrix[i, k] = 1.0
            matrix[len(offers) + j, k] = 1.0
        bounds_rhs = np.array([o.capacity for o in offers] + [b.quantity for b in intents])
        result = linprog(
            c=-np.array([p[2] for p in pairs]),
            A_ub=matrix.tocsr(),
            b_ub=bounds_rhs,
            bounds=(0, None),
            method="highs-ds",
        )
        if result.status != 0:
            raise RuntimeError(f"Clearing failed: {result.message}")
        flows = np.round(result.x, 6)
        welfare = float(-result.fun)
        seller_rent, buyer_rent = lowest_prices(offers, intents, pairs, flows)

    plant_prices = {o.id: round(o.ask + seller_rent[i], 2) for i, o in enumerate(offers)}
    seller_rents = {o.id: round(float(seller_rent[i]), 2) for i, o in enumerate(offers)}

    by_intent: dict[str, list[Allocation]] = defaultdict(list)
    for k, (i, j, _surplus, km, freight) in enumerate(pairs):
        if flows[k] > EPS:
            offer, intent = offers[i], intents[j]
            by_intent[intent.id].append(
                Allocation(
                    offer.id, intent.id, float(flows[k]), km, freight, plant_prices[offer.id]
                )
            )

    fills: dict[str, Fill] = {}
    for j, intent in enumerate(intents):
        options = [
            plant_prices[o.id] + route(o, intent.region)[1] for o in offers if feasible(o, intent)
        ]
        allocations = by_intent.get(intent.id, [])
        filled = round(sum(a.tonnes for a in allocations), 6)
        price = round(min(options), 2) if options else None
        if not any(o.product == intent.product for o in offers):
            reason = "no_seller"
        elif not options:
            reason = "deadline"
        elif filled <= EPS:
            reason = "price_above_limit"
        elif filled + EPS < intent.quantity:
            reason = "partial"
        else:
            reason = "filled"
        fills[intent.id] = Fill(
            intent.id, filled, price, reason, round(float(buyer_rent[j]), 2), allocations
        )

    zone_prices: dict[tuple[str, str], float] = {}
    for product in sorted({o.product for o in offers}):
        for region in REGIONS:
            options = [
                plant_prices[o.id] + route(o, region)[1] for o in offers if o.product == product
            ]
            if options:
                zone_prices[(region, product)] = round(min(options), 2)

    grouped: dict[tuple[str, str], list[Allocation]] = defaultdict(list)
    regions_by_intent = {b.id: b.region for b in intents}
    for allocations in by_intent.values():
        for a in allocations:
            grouped[(a.offer_id, regions_by_intent[a.intent_id])].append(a)
    shipments = []
    for (offer_id, region), allocations in sorted(grouped.items()):
        tonnes = sum(a.tonnes for a in allocations)
        trucks = max(1, math.ceil(tonnes / TRUCK_TONNES - EPS))
        shipments.append(
            Shipment(
                offer_id,
                region,
                round(tonnes, 3),
                len({a.intent_id for a in allocations}),
                trucks,
                round(tonnes / (trucks * TRUCK_TONNES), 3),
            )
        )

    traded = round(sum(f.filled for f in fills.values()), 6)
    return RoundResult(
        fills, plant_prices, seller_rents, zone_prices, shipments, round(welfare, 2), traded
    )
