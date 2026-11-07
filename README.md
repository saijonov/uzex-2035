# Niyat — UZEX 2035

Prototype for the UZEX AI Hackathon 2026 final task "The Exchange of 2035 — Reinvent UZEX".

A phone app where an ordinary person trades real goods on the exchange without a broker. Every position is real cement
in a plant warehouse, fully paid, no borrowed money. You can buy and keep it, sell it in a later round, or have it
delivered. An AI assistant takes plain requests in Uzbek or Russian.

AI reads people. An open algorithm sets prices. Rules protect the buyer.

## Run

```bash
uv sync
uv run uvicorn niyat.app:app --app-dir src --port 8035
```

- Phone app: http://localhost:8035/ (tabs: Bozor, Yordamchi, Portfel; `?lang=ru` for Russian)
- Market screen for the projector: http://localhost:8035/market

Settings in `.env` (see `.env.example`):

- `OPENAI_API_KEY`, `OPENAI_MODEL` for the assistant. Without a key the rule-based parser is used.
- `ROUND_SECONDS=30` clears a round every 30 seconds so prices move on their own. `0` means rounds run from the button.
- `WARMUP_ROUNDS=24` runs that many simulated rounds at start so the price charts have history.

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
| `src/niyat/exchange.py` | Accounts, held money, rounds, warehouse receipts, selling, delivery, price index, alerts |
| `src/niyat/explain.py` | Plain explanation of each result in Uzbek and Russian |
| `src/niyat/ai_intake.py` | Reads a message with one strict tool call |
| `src/niyat/rules_parser.py` | Rule-based reader used when the AI is off or fails |
| `src/niyat/intake.py` | Dialogue: one question at a time, then the confirmation card |
| `src/niyat/guardian.py` | Checks before an order: restricted goods, odd limits, deadlines, money, too much in one order |
| `src/niyat/app.py` | Web API and pages |
| `src/niyat/web/` | Phone app (`index.html`, `trade.js`, `buyer.js`) and the projector screen (`market.html`) |
| `data/cement_market.json` | Seed built by `scripts/build_seed.py` from the fictional hackathon registry |

More in [docs/how-it-works.md](docs/how-it-works.md) and [docs/demo.md](docs/demo.md).

## Data

All market data is simulated from the fictional registry given in the qualifying round. Prices, sellers and buyers are
not real. Fees use the real UZEX tariff rates: buyer 0.13% exchange fee, seller 0.05%, clearing 0.05% each side.
