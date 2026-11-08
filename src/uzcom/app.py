from collections import Counter
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .broker import answer
from .settings import Settings


class Message(BaseModel):
    role: Literal["user", "assistant"]
    text: str = Field(min_length=1, max_length=1000)


class AskIn(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=12)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    usage: dict = {"day": date.today(), "total": 0, "users": Counter()}
    app = FastAPI(title="UzCom", docs_url=None, redoc_url=None, openapi_url=None)

    def may_use_model(user: str) -> bool:
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
        response.headers["Cache-Control"] = "no-cache"
        return response

    @app.post("/api/ai")
    def ai(body: AskIn, request: Request) -> dict:
        user = request.headers.get("cf-connecting-ip") or (
            request.client.host if request.client else "local"
        )
        messages = [m.model_dump() for m in body.messages]
        return answer(messages, settings, may_use_model(user))

    app.mount("/", StaticFiles(directory=Path(__file__).parent / "web", html=True), name="web")
    return app


app = create_app()
