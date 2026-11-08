# UzCom pitch deck

13 slides, 1920 × 1080, built from the team style guide (Onest, white, yellow #FFDD2D, ink #111111).
`index.html` is in Russian and `uz.html` in Uzbek (Latin, with oʻ and gʻ). Both share `deck.css` and `deck.js`.
The app screenshots stay in Russian, as the app is.

| # | Slide |
|---|---|
| 1 | Title: UzCom with the AI broker, Команда 21, pixel Said with "Это другой Саид" |
| 2 | Problem: Said has 15 restaurants; today's path through two brokers |
| 3 | Solution: UzCom in Said's phone, AI broker included |
| 4 | Abroad: Pinduoduo, Full Truck Alliance, e-NAM |
| 5 | AI broker: advises, answers, checks, orders; two live screens of the app |
| 6–9 | App: choose, auto-buy, pay, track and accept |
| 10 | Why now and why us |
| 11 | Questions the jury may ask, answered first, including "what if the AI is wrong" |
| 12 | Team (replace the letters with photos) |
| 13 | Quote by Alan Kay, QR code to the bot |

## Open and present

```bash
cd pitch
python3 -m http.server 8037
```

Open http://localhost:8037 for Russian or http://localhost:8037/uz.html for Uzbek. Press F to present one slide at a time; arrows move, Esc leaves.

## Import into Figma

Use the html.to.design plugin with its Chrome extension on the open page. Every slide is its own 1920 × 1080 block,
so each one becomes a frame. Team photos: replace the letter circles on slide 11.

## AI broker slide

The two phones on slide 5 are not pictures: they are the app's own HTML, saved from real conversations with the AI
broker on 8 November 2026 (Russian in `index.html`, Uzbek in `uz.html`), so they stay sharp and editable in Figma.

## Pixel Said

`tools/said.py` draws the three poses and the papers as SVG in `img/pixel/`:

```bash
python3 tools/said.py img/pixel
```

## Sources for the numbers

- UZEX deals +31% in 2025: [UzA](https://uza.uz/ar/posts/2025-yilda-birja-savdolarida-4-3073-kg-oltin-va-3230-kg-kumush-sotildi_815944)
- Internet 94.2% of the population, August 2025: [Anhor](https://anhor.uz/news/uzbekistan-internet/)
- Click 71%, Payme 65%: [Uzum digital habits study](https://uzum.com/en/press-center/news-and-press-releases/first-digital-habits-study-of-uzbekistan-uzum-ecosystem-services-are-the-most-in-demand-digital-products-in-the-country/)
- Full Truck Alliance, 236.3 million fulfilled orders in 2025, +19.8%: [FY2025 results](https://www.barchart.com/story/news/707417/full-truck-alliance-co-ltd-announces-fourth-quarter-and-fiscal-year-2025-unaudited-financial-results)
- e-NAM, 1,656 mandis and 1.80 crore (18 million) farmers, March 2026: [Angel One on PIB data](https://www.angelone.in/news/economy/how-has-e-nam-reached-1656-mandis-and-1-80-crore-farmers-across-india)
- Pinduoduo, 16+ million farmers and 800+ million buyers (company statement): [FreshPlaza](https://www.freshplaza.com/north-america/article/9350524/pinduoduo-says-it-will-help-farmers-to-bring-out-full-value-by-building-agriculture-brands/)
- Buying on UZEX needs a broker contract, accreditation with an e-signature and money on the exchange deposit account:
  [Dogovor24](https://dogovor24.kz/questions/yuridicheskoe-lico-rezident-rk-reshilo-stat-uchastnikom-uzbekskoi-respublikanskoi-tovarno-syrevoi-birzhi-i-prodavat-na-nei-17794.html),
  [Buxgalter.uz](https://buxgalter.uz/ru/publish/doc/text168486_minfin_napomnil_o_vozmojnosti_uchastiya_v_birjevyh_torgah)

Screenshots of Pinduoduo, Yunmanman (Full Truck Alliance) and e-NAM were taken from their public websites on
8 November 2026. App prices and orders are the app's demo values.
