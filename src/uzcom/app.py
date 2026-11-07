from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="UzCom", docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def no_cache(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache"
    return response


app.mount("/", StaticFiles(directory=Path(__file__).parent / "web", html=True), name="web")
