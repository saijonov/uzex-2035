import json
import math
import zlib
from pathlib import Path

from .goods import (
    CLEARING_FEE,
    EXCHANGE_FEE,
    FREIGHT_PER_TONNE_KM,
    GOODS,
    KM_PER_DAY,
    SELLER_FEE,
    TRUCK_TONNES,
)
from .regions import LOCAL_KM, REGIONS

TRUCK_PER_KM = FREIGHT_PER_TONNE_KM * TRUCK_TONNES
SELLER_KEYS = ("id", "name", "region", "region_name", "city", "grade", "on_time", "deals")


def seed(*parts: str) -> int:
    return zlib.crc32("|".join(parts).encode())


class Market:
    def __init__(self, data_dir: Path):
        data = json.loads((data_dir / "market.json").read_text())
        self.as_of = data["as_of"]
        self.goods = {g["id"]: g for g in data["goods"]}
        self.sellers = {
            s["id"]: {**s, "good": g["id"]} for g in data["goods"] for s in g["sellers"]
        }
        self.routes = json.loads((data_dir / "routes.json").read_text())

    def index(self, good: str) -> int:
        return self.goods[good]["weeks"][-1][1]

    def route(self, start: str, end: str) -> dict:
        if start == end:
            r = REGIONS[end]
            return {
                "km": LOCAL_KM,
                "line": [[round(r.lat - 0.18, 3), round(r.lon - 0.24, 3)], [r.lat, r.lon]],
            }
        key = "|".join(sorted((start, end)))
        route = self.routes[key]
        line = route["line"] if key.startswith(start + "|") else route["line"][::-1]
        return {"km": route["km"], "line": line}

    def leg(self, start: str, end: str, tonnes: int, key: str) -> dict:
        route = self.route(start, end)
        km, trucks = route["km"], math.ceil(tonnes / TRUCK_TONNES)
        others = trucks * TRUCK_TONNES - tonnes
        return {
            "km": km,
            "days": 1 + km // KM_PER_DAY,
            "freight": int(round(km * FREIGHT_PER_TONNE_KM, -2)),
            "trucks": trucks,
            "solo": trucks * km * TRUCK_PER_KM,
            "others": others,
            "riders": min(others, 1 + seed(key, end) % 4) if others else 0,
            "line": route["line"],
        }

    def offer(self, seller: dict, region: str) -> dict:
        km = self.route(seller["region"], region)["km"]
        freight = int(round(km * FREIGHT_PER_TONNE_KM, -2))
        return {
            **seller,
            "region_name": REGIONS[seller["region"]].name,
            "km": km,
            "freight": freight,
            "delivered": seller["price"] + freight,
            "days": 1 + km // KM_PER_DAY,
        }

    def offers(self, good: str, region: str) -> list[dict]:
        offers = [self.offer(s, region) for s in self.goods[good]["sellers"]]
        return sorted(offers, key=lambda o: (o["delivered"], o["days"]))

    def summary(self, good: str, region: str) -> dict:
        g, weeks = GOODS[good], self.goods[good]["weeks"]
        offers = self.offers(good, region)
        return {
            "id": good,
            "name": g.name,
            "category": g.category,
            "words": list(g.words),
            "price": weeks[-1][1],
            "change": round(weeks[-1][1] / weeks[-5][1] - 1, 4),
            "spark": [p for _, p in weeks[-13:]],
            "sellers": len(offers),
            "best": offers[0]["delivered"],
            "stock": sum(o["available"] for o in offers),
        }

    def pool(self, good: str, region: str) -> dict:
        offer, h = self.offers(good, region)[0], seed(good, region)
        filled = 6 + h % 10
        return {
            "seller": {k: offer[k] for k in ("id", "name", "city", "available")},
            "filled": filled,
            "free": TRUCK_TONNES - filled,
            "buyers": 2 + h % 4,
            "shared": offer["freight"],
            "truck": offer["km"] * TRUCK_PER_KM,
            "km": offer["km"],
        }

    def detail(self, good: str, region: str) -> dict:
        prices = [p for _, p in self.goods[good]["weeks"]]
        return {
            **self.summary(good, region),
            "weeks": self.goods[good]["weeks"],
            "low": min(prices),
            "high": max(prices),
            "offers": self.offers(good, region),
            "pool": self.pool(good, region),
        }

    def plan(
        self, good: str, tonnes: int, region: str, whole: bool = False, seller: str | None = None
    ) -> dict:
        offers = [self.offer(self.sellers[seller], region)] if seller else self.offers(good, region)
        parts, left = [], tonnes
        for o in offers:
            take = min(o["available"], left)
            if take:
                parts.append(
                    {
                        "seller": {k: o[k] for k in SELLER_KEYS},
                        "tonnes": take,
                        "price": o["price"],
                        **self.leg(o["region"], region, take, o["id"]),
                    }
                )
                left -= take
            if not left:
                break
        cost = sum(p["tonnes"] * p["price"] for p in parts)
        delivery = sum(p["tonnes"] * p["freight"] for p in parts)
        exchange, clearing = round(cost * EXCHANGE_FEE), round(cost * CLEARING_FEE)
        return {
            "good": good,
            "good_name": GOODS[good].name,
            "region": region,
            "region_name": REGIONS[region].name,
            "asked": tonnes,
            "filled": tonnes - left,
            "short": left,
            "whole": whole,
            "ready": bool(parts) and (left == 0 or not whole),
            "parts": parts,
            "cost": cost,
            "delivery": delivery,
            "delivery_solo": sum(p["solo"] for p in parts),
            "exchange_fee": exchange,
            "clearing_fee": clearing,
            "total": cost + delivery + exchange + clearing,
            "trucks": sum(p["trucks"] for p in parts),
            "days": max((p["days"] for p in parts), default=0),
        }

    def request(
        self, good: str, region: str, tonnes: int, buyers: int, home: str, mine: bool = False
    ) -> dict:
        best = self.offers(good, region)[0]["delivered"]
        limit = int(round(best * (1.01 + seed("limit", good, region) % 5 / 100), -3))
        leg = self.leg(home, region, tonnes, good)
        return {
            "id": f"{good}-{region}{'-mine' if mine else ''}",
            "good": good,
            "good_name": GOODS[good].name,
            "category": GOODS[good].category,
            "region": region,
            "region_name": REGIONS[region].name,
            "city": REGIONS[region].city,
            "tonnes": tonnes,
            "buyers": buyers,
            "limit": limit,
            "km": leg["km"],
            "freight": leg["freight"],
            "net": limit - leg["freight"],
            "index": self.index(good),
            "mine": mine,
        }

    def requests(self, home: str, wants: list[dict] | None = None) -> list[dict]:
        items = [
            self.request(w["good"], w["region"], w["tonnes"], 1, home, mine=True)
            for w in wants or []
        ]
        for good in GOODS:
            far = sorted(REGIONS, key=lambda r: -self.offers(good, r)[0]["delivered"])[:2]
            items += [
                self.request(good, r, 5 + seed(good, r) % 26, 1 + seed(r, good) % 6, home)
                for r in far
            ]
        return sorted(items, key=lambda i: (not i["mine"], i["km"]))

    def sale(self, good: str, tonnes: int, price: int, home: str, region: str) -> dict:
        leg = self.leg(home, region, tonnes, good)
        cost = tonnes * price
        exchange, clearing = round(cost * SELLER_FEE), round(cost * CLEARING_FEE)
        part = {
            "seller": {
                "id": "me",
                "name": "Sizning omboringiz",
                "region": home,
                "city": REGIONS[home].city,
            },
            "tonnes": tonnes,
            "price": price,
            **leg,
        }
        return {
            "good": good,
            "good_name": GOODS[good].name,
            "region": region,
            "region_name": REGIONS[region].name,
            "home": home,
            "filled": tonnes,
            "parts": [part],
            "cost": cost,
            "delivery": tonnes * leg["freight"],
            "exchange_fee": exchange,
            "clearing_fee": clearing,
            "payout": cost - exchange - clearing,
            "buyer_price": price + leg["freight"],
            "trucks": leg["trucks"],
            "days": leg["days"],
        }
