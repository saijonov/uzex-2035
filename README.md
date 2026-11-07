# Bozor — UZEX 2035

Demo for the UZEX AI Hackathon 2026 final task "The Exchange of 2035 — Reinvent UZEX".

A phone app where anyone buys exchange goods like in a normal online shop: no broker, no terminal. It runs as a Telegram
Mini App inside the team bot and as an iPhone app (Expo).

Three screens:

- **Bozor.** Search, categories, price trend for each good, sellers with the price delivered to your city, buy.
- **AI yordamchi.** Write "Samarqandga 10 tonna shakar kerak". If no seller has 10 t, the app gathers it from several
  sellers, cheapest delivered first, and shows one card to confirm.
- **Xaridlarim.** Each purchase on a map: trucks moving along real roads from every seller to you. The money stays
  blocked on the exchange until you press "Yukni qabul qildim".

This is a demo, not a working product. Prices and sellers come from the hackathon registry (fictional data).

## Run

```bash
uv sync
uv run uvicorn bozor.app:app --app-dir src --port 8035
```

Open http://localhost:8035/ on a phone-sized window. Without `OPENAI_API_KEY` in `.env` the chat still works with
simple rules.

## More

- [How it works](docs/how-it-works.md)
- [Demo script and jury questions](docs/demo.md)
- [Hosting, Telegram and iPhone](docs/deploy.md)
