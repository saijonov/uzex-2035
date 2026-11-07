# How Niyat works

## The idea

Today a buyer has to speak the exchange's language: contract numbers, lots, deposits, a broker, the order book, a
one-hour signing window. Niyat flips it: the buyer states an outcome in their own words, and the exchange does the rest.

Three layers:

1. **Say it.** AI turns a message into a draft intent: product, tonnes, delivery region, deadline, maximum price per
   tonne. It asks one missing thing at a time. The buyer confirms a plain card. The money for the maximum is held.
2. **Clear it.** Once per round all intents and all seller offers go into one sealed calculation. Nobody sees anyone
   else's order, so there is nothing to snipe or front-run.
3. **Explain and guard it.** Every buyer gets the price, where it came from, how much was saved against their limit,
   who shares their truck, and when it arrives. The seller is paid only after delivery is confirmed.

AI is used only at the edges (reading people, writing nothing that decides money). The price comes from a published
calculation. This follows a published finding that LLM pricing agents can drift to collusive prices
(Fish, Gonczarowski, Shorrer, arXiv 2404.00806).

## One round

Inputs:

- Offers: seller, plant region, product, tonnes available this round, asking price at the plant.
- Intents: buyer region, product, tonnes, maximum delivered price per tonne, deadline in days.

Delivery cost is `distance × 450 so'm per tonne-km`, distance is the straight line between region centres times 1.3,
40 km inside one region. Delivery takes one day per 450 km, plus one.

The engine solves a linear program: choose tonnes from each plant to each buyer to maximize total gain
`Σ (buyer limit − plant ask − delivery) × tonnes`, within plant capacity and buyer quantity, using only routes that
meet the buyer's deadline.

Prices come from the dual of that program. A second small linear program picks the **lowest** set of prices that still
supports the same matches, so a buyer never pays more than needed to clear the market. From those:

- Plant price = asking price + scarcity premium (zero when the plant did not sell out).
- A buyer's price = the cheapest plant price + delivery among the plants that can meet their deadline.
- Zone price = the same calculation for a region with no deadline limit. Everyone in a region pays one price.

Properties covered by tests:

- With enough supply the price is ask + delivery, and raising your limit does not raise your price.
- When supply is short, the cement goes to higher limits at the lowest clearing price.
- Money balances: what buyers pay equals what plants and carriers receive.
- Whole tonnes in give whole tonnes out.
- Small orders to the same region from the same plant are grouped into 20-tonne trucks.

This is the same family of mechanism as the European day-ahead power market (one closed auction, welfare maximized,
one price per bidding zone) and the frequent batch auctions proposed by Budish, Cramton and Shim (QJE 2015).

## Money

- On confirm: `tonnes × limit × (1 + 0.18%)` is held. 0.13% is the UZEX buyer fee and 0.05% is clearing, from the
  tariff in force from 1 October 2026.
- After the round: the buyer is charged `filled tonnes × price` plus fees, the rest is released.
- On delivery confirmation the seller and carrier are paid. No broker fee.

## Guardian

Before an intent goes in:

- Goods UZEX limits to certain buyers (AI-80 petrol, wheat, cotton fibre, alcohol, oil, gold and silver) are refused
  with the reason.
- Limits far below or far above the current regional price get a warning.
- Deadlines shorter than the fastest possible delivery get a warning.
- Not enough money stops the intent.

## Reading messages

`ai_intake.py` makes one Responses API call with a strict function schema. The model can only return fields; it never
writes prices or answers. The last question asked is included, so "1 mln 100 ming" after the price question becomes the
price limit. If there is no key, or the call fails, `rules_parser.py` reads the message with patterns (bags to tonnes,
weekdays to days, "mln" and "ming", region aliases).

## Limits of this prototype

- The market is simulated from the fictional registry. There is no live UZEX connection.
- Cement only, two grades (M400 ≈ CEM 32.5, M500 ≈ CEM 42.5).
- Delivery cost and time are rough formulas, not real logistics quotes.
- Partial fills are allowed; all-or-nothing orders would need integer programming.
- Signing with E-IMZO and real payments are shown as buttons.

## Trading real goods

The app lets an ordinary person trade, but every position is real goods.

- **Buy and keep.** An order with no delivery region buys at the plant price (no delivery cost). Each plant the order
  was filled from becomes a warehouse receipt in the portfolio: product, plant, tonnes, price paid.
- **Value.** A receipt is valued at the lowest plant price in its region from the last round. Profit or loss is that
  value minus what was paid.
- **Sell.** A sell order puts the receipt's tonnes into the next round as an offer at the seller's minimum price.
  The seller gets the round's plant price, which can be higher than the minimum. Fees: 0.05% exchange + 0.05% clearing.
- **Deliver.** A receipt can be sent to any region. The delivery cost is charged by distance.
- **Price index.** Each round records a price per product: the tonnage-weighted plant price of what traded, or the
  average plant price if nothing traded. The charts show this index.
- **Alerts.** A person can ask to be told when the index falls below or rises above a price.
- **Warm-up.** On start the server runs `WARMUP_ROUNDS` simulated rounds so the charts have history.

There is no borrowing and no short selling. The guardian adds a warning when one order uses more than half of the free
money.
