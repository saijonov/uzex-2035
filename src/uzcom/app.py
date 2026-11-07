import logging
from collections import Counter
from dataclasses import asdict, fields
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .chat import Draft, ai, listing_reply, reply, rules
from .goods import CLEARING_FEE, EXCHANGE_FEE, FREIGHT_PER_TONNE_KM, GOODS, TRUCK_TONNES
from .market import Market
from .regions import REGIONS
from .settings import Settings

WEB = Path(__file__).parent / "web"
log = logging.getLogger("uzcom")


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    region: str
    draft: dict | None = None
    asked: str | None = None
    role: Literal["buyer", "seller"] = "buyer"


class Want(BaseModel):
    good: str
    region: str
    tonnes: int = Field(ge=1, le=1000)


class DemandIn(BaseModel):
    region: str
    wants: list[Want] = Field(default_factory=list, max_length=20)


class SaleIn(BaseModel):
    good: str
    tonnes: int = Field(ge=1, le=1000)
    price: int = Field(ge=1, le=10_000_000_000)
    home: str
    region: str


class PlanIn(BaseModel):
    good: str
    tonnes: int = Field(ge=1, le=1000)
    region: str
    whole: bool = False
    seller: str | None = None


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    market = Market(settings.data_dir)
    usage: dict = {"day": date.today(), "total": 0, "users": Counter()}
    app = FastAPI(title="UzCom", docs_url=None, redoc_url=None)

    def region_of(region: str) -> str:
        if region not in REGIONS:
            raise HTTPException(400, "unknown region")
        return region

    def good_of(good: str) -> str:
        if good not in GOODS:
            raise HTTPException(404, "unknown good")
        return good

    def may_use_ai(user: str) -> bool:
        if usage["day"] != date.today():
            usage.update(day=date.today(), total=0, users=Counter())
        if not settings.openai_api_key.get_secret_value():
            return False
        if (
            usage["total"] >= settings.ai_daily_limit
            or usage["users"][user] >= settings.ai_per_user_limit
        ):
            return False
        usage["total"] += 1
        usage["users"][user] += 1
        return True

    @app.middleware("http")
    async def no_cache(request: Request, call_next):
        response = await call_next(request)
        if not request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache"
        return response

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB / "index.html")

    @app.get("/api/meta")
    def meta() -> dict:
        return {
            "as_of": market.as_of,
            "regions": [
                {"id": r.id, "name": r.name, "city": r.city, "lat": r.lat, "lon": r.lon}
                for r in REGIONS.values()
            ],
            "exchange_fee": EXCHANGE_FEE,
            "clearing_fee": CLEARING_FEE,
            "freight": FREIGHT_PER_TONNE_KM,
            "truck": TRUCK_TONNES,
        }

    @app.get("/api/goods")
    def goods(region: str) -> list[dict]:
        return [market.summary(g, region_of(region)) for g in GOODS]

    @app.get("/api/goods/{good}")
    def good(good: str, region: str) -> dict:
        return market.detail(good_of(good), region_of(region))

    @app.post("/api/plan")
    def plan(body: PlanIn) -> dict:
        if body.seller and market.sellers.get(body.seller, {}).get("good") != body.good:
            raise HTTPException(404, "unknown seller")
        return market.plan(
            good_of(body.good), body.tonnes, region_of(body.region), body.whole, body.seller
        )

    @app.get("/api/demo")
    def demo(region: str) -> list[dict]:
        region = region_of(region)
        far = max(REGIONS, key=lambda r: market.route(r, region)["km"] if r != region else 0)
        cement = market.plan("cement", 40, region, seller=market.offers("cement", far)[0]["id"])
        flour = market.plan("flour", 5, region)
        return [{"plan": cement, "progress": 0.55}, {"plan": flour, "progress": 1.0}]

    @app.post("/api/demand")
    def demand(body: DemandIn) -> list[dict]:
        wants = [w.model_dump() for w in body.wants if w.good in GOODS and w.region in REGIONS]
        return market.requests(region_of(body.region), wants)

    @app.post("/api/sale")
    def sale(body: SaleIn) -> dict:
        return market.sale(
            good_of(body.good),
            body.tonnes,
            body.price,
            region_of(body.home),
            region_of(body.region),
        )

    @app.get("/api/seller-demo")
    def seller_demo(region: str) -> dict:
        home = region_of(region)
        first, second = market.requests(home)[:2]
        deals = [
            {
                "sale": market.sale(
                    r["good"], min(r["tonnes"], 20), r["net"] // 1000 * 1000, home, r["region"]
                ),
                "progress": p,
            }
            for r, p in ((first, None), (second, 0.4))
        ]
        index = market.index("cement")
        listing = {
            "good": "cement",
            "good_name": GOODS["cement"].name,
            "tonnes": 60,
            "price": index // 1000 * 1000,
            "region": home,
            "city": REGIONS[home].city,
            "index": index,
            "diff": round((index // 1000 * 1000) / index - 1, 3),
        }
        return {"deals": deals, "listings": [listing]}

    @app.post("/api/chat")
    def chat(body: ChatIn, request: Request) -> dict:
        draft = Draft(**{f.name: (body.draft or {}).get(f.name, f.default) for f in fields(Draft)})
        draft.region = draft.region or region_of(body.region)
        found = rules(body.message, body.asked)
        user = request.headers.get("cf-connecting-ip") or (
            request.client.host if request.client else "local"
        )
        if may_use_ai(user):
            try:
                found = {**found, **ai(body.message, draft, body.asked, settings, body.role)}
            except Exception as error:
                log.warning("AI parse failed: %s", type(error).__name__)
        if found.get("good") not in (None, *GOODS):
            found.pop("good")
        if "good" in found:
            found.pop("restricted", None)
            found.pop("other", None)
        if {"good", "restricted", "other"} & found.keys():
            draft.good, draft.restricted, draft.other = (
                found.get("good"),
                found.get("restricted"),
                found.get("other"),
            )
        for key in ("tonnes", "region", "whole", "price"):
            if key in found:
                setattr(draft, key, found[key])
        if body.role == "seller":
            text, asked, listing = listing_reply(draft, market)
            plan = None
        else:
            text, asked, plan = reply(draft, market)
            listing = None
        draft.restricted = draft.other = None
        return {
            "reply": text,
            "asked": asked,
            "draft": asdict(draft),
            "plan": plan,
            "listing": listing,
        }

    app.mount("/", StaticFiles(directory=WEB), name="web")
    return app


app = create_app()
