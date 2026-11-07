import itertools
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from niyat.catalog import CLEARING_FEE, EXCHANGE_FEE_BUYER, delivery_days
from niyat.clearing import Fill, Intent, Offer, RoundResult, Shipment, clear
from niyat.market import Seed, load_seed, reference_prices, round_background, round_offers
from niyat.regions import distance_km

START_BALANCE = 50_000_000.0
FEE_RATE = EXCHANGE_FEE_BUYER + CLEARING_FEE


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


@dataclass
class RoundRecord:
    number: int
    at: datetime
    offers: list[Offer]
    intents: list[Intent]
    result: RoundResult
    live_ids: list[str] = field(default_factory=list)


class Exchange:
    def __init__(self, seed: Seed | None = None, clock=datetime.now):
        self.seed = seed or load_seed()
        self.reference = reference_prices(self.seed)
        self.clock = clock
        self.lock = threading.RLock()
        self.accounts: dict[str, Account] = {}
        self.live: dict[str, LiveIntent] = {}
        self.rounds: list[RoundRecord] = []
        self.counter = itertools.count(1)

    def account(self, account_id: str, name: str = "") -> Account:
        with self.lock:
            if account_id not in self.accounts:
                self.accounts[account_id] = Account(account_id, name or account_id)
            return self.accounts[account_id]

    def next_round(self) -> int:
        return len(self.rounds) + 1

    def reference_price(self, region: str, product: str) -> float | None:
        if self.rounds:
            price = self.rounds[-1].result.zone_prices.get((region, product))
            if price:
                return float(price)
        return self.reference.get((region, product))

    def fastest_days(self, region: str, product: str) -> int | None:
        days = [
            delivery_days(distance_km(s.region, region))
            for s in self.seed.sellers
            if s.product == product
        ]
        return min(days) if days else None

    def submit(
        self,
        account_id: str,
        region: str,
        product: str,
        quantity: float,
        limit: float,
        deadline_days: int,
    ) -> LiveIntent:
        with self.lock:
            account = self.account(account_id)
            reserved = round(quantity * limit * (1 + FEE_RATE), 2)
            if reserved > account.balance - account.held + 1e-6:
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

    def clear_round(self) -> RoundRecord:
        with self.lock:
            number = self.next_round()
            offers = round_offers(self.seed, number)
            background = round_background(self.seed, number, offers)
            waiting = [lv for lv in self.live.values() if lv.status == "waiting"]
            intents = background + [lv.intent for lv in waiting]
            result = clear(offers, intents)
            now = self.clock()
            shipments = {(s.offer_id, s.region): s for s in result.shipments}
            for lv in waiting:
                fill = result.fills[lv.intent.id]
                account = self.accounts[lv.account_id]
                lv.round = number
                lv.fill = fill
                lv.cost = round(fill.filled * fill.price, 2) if fill.filled else 0.0
                lv.fees = round(lv.cost * FEE_RATE, 2)
                lv.refund = round(lv.reserved - lv.cost - lv.fees, 2)
                account.held -= lv.reserved
                account.balance -= lv.cost + lv.fees
                if fill.filled:
                    lv.status = "matched" if fill.reason == "filled" else "partial"
                    days = max(delivery_days(a.km) for a in fill.allocations)
                    lv.eta = now + timedelta(days=days)
                    main = max(fill.allocations, key=lambda a: a.tonnes)
                    lv.shipment = shipments.get((main.offer_id, lv.intent.region))
                else:
                    lv.status = "unmatched"
            record = RoundRecord(
                number, now, offers, intents, result, [lv.intent.id for lv in waiting]
            )
            self.rounds.append(record)
            return record

    def confirm_delivery(self, intent_id: str) -> LiveIntent:
        with self.lock:
            live = self.live[intent_id]
            if live.status not in ("matched", "partial"):
                raise ValueError("not_deliverable")
            live.status = "delivered"
            live.delivered = self.clock()
            return live

    def record(self, number: int) -> RoundRecord | None:
        return self.rounds[number - 1] if 0 < number <= len(self.rounds) else None
