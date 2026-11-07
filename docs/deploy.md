# Hosting, Telegram and iPhone

## Server

The app runs next to the bot on the team server with Docker. A Cloudflare quick tunnel gives it a public HTTPS address,
so no port has to be opened.

```bash
cd ~/bozor
docker compose up -d --build
docker compose logs tunnel | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | tail -1
```

`.env` needs `OPENAI_API_KEY` and `OPENAI_MODEL` (see `.env.example`). The quick tunnel address changes when the tunnel
restarts; set the bot button again after that.

## Telegram button

The bot itself is not changed. One Bot API call puts an "Bozor" button next to the message field for everyone:

```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setChatMenuButton" \
  -H 'content-type: application/json' \
  -d '{"menu_button": {"type": "web_app", "text": "Bozor", "web_app": {"url": "https://<address>.trycloudflare.com"}}}'
```

## iPhone

```bash
cd mobile
npm install
EXPO_PUBLIC_APP_URL=https://<address>.trycloudflare.com npx expo start
```

Scan the QR code with the iPhone camera; it opens in Expo Go. The app is a full-screen web view of the same address.
