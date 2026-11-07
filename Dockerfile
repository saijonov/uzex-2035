FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --locked --no-dev --no-editable && useradd --uid 10001 --create-home app
USER app
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "uzcom.app:app", "--host", "0.0.0.0", "--port", "8000"]
