# Niyat — UZEX 2035

Prototype for the UZEX AI Hackathon 2026 final task "The Exchange of 2035 — Reinvent UZEX".

A person says what they need in plain words ("Qarshiga juma kunigacha 60 qop M400 sement kerak"). The exchange turns
it into a confirmed intent, holds the money, clears all intents and offers together once per round with one delivered
price per region, pools small orders into shared trucks, and explains the result in Uzbek or Russian.

AI reads people. An open algorithm sets prices. Rules protect the buyer.

## Run

```bash
uv sync
uv run uvicorn niyat.app:app --app-dir src --port 8035
```

- Buyer screen: http://localhost:8035/
- Market screen for the projector: http://localhost:8035/market (`?lang=ru` for Russian)

Put `OPENAI_API_KEY` and `OPENAI_MODEL` in `.env` (see `.env.example`). Without a key the buyer screen still works with
the rule-based parser, so the demo never depends on the network.

Set `ROUND_SECONDS=60` in `.env` to clear a round automatically every minute. By default rounds run from the button on
the market screen.

## Tests

```bash
uv run pytest -q
uv run ruff check src tests
```

## Layout

| Path | What it does |
|---|---|
| `src/niyat/clearing.py` | One round: linear program for the best matches, lowest clearing prices, zone prices, pooled trucks |
| `src/niyat/market.py` | Simulated sellers and background buyers for each round, built from the seed file |
| `src/niyat/exchange.py` | Accounts, held money, rounds, settlement, delivery confirmation |
| `src/niyat/explain.py` | Plain explanation of each result in Uzbek and Russian |
| `src/niyat/ai_intake.py` | Reads a buyer message with one strict tool call |
| `src/niyat/rules_parser.py` | Rule-based reader used when the AI is off or fails |
| `src/niyat/intake.py` | Dialogue: one question at a time, then the confirmation card |
| `src/niyat/guardian.py` | Checks before sending: restricted goods, odd limits, deadlines, money |
| `src/niyat/app.py` | Web API and pages |
| `data/cement_market.json` | Seed built by `scripts/build_seed.py` from the fictional hackathon registry |

More in [docs/how-it-works.md](docs/how-it-works.md) and [docs/demo.md](docs/demo.md).

## Data

All market data is simulated from the fictional registry given in the qualifying round. Prices, sellers and buyers are
not real. Fees use the real UZEX tariff rates for a buyer (0.13% exchange fee and 0.05% clearing).
