import asyncio
import contextlib
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from niyat.catalog import PRODUCTS, freight_per_tonne
from niyat.exchange import FEE_RATE, Exchange, LiveIntent
from niyat.explain import explain, explain_sell, money, product_name, region_name
from niyat.guardian import check_order
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


class OrderIn(BaseModel):
    session: str
    product: str
    tonnes: float
    limit: float
    region: str | None = None
    lang: str = "uz"
    preview: bool = False


class SellIn(BaseModel):
    session: str
    receipt: str
    tonnes: float
    min_price: float
    lang: str = "uz"


class DeliverIn(BaseModel):
    session: str
    region: str
    lang: str = "uz"


class AlertIn(BaseModel):
    session: str
    product: str
    direction: str
    price: float


WAREHOUSE = {"uz": "Zavod omborida", "ru": "На складе завода"}


class State:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.reset()
        self.next_at: float | None = None

    def reset(self) -> None:
        self.exchange = Exchange(warmup=self.settings.warmup_rounds)
        self.intake = Intake(self.exchange, self.settings)


def intent_view(live: LiveIntent, state: State, lang: str) -> dict:
    record = state.exchange.record(live.round) if live.round else None
    i = live.intent
    fill = live.fill
    return {
        "id": i.id,
        "status": live.status,
        "hold": live.hold,
        "product": product_name(i.product, lang),
        "quantity": i.quantity,
        "region": region_name(i.region, lang) if i.region else WAREHOUSE[lang],
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
        "balance": a.balance - a.held,
        "balance_text": money(a.balance - a.held, lang),
        "held_text": money(a.held, lang),
    }


def instruments_view(state: State, lang: str) -> list[dict]:
    ex = state.exchange
    rows = []
    for pid in PRODUCTS:
        history = ex.history(pid)
        price = ex.index_price(pid)
        before = history[-2]["price"] if len(history) > 1 else None
        record = ex.rounds[-1] if ex.rounds else None
        plants = []
        if record:
            for (rid, prod), value in sorted(
                record.plant_region_prices.items(), key=lambda kv: kv[1]
            ):
                if prod == pid:
                    plants.append(
                        {
                            "region": rid,
                            "name": region_name(rid, lang),
                            "price": value,
                            "text": money(value, lang),
                        }
                    )
        rows.append(
            {
                "id": pid,
                "name": product_name(pid, lang),
                "price": price,
                "price_text": money(price, lang) if price else "—",
                "change": round((price - before) / before * 100, 2) if price and before else None,
                "history": history[-40:],
                "plants": plants,
            }
        )
    return rows


def sell_view(order, state: State, lang: str) -> dict:
    receipt = state.exchange.receipts[order.receipt_id]
    return {
        "id": order.id,
        "status": order.status,
        "product": product_name(order.product, lang),
        "plant": receipt.plant,
        "region": region_name(order.region, lang),
        "tonnes": order.tonnes,
        "round": order.round,
        "explanation": explain_sell(order, lang, state.exchange.next_round()),
    }


def portfolio_view(state: State, session: str, lang: str) -> dict:
    ex = state.exchange
    holdings = []
    total_value = total_pnl = 0.0
    for row in ex.portfolio(session):
        r = row["receipt"]
        total_value += row["value"]
        total_pnl += row["pnl"]
        holdings.append(
            {
                "id": r.id,
                "product": product_name(r.product, lang),
                "product_id": r.product,
                "plant": r.plant,
                "region": region_name(r.region, lang),
                "tonnes": r.tonnes,
                "free": r.free,
                "status": r.status,
                "cost_text": money(r.cost, lang),
                "mark": row["mark"],
                "mark_text": money(row["mark"], lang) if row["mark"] else "—",
                "value_text": money(row["value"], lang),
                "pnl": row["pnl"],
                "pnl_text": money(abs(row["pnl"]), lang),
                "eta": r.eta.strftime("%d.%m.%Y") if r.eta else None,
                "delivery_region": region_name(r.delivery_region, lang)
                if r.delivery_region
                else None,
            }
        )
    mine = [lv for lv in ex.live.values() if lv.account_id == session]
    sells = [s for s in ex.sells.values() if s.account_id == session]
    alerts = [a for a in ex.alerts.values() if a.account_id == session]
    return {
        "account": account_view(state, session, lang),
        "value_text": money(total_value, lang),
        "pnl": round(total_pnl, 2),
        "pnl_text": money(abs(total_pnl), lang),
        "holdings": holdings,
        "intents": [intent_view(lv, state, lang) for lv in reversed(mine)],
        "sells": [sell_view(s, state, lang) for s in reversed(sells)],
        "alerts": [
            {
                "id": a.id,
                "product": product_name(a.product, lang),
                "direction": a.direction,
                "price_text": money(a.price, lang),
                "status": a.status,
                "round": a.round,
                "value_text": money(a.value, lang) if a.value else None,
            }
            for a in reversed(alerts)
        ],
        "next_round": ex.next_round(),
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

    @app.middleware("http")
    async def no_stale_pages(request, call_next):
        response = await call_next(request)
        if not request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache"
        return response

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

    @app.get("/api/instruments")
    def instruments(lang: str = "uz"):
        return {
            "instruments": instruments_view(state, lang),
            "round": len(state.exchange.rounds),
            "next_round": state.exchange.next_round(),
            "seconds_to_next": max(0, round(state.next_at - time.time()))
            if state.next_at
            else None,
            "regions": [{"id": rid, "name": region_name(rid, lang)} for rid in REGIONS],
        }

    @app.post("/api/order")
    def order(body: OrderIn):
        if body.product not in PRODUCTS or (body.region and body.region not in REGIONS):
            raise HTTPException(404, "unknown")
        if body.tonnes <= 0 or body.limit <= 0:
            raise HTTPException(400, "bad_numbers")
        notices = check_order(
            state.exchange,
            body.session,
            body.product,
            body.tonnes,
            body.limit,
            body.region,
            body.lang,
        )
        hold = body.tonnes * body.limit * (1 + FEE_RATE)
        summary = {"hold": hold, "hold_text": money(hold, body.lang), "notices": notices}
        if body.preview or any(n["level"] == "block" for n in notices):
            return summary | {"submitted": False}
        live = state.exchange.submit(
            body.session, body.region, body.product, body.tonnes, body.limit, 7
        )
        return summary | {
            "submitted": True,
            "intent": intent_view(live, state, body.lang),
            "account": account_view(state, body.session, body.lang),
        }

    @app.post("/api/sell")
    def sell(body: SellIn):
        try:
            order = state.exchange.sell(body.session, body.receipt, body.tonnes, body.min_price)
        except (KeyError, ValueError) as error:
            raise HTTPException(409, str(error)) from error
        return {"sell": sell_view(order, state, body.lang)}

    @app.post("/api/sells/{order_id}/cancel")
    def cancel_sell(order_id: str, lang: str = "uz"):
        try:
            order = state.exchange.cancel_sell(order_id)
        except (KeyError, ValueError) as error:
            raise HTTPException(409, str(error)) from error
        return {"sell": sell_view(order, state, lang)}

    @app.post("/api/receipts/{receipt_id}/deliver")
    def deliver(receipt_id: str, body: DeliverIn):
        if body.region not in REGIONS:
            raise HTTPException(404, "unknown")
        try:
            state.exchange.deliver(body.session, receipt_id, body.region)
        except (KeyError, ValueError) as error:
            raise HTTPException(409, str(error)) from error
        return portfolio_view(state, body.session, body.lang)

    @app.post("/api/alerts")
    def alert(body: AlertIn):
        try:
            a = state.exchange.add_alert(body.session, body.product, body.direction, body.price)
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        return {"id": a.id}

    @app.get("/api/portfolio")
    def portfolio(session: str, lang: str = "uz"):
        return portfolio_view(state, session, lang)

    @app.post("/api/reset")
    def reset():
        state.reset()
        return {"ok": True}

    return app


app = create_app()
