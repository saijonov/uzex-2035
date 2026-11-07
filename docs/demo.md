# Demo plan (3 minutes)

Open the bot on the phone, mirror the phone to the projector. Before going on stage press "Demo xaridlarni qaytadan
boshlash" in Xaridlarim so the cement truck is half way and the flour has arrived.

| Time | What to show |
|---|---|
| 0:00–0:25 | Today a small business needs a broker, a desktop terminal and a contract number to buy cement on UZEX. |
| 0:25–1:00 | Bozor: search "shakar". Price chart for a year. Four sellers, each with the price delivered to your city and how often they deliver on time. |
| 1:00–1:50 | AI button: "Samarqandga 10 tonna shakar kerak". Nobody has 10 t. The AI gathers 5 + 2 + 3 t from three sellers, cheapest delivered first, with every fee shown. Confirm. |
| 1:50–2:25 | Map: three trucks from Namangan, Nurafshon and Andijon driving to Samarqand on real roads. The money is blocked on the exchange until you confirm. |
| 2:25–2:45 | Flour order: arrived, press "Yukni qabul qildim", money goes to the seller. |
| 2:45–3:00 | "10 tonna paxta kerak" is refused with the reason. 2035: every exchange good, one tap, no broker. |

## Likely jury questions

- **Isn't this just an online shop?** The shop part is on purpose: it is what people already know. What is new: one
  request is filled from many sellers, every price includes delivery, the money is held by the exchange until delivery,
  and no broker is needed.
- **Where do prices come from?** The hackathon registry (fictional data): weekly median price and each seller's recent
  median. Delivery is road km × 450 so'm per tonne, a rough rate.
- **What does the AI decide?** Nothing about money. It only reads the request into fields. The split, prices and fees
  are plain code that can be checked.
- **What if a seller doesn't deliver?** The money is still on the exchange, so the buyer is not paid out until they
  confirm. Sellers show their on-time share from past deals.
- **Why not buy cotton?** UZEX sells cotton only to companies that can process it. The app says so instead of taking
  the order.
- **Is the truck real?** In the demo it moves on the road route at 1 day = 2 minutes. In a real app the position comes
  from the carrier's GPS.
