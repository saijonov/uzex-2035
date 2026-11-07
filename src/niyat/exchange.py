import itertools
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from niyat.catalog import (
    CLEARING_FEE,
    EXCHANGE_FEE_BUYER,
    EXCHANGE_FEE_SELLER,
    PRODUCTS,
    delivery_days,
    freight_per_tonne,
)
from niyat.clearing import Fill, Intent, Offer, RoundResult, Shipment, clear
from niyat.market import Seed, load_seed, reference_prices, round_background, round_offers
from niyat.regions import distance_km

START_BALANCE = 50_000_000.0
FEE_RATE = EXCHANGE_FEE_BUYER + CLEARING_FEE
SELL_FEE_RATE = EXCHANGE_FEE_SELLER + CLEARING_FEE
EPS = 1e-6


@dataclass
class Account:
    id: str
    name: str
    balance: float = START_BALANCE
    held: float = 0.0


@dataclass
class LiveIntent:
    intent: Intent
    account_id: str
    reserved: float
    created: datetime
    status: str = "waiting"
    round: int | None = None
    fill: Fill | None = None
    cost: float = 0.0
    fees: float = 0.0
    refund: float = 0.0
    eta: datetime | None = None
    delivered: datetime | None = None
    shipment: Shipment | None = None
    receipts: list[str] = field(default_factory=list)

    @property
    def hold(self) -> bool:
        return self.intent.region is None


@dataclass
class Receipt:
    id: str
    account_id: str
    product: str
    region: str
    plant: str
    tonnes: float
    cost: float
    round: int
    locked: float = 0.0
    status: str = "stored"
    delivery_region: str | None = None
    eta: datetime | None = None

    @property
    def free(self) -> float:
        return round(self.tonnes - self.locked, 6)


@dataclass
class SellOrder:
    id: str
    account_id: str
    receipt_id: str
    product: str
    region: str
    tonnes: float
    min_price: float
    created: datetime
    status: str = "waiting"
    round: int | None = None
    sold: float = 0.0
    price: float | None = None
    proceeds: float = 0.0
    fees: float = 0.0


@dataclass
class Alert:
    id: str
    account_id: str
    product: str
    direction: str
    price: float
    status: str = "active"
    round: int | None = None
    value: float | None = None


@dataclass
class RoundRecord:
    number: int
    at: datetime
    offers: list[Offer]
    intents: list[Intent]
    result: RoundResult
    live_ids: list[str] = field(default_factory=list)
    sell_ids: list[str] = field(default_factory=list)
    index: dict[str, float] = field(default_factory=dict)
    plant_region_prices: dict[tuple[str, str], float] = field(default_factory=dict)


def price_index(offers: list[Offer], result: RoundResult) -> dict[str, float]:
    sold: dict[str, float] = defaultdict(float)
    for fill in result.fills.values():
        for a in fill.allocations:
            sold[a.offer_id] += a.tonnes
    index = {}
    for product in PRODUCTS:
        mine = [o for o in offers if o.product == product]
        traded = [(result.plant_prices[o.id], sold[o.id]) for o in mine if sold[o.id] > EPS]
        if traded:
            index[product] = round(sum(p * t for p, t in traded) / sum(t for _, t in traded), 2)
        elif mine:
            index[product] = round(sum(result.plant_prices[o.id] for o in mine) / len(mine), 2)
    return index


def plant_region_prices(offers: list[Offer], result: RoundResult) -> dict[tuple[str, str], float]:
    prices: dict[tuple[str, str], float] = {}
    for o in offers:
        key = (o.region, o.product)
        price = result.plant_prices[o.id]
        if key not in prices or price < prices[key]:
            prices[key] = round(price, 2)
    return prices


class Exchange:
    def __init__(self, seed: Seed | None = None, clock=datetime.now, warmup: int = 0):
        self.seed = seed or load_seed()
        self.reference = reference_prices(self.seed)
        self.clock = clock
        self.lock = threading.RLock()
        self.accounts: dict[str, Account] = {}
        self.live: dict[str, LiveIntent] = {}
        self.receipts: dict[str, Receipt] = {}
        self.sells: dict[str, SellOrder] = {}
        self.alerts: dict[str, Alert] = {}
        self.rounds: list[RoundRecord] = []
        self.counter = itertools.count(1)
        for _ in range(warmup):
            self.clear_round()

    def account(self, account_id: str, name: str = "") -> Account:
        with self.lock:
            if account_id not in self.accounts:
                self.accounts[account_id] = Account(account_id, name or account_id)
            return self.accounts[account_id]

    def available(self, account_id: str) -> float:
        a = self.account(account_id)
        return a.balance - a.held

    def next_round(self) -> int:
        return len(self.rounds) + 1

    def reference_price(self, region: str | None, product: str) -> float | None:
        if region is None:
            return self.index_price(product)
        if self.rounds:
            price = self.rounds[-1].result.zone_prices.get((region, product))
            if price:
                return float(price)
        return self.reference.get((region, product))

    def index_price(self, product: str) -> float | None:
        if self.rounds and product in self.rounds[-1].index:
            return self.rounds[-1].index[product]
        values = [s.median_price for s in self.seed.sellers if s.product == product]
        return round(sum(values) / len(values), 2) if values else None

    def mark_price(self, region: str, product: str) -> float | None:
        if self.rounds:
            price = self.rounds[-1].plant_region_prices.get((region, product))
            if price:
                return price
        return self.index_price(product)

    def history(self, product: str) -> list[dict]:
        return [
            {"round": r.number, "price": r.index[product]}
            for r in self.rounds
            if product in r.index
        ]

    def fastest_days(self, region: str | None, product: str) -> int | None:
        if region is None:
            return 0
        days = [
            delivery_days(distance_km(s.region, region))
            for s in self.seed.sellers
            if s.product == product
        ]
        return min(days) if days else None

    def submit(
        self,
        account_id: str,
        region: str | None,
        product: str,
        quantity: float,
        limit: float,
        deadline_days: int,
    ) -> LiveIntent:
        with self.lock:
            account = self.account(account_id)
            reserved = round(quantity * limit * (1 + FEE_RATE), 2)
            if reserved > account.balance - account.held + EPS:
                raise ValueError("insufficient_funds")
            intent = Intent(
                f"live-{next(self.counter)}",
                account.name,
                region,
                product,
                float(quantity),
                float(limit),
                int(deadline_days),
                live=True,
            )
            account.held += reserved
            live = LiveIntent(intent, account_id, reserved, self.clock())
            self.live[intent.id] = live
            return live

    def cancel(self, intent_id: str) -> LiveIntent:
        with self.lock:
            live = self.live[intent_id]
            if live.status != "waiting":
                raise ValueError("not_waiting")
            self.accounts[live.account_id].held -= live.reserved
            live.status = "cancelled"
            live.refund = live.reserved
            return live

    def sell(self, account_id: str, receipt_id: str, tonnes: float, min_price: float) -> SellOrder:
        with self.lock:
            receipt = self.receipts[receipt_id]
            if receipt.account_id != account_id or receipt.status != "stored":
                raise ValueError("not_yours")
            if tonnes <= 0 or tonnes > receipt.free + EPS:
                raise ValueError("not_enough_goods")
            if min_price <= 0:
                raise ValueError("bad_price")
            receipt.locked += tonnes
            order = SellOrder(
                f"sell-{next(self.counter)}",
                account_id,
                receipt_id,
                receipt.product,
                receipt.region,
                float(tonnes),
                float(min_price),
                self.clock(),
            )
            self.sells[order.id] = order
            return order

    def cancel_sell(self, order_id: str) -> SellOrder:
        with self.lock:
            order = self.sells[order_id]
            if order.status != "waiting":
                raise ValueError("not_waiting")
            self.receipts[order.receipt_id].locked -= order.tonnes
            order.status = "cancelled"
            return order

    def deliver(self, account_id: str, receipt_id: str, region: str) -> Receipt:
        with self.lock:
            receipt = self.receipts[receipt_id]
            if receipt.account_id != account_id or receipt.status != "stored":
                raise ValueError("not_yours")
            if receipt.locked > EPS:
                raise ValueError("on_sale")
            km = distance_km(receipt.region, region)
            cost = round(freight_per_tonne(km) * receipt.tonnes, 2)
            if cost > self.available(account_id) + EPS:
                raise ValueError("insufficient_funds")
            self.accounts[account_id].balance -= cost
            receipt.status = "delivering"
            receipt.delivery_region = region
            receipt.eta = self.clock() + timedelta(days=delivery_days(km))
            return receipt

    def portfolio(self, account_id: str) -> list[dict]:
        rows = []
        for r in self.receipts.values():
            if r.account_id != account_id or r.tonnes <= EPS:
                continue
            mark = self.mark_price(r.region, r.product)
            rows.append(
                {
                    "receipt": r,
                    "mark": mark,
                    "value": round((mark or 0) * r.tonnes, 2),
                    "pnl": round(((mark or r.cost) - r.cost) * r.tonnes, 2),
                }
            )
        return rows

    def clear_round(self) -> RoundRecord:
        with self.lock:
            number = self.next_round()
            offers = round_offers(self.seed, number)
            background = round_background(self.seed, number, offers)
            selling = [s for s in self.sells.values() if s.status == "waiting"]
            offers += [
                Offer(
                    s.id,
                    self.accounts[s.account_id].name,
                    s.region,
                    s.product,
                    s.tonnes,
                    s.min_price,
                )
                for s in selling
            ]
            waiting = [lv for lv in self.live.values() if lv.status == "waiting"]
            intents = background + [lv.intent for lv in waiting]
            result = clear(offers, intents)
            now = self.clock()
            by_offer = {o.id: o for o in offers}
            shipments = {(s.offer_id, s.region): s for s in result.shipments}
            for lv in waiting:
                self.settle_buy(lv, result, number, now, by_offer, shipments)
            for order in selling:
                self.settle_sell(order, result, number)
            record = RoundRecord(
                number,
                now,
                offers,
                intents,
                result,
                [lv.intent.id for lv in waiting],
                [s.id for s in selling],
                price_index(offers, result),
                plant_region_prices(offers, result),
            )
            self.rounds.append(record)
            self.check_alerts(record)
            return record

    def add_alert(self, account_id: str, product: str, direction: str, price: float) -> Alert:
        with self.lock:
            if direction not in ("below", "above") or product not in PRODUCTS or price <= 0:
                raise ValueError("bad_alert")
            alert = Alert(f"al-{next(self.counter)}", account_id, product, direction, float(price))
            self.alerts[alert.id] = alert
            return alert

    def check_alerts(self, record: RoundRecord) -> None:
        for alert in self.alerts.values():
            value = record.index.get(alert.product)
            if alert.status != "active" or value is None:
                continue
            hit = value <= alert.price if alert.direction == "below" else value >= alert.price
            if hit:
                alert.status = "fired"
                alert.round = record.number
                alert.value = value

    def settle_buy(self, lv, result, number, now, by_offer, shipments) -> None:
        fill = result.fills[lv.intent.id]
        account = self.accounts[lv.account_id]
        lv.round = number
        lv.fill = fill
        lv.cost = round(fill.filled * fill.price, 2) if fill.filled else 0.0
        lv.fees = round(lv.cost * FEE_RATE, 2)
        lv.refund = round(lv.reserved - lv.cost - lv.fees, 2)
        account.held -= lv.reserved
        account.balance -= lv.cost + lv.fees
        if not fill.filled:
            lv.status = "unmatched"
            return
        lv.status = "matched" if fill.reason == "filled" else "partial"
        if lv.hold:
            for a in fill.allocations:
                offer = by_offer[a.offer_id]
                receipt = Receipt(
                    f"rc-{next(self.counter)}",
                    lv.account_id,
                    offer.product,
                    offer.region,
                    offer.seller,
                    a.tonnes,
                    a.plant_price,
                    number,
                )
                self.receipts[receipt.id] = receipt
                lv.receipts.append(receipt.id)
            return
        days = max(delivery_days(a.km) for a in fill.allocations)
        lv.eta = now + timedelta(days=days)
        main = max(fill.allocations, key=lambda a: a.tonnes)
        lv.shipment = shipments.get((main.offer_id, lv.intent.region))

    def settle_sell(self, order: SellOrder, result: RoundResult, number: int) -> None:
        sold = sum(
            a.tonnes for f in result.fills.values() for a in f.allocations if a.offer_id == order.id
        )
        receipt = self.receipts[order.receipt_id]
        account = self.accounts[order.account_id]
        order.round = number
        order.price = result.plant_prices[order.id]
        order.sold = round(sold, 6)
        order.proceeds = round(order.sold * order.price, 2)
        order.fees = round(order.proceeds * SELL_FEE_RATE, 2)
        account.balance += order.proceeds - order.fees
        receipt.locked -= order.tonnes
        receipt.tonnes = round(receipt.tonnes - order.sold, 6)
        if receipt.tonnes <= EPS:
            receipt.status = "sold"
        if order.sold <= EPS:
            order.status = "unsold"
        elif order.sold + EPS < order.tonnes:
            order.status = "partial"
        else:
            order.status = "sold"

    def confirm_delivery(self, intent_id: str) -> LiveIntent:
        with self.lock:
            live = self.live[intent_id]
            if live.status not in ("matched", "partial") or live.hold:
                raise ValueError("not_deliverable")
            live.status = "delivered"
            live.delivered = self.clock()
            return live

    def record(self, number: int) -> RoundRecord | None:
        return self.rounds[number - 1] if 0 < number <= len(self.rounds) else None
