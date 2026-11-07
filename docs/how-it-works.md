# How Bozor works

## Data

`scripts/build_market.py` reads the hackathon registry (`registry.duckdb`, marked fictional by the organizers) and writes
`data/market.json`:

- 12 goods anyone may buy: cement, rebar, gypsum, lime, flour, sugar, rice, cottonseed oil, sunflower oil, salt, feed,
  polyethylene.
- Price history: weekly median price per tonne, 52 weeks up to 30 October 2026 (`amount_uzs / mass_t`).
- Sellers: up to 6 per good with at least 20 deals in 2026. For each seller:
  - price: median price per tonne since 1 August 2026;
  - deals: number of deals in 2026;
  - on time: share of 2026 deals delivered on or before the due date;
  - since: year of the seller's first deal;
  - grade and packaging: the most common product name and packaging, translated to Uzbek.
- Stock on sale is made up from the seller's typical deal size. Sugar is set to 5, 3, 3 and 2 t so that a 10 t order
  needs several sellers.

## Roads

`scripts/build_routes.py` asks the public OSRM router (OpenStreetMap roads) for the driving route between the 14
regional centres. Routes between the Fergana valley and the rest pass the Kamchik pass. Routes to Surxondaryo pass
G'uzor. Without those waypoints the router picked roads through Tajikistan. The script flags any route that passes
within 15 km of a city abroad; none do now.

## Price you pay

For each seller:

- delivery per tonne = road km × 450 so'm (a rough rate; no public per-km truck tariff was found);
- delivered price = seller price + delivery;
- days = 1 + km ÷ 450 (one day to load, 450 km a day).

Exchange fees on the goods value: 0.13% buyer fee and 0.05% clearing, the UZEX tariff from 1 October 2026.

## Gathering one order from several sellers

Sellers are sorted by delivered price. The order takes as much as each one has, cheapest first, until the amount is
reached. Delivery cost is per tonne, so this order is the cheapest possible.

- Not enough on the market: the buyer gets what exists, or nothing if "all or nothing" is on.
- One truck carries up to 20 t.

## AI

The chat makes one OpenAI call per message with a strict function schema: good, tonnes, region, all-or-nothing, a
restricted good, or an unknown good. The model only fills fields. Prices, sellers and totals come from the code above.
Rules read the same message as a fallback (bags of 50 kg, "mln", region names in Uzbek and Russian). Limits: 1,500 calls
a day in total and 40 per user.

Goods UZEX sells only to certain buyers (cotton, wheat, AI-80 petrol, alcohol, oil, gold and silver) are refused with
the reason.

## Purchases

Purchases are kept in the phone's browser storage. In the demo a day of driving takes 2 minutes. A truck's position is
the point along the road route at that share of the trip. In a real app it would come from the carrier's GPS.

Payment states: blocked on the exchange → loaded → arrived → buyer confirms → paid to sellers and carriers.

## Shared trucks (Birga olish)

A truck carries 20 t and costs road km × 9,000 so'm for the trip (450 so'm per tonne-km × 20 t).

- Shared: each buyer pays tonnes × km × 450, the share of a full truck. All prices in the app use this.
- Own truck: the whole trip, shown next to it so the saving is visible.
- Each product page shows a truck to your region that other buyers are filling (demo numbers: 6–15 t taken by 2–5
  buyers) and a button to join with the room that is left.

## Seller side

- **Requests.** For every good, the two regions where the cheapest delivered price is highest (furthest from sellers)
  get a buyer request. Tonnes and buyer count are demo numbers. The most a buyer pays is that delivered price plus
  1–5%. When a buyer presses "Kutaman" in the chat, the missing tonnes appear at the top of the seller list as "Yangi".
- **What is left for the seller:** the buyer's maximum minus delivery from the seller's warehouse.
- **Offer.** The seller sets tonnes and a warehouse price. Fees: 0.05% exchange and 0.05% clearing, the seller rates
  from 1 October 2026. If the price plus delivery is above the buyer's maximum, the offer cannot be sent.
- **Deal.** In the demo the buyer accepts at once. The buyer's money is shown as blocked on the exchange, the seller
  presses "Yukni jo'natdim", the truck moves on the map, and a few seconds after it arrives the buyer accepts and the
  payout lands.
- **Listing with AI.** The chat reads good, tonnes, warehouse region and price, then compares the price with the weekly
  market median (within 5% counts as in line) and names the nearest request for that good.
