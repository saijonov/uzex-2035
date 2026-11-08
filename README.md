# UzCom — UZEX 2035

Demo for the UZEX AI Hackathon 2026 final task "The Exchange of 2035 — Reinvent UZEX".

A phone app where anyone buys exchange goods like in a normal online shop: no broker, no terminal. It runs as a Telegram
Mini App inside the team bot and as an iPhone app (Expo). The screens are in Russian.

| Screen | What it shows |
|---|---|
| Рынок | Search, the order on its way, popular goods with the price per tonne and the change |
| Цемент М400 | Exchange price chart (3 months, 6 months, 1 year), price delivered to the door, tonnes, buy |
| Купить, когда подешевеет | Target price, tonnes and how long to wait; the app buys by itself |
| Подтверждение | Where and when, shared truck, every fee, Click / Payme / company account, confirm with MyID |
| Заказ принят | Money frozen on the exchange and the four next steps |
| Мои заказы | The current order with progress, and the price the app is waiting for |
| В пути | Map of the route, the driver, money held on the exchange |
| Заказ № 21-0412 | Deal, delivery, money and documents |
| Груз приехал | Checklist before accepting, close the order, rate the seller |
| AI-брокер | Opens from the search bar. Advises when to buy, checks sellers and prices, answers questions, prepares an order |

This is a demo, not a working product: the numbers are fixed demo values. The AI broker calls OpenAI when
`OPENAI_API_KEY` is set in `.env` (see `.env.example`) and falls back to simple rules otherwise.

## Run

```bash
uv sync
uv run uvicorn uzcom.app:app --app-dir src --port 8035
```

Open http://localhost:8035/ in a phone-sized window. Add a screen name to open it directly, for example
http://localhost:8035/#Y4Track.

```bash
uv run pytest
```

## More

- [How it works](docs/how-it-works.md)
- [Demo script and jury questions](docs/demo.md)
- [Hosting, Telegram and iPhone](docs/deploy.md)
