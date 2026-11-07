import asyncio
import contextlib
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from niyat.catalog import PRODUCTS, freight_per_tonne
from niyat.exchange import Exchange, LiveIntent
from niyat.explain import explain, money, product_name, region_name
from niyat.intake import Intake
from niyat.regions import REGIONS, distance_km
from niyat.settings import Settings

WEB = Path(__file__).resolve().parent / "web"


class ChatIn(BaseModel):
    session: str
    message: str
    lang: str = "uz"


class SessionIn(BaseModel):
    session: str
    lang: str = "uz"


class State:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.exchange = Exchange()
        self.intake = Intake(self.exchange, settings)
        self.next_at: float | None = None

    def reset(self) -> None:
        self.exchange = Exchange()
        self.intake = Intake(self.exchange, self.settings)


def intent_view(live: LiveIntent, state: State, lang: str) -> dict:
    record = state.exchange.record(live.round) if live.round else None
    i = live.intent
    fill = live.fill
    return {
        "id": i.id,
        "status": live.status,
        "product": product_name(i.product, lang),
        "quantity": i.quantity,
        "region": region_name(i.region, lang),
        "limit_text": money(i.limit, lang),
        "reserved_text": money(live.reserved, lang),
        "round": live.round,
        "filled": fill.filled if fill else 0,
        "price_text": money(fill.price, lang) if fill and fill.price else None,
        "explanation": explain(live, record, lang, state.exchange.next_round()),
    }


def account_view(state: State, session: str, lang: str) -> dict:
    a = state.exchange.account(session)
    return {
        "balance_text": money(a.balance - a.held, lang),
        "held_text": money(a.held, lang),
    }


def curve(state: State, region: str, product: str) -> dict | None:
    if not state.exchange.rounds:
        return None
    record = state.exchange.rounds[-1]
    demand = sorted(
        (
            (i.limit, i.quantity, i.live)
            for i in record.intents
            if i.region == region and i.product == product
        ),
        key=lambda x: -x[0],
    )
    supply = sorted(
        (
            (o.ask + freight_per_tonne(distance_km(o.region, region)), o.capacity, o.seller)
            for o in record.offers
            if o.product == product
        ),
        key=lambda x: x[0],
    )
    price = record.result.zone_prices.get((region, product))
    return {
        "region": region,
        "product": product,
        "price": price,
        "demand": [{"price": p, "tonnes": q, "live": live} for p, q, live in demand],
        "supply": [{"price": p, "tonnes": q, "seller": s} for p, q, s in supply],
    }


def market_view(state: State, lang: str, region: str, product: str) -> dict:
    ex = state.exchange
    waiting = sum(1 for lv in ex.live.values() if lv.status == "waiting")
    base = {
        "round": len(ex.rounds),
        "next_round": ex.next_round(),
        "waiting_live": waiting,
        "seconds_to_next": max(0, round(state.next_at - time.time())) if state.next_at else None,
        "products": [
            {"id": p.id, "name": p.uz if lang == "uz" else p.ru} for p in PRODUCTS.values()
        ],
    }
    if not ex.rounds:
        return base | {"zones": [], "stats": None, "shipments": [], "curve": None}
    record = ex.rounds[-1]
    previous = ex.rounds[-2] if len(ex.rounds) > 1 else None
    result = record.result
    zones = []
    for rid, r in REGIONS.items():
        row = {"id": rid, "name": r.uz if lang == "uz" else r.ru, "prices": {}}
        for pid in PRODUCTS:
            price = result.zone_prices.get((rid, pid))
            before = previous.result.zone_prices.get((rid, pid)) if previous else None
            row["prices"][pid] = {
                "value": price,
                "text": money(price, lang) if price else "—",
                "change": round((price - before) / before * 100, 1) if price and before else None,
            }
        zones.append(row)
    offers = {o.id: o for o in record.offers}
    pooled = sorted(
        (s for s in result.shipments if s.buyers > 1), key=lambda s: (-s.buyers, -s.tonnes)
    )
    shipments = [
        {
            "seller": offers[s.offer_id].seller,
            "from": region_name(offers[s.offer_id].region, lang),
            "to": region_name(s.region, lang),
            "product": product_name(offers[s.offer_id].product, lang),
            "buyers": s.buyers,
            "trucks": s.trucks,
            "tonnes": s.tonnes,
            "fill": s.fill,
        }
        for s in pooled[:8]
    ]
    fills = result.fills.values()
    stats = {
        "supply": round(sum(o.capacity for o in record.offers)),
        "demand": round(sum(i.quantity for i in record.intents)),
        "traded": round(result.traded),
        "buyers": len(record.intents),
        "sellers": len(record.offers),
        "matched": sum(1 for f in fills if f.filled),
        "pooled": len(pooled),
        "small": sum(1 for i in record.intents if i.quantity <= 10),
        "live": len(record.live_ids),
    }
    return base | {
        "zones": zones,
        "stats": stats,
        "shipments": shipments,
        "curve": curve(state, region, product),
    }


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    state = State(settings)

    async def ticker() -> None:
        while True:
            state.next_at = time.time() + settings.round_seconds
            await asyncio.sleep(settings.round_seconds)
            await asyncio.to_thread(state.exchange.clear_round)

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(ticker()) if settings.round_seconds > 0 else None
        yield
        if task:
            task.cancel()

    app = FastAPI(title="Niyat", lifespan=lifespan)
    app.state.niyat = state
    app.mount("/static", StaticFiles(directory=WEB), name="static")

    @app.get("/")
    def buyer_page():
        return FileResponse(WEB / "index.html")

    @app.get("/market")
    def market_page():
        return FileResponse(WEB / "market.html")

    @app.post("/api/chat")
    async def chat(body: ChatIn):
        if not body.message.strip():
            raise HTTPException(400, "empty")
        reply = await asyncio.to_thread(state.intake.handle, body.session, body.message, body.lang)
        return reply | {"account": account_view(state, body.session, reply["lang"])}

    @app.post("/api/submit")
    def submit(body: SessionIn):
        try:
            intent_id = state.intake.submit(body.session)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        live = state.exchange.live[intent_id]
        return {
            "intent": intent_view(live, state, body.lang),
            "account": account_view(state, body.session, body.lang),
        }

    @app.post("/api/new")
    def new_draft(body: SessionIn):
        state.intake.reset(body.session)
        return {"ok": True}

    @app.get("/api/intents")
    def intents(session: str, lang: str = "uz"):
        mine = [lv for lv in state.exchange.live.values() if lv.account_id == session]
        return {
            "intents": [intent_view(lv, state, lang) for lv in reversed(mine)],
            "account": account_view(state, session, lang),
            "next_round": state.exchange.next_round(),
        }

    @app.post("/api/intents/{intent_id}/cancel")
    def cancel(intent_id: str, lang: str = "uz"):
        try:
            live = state.exchange.cancel(intent_id)
        except (KeyError, ValueError) as error:
            raise HTTPException(409, str(error)) from error
        return {"intent": intent_view(live, state, lang)}

    @app.post("/api/intents/{intent_id}/delivered")
    def delivered(intent_id: str, lang: str = "uz"):
        try:
            live = state.exchange.confirm_delivery(intent_id)
        except (KeyError, ValueError) as error:
            raise HTTPException(409, str(error)) from error
        return {"intent": intent_view(live, state, lang)}

    @app.post("/api/round")
    async def run_round(lang: str = "uz"):
        record = await asyncio.to_thread(state.exchange.clear_round)
        if settings.round_seconds > 0:
            state.next_at = time.time() + settings.round_seconds
        return {"round": record.number, "traded": record.result.traded}

    @app.get("/api/market")
    def market(lang: str = "uz", region: str = "kashkadarya", product: str = "cement_325"):
        if region not in REGIONS or product not in PRODUCTS:
            raise HTTPException(404, "unknown")
        return market_view(state, lang, region, product)

    @app.post("/api/reset")
    def reset():
        state.reset()
        return {"ok": True}

    return app


app = create_app()
