import json
import math
from pathlib import Path

from .goods import CLEARING_FEE, EXCHANGE_FEE, FREIGHT_PER_TONNE_KM, GOODS, KM_PER_DAY, TRUCK_TONNES
from .regions import LOCAL_KM, REGIONS


class Market:
    def __init__(self, data_dir: Path):
        data = json.loads((data_dir / "market.json").read_text())
        self.as_of = data["as_of"]
        self.goods = {g["id"]: g for g in data["goods"]}
        self.sellers = {
            s["id"]: {**s, "good": g["id"]} for g in data["goods"] for s in g["sellers"]
        }
        self.routes = json.loads((data_dir / "routes.json").read_text())

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

    def offer(self, seller: dict, region: str) -> dict:
        km = self.route(seller["region"], region)["km"]
        freight = round(km * FREIGHT_PER_TONNE_KM, -2)
        return {
            **seller,
            "region_name": REGIONS[seller["region"]].name,
            "km": km,
            "freight": int(freight),
            "delivered": int(seller["price"] + freight),
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

    def detail(self, good: str, region: str) -> dict:
        prices = [p for _, p in self.goods[good]["weeks"]]
        return {
            **self.summary(good, region),
            "weeks": self.goods[good]["weeks"],
            "low": min(prices),
            "high": max(prices),
            "offers": self.offers(good, region),
        }

    def plan(
        self, good: str, tonnes: int, region: str, whole: bool = False, seller: str | None = None
    ) -> dict:
        offers = [self.offer(self.sellers[seller], region)] if seller else self.offers(good, region)
        parts, left = [], tonnes
        for o in offers:
            take = min(o["available"], left)
            if take:
                route = self.route(o["region"], region)
                parts.append(
                    {
                        "seller": {
                            k: o[k]
                            for k in (
                                "id",
                                "name",
                                "region",
                                "region_name",
                                "city",
                                "grade",
                                "on_time",
                                "deals",
                            )
                        },
                        "tonnes": take,
                        "price": o["price"],
                        "freight": o["freight"],
                        "km": o["km"],
                        "days": o["days"],
                        "trucks": math.ceil(take / TRUCK_TONNES),
                        "line": route["line"],
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
            "exchange_fee": exchange,
            "clearing_fee": clearing,
            "total": cost + delivery + exchange + clearing,
            "trucks": sum(p["trucks"] for p in parts),
            "days": max((p["days"] for p in parts), default=0),
        }
