# Demo plan (3 minutes)

Open the bot on the phone, mirror the phone to the projector. Before going on stage press "Demo xaridlarni qaytadan
boshlash" in Xaridlarim so the cement truck is half way and the flour has arrived.

| Time | What to show |
|---|---|
| 0:00–0:20 | Today a small business needs a broker, a desktop terminal and a contract number to buy cement on UZEX. |
| 0:20–0:30 | Open the bot: two buttons, Xaridorman and Sotuvchiman. Pick Xaridorman. |
| 0:30–0:55 | Search "shakar": a year of prices, sellers with the price delivered to your city and how often they deliver on time. |
| 0:55–1:35 | AI: "Samarqandga 10 tonna shakar kerak". Nobody has 10 t; the AI gathers 5 + 2 + 3 t from three sellers. The card shows the shared-truck delivery next to what an own truck would cost. Confirm. |
| 1:35–1:55 | Map: three trucks driving to Samarqand on real roads. Money is blocked until you accept. |
| 1:55–2:10 | Flour page: "Birga olish" — a truck 15 of 20 t full, join with 5 t, delivery about 20× cheaper. |
| 2:10–2:45 | Switch to Sotuvchiman. Talab: what buyers lack, where, and what is left after delivery. Send an offer: "Xaridor puli bloklangan ✓". Press "Yukni jo'natdim". |
| 2:45–3:00 | 2035: buyers and sellers meet on the exchange directly. Many sellers → one buyer, many buyers → one truck, money safe on both sides. |

## Likely jury questions

- **Where do sellers come from?** They see demand the market cannot fill, with the buyer's money already blocked. They
  never chase a buyer for payment.
- **Is shared delivery real?** It is how groupage freight works. The app prices every order as a share of a 20 t truck and
  shows what an own truck would cost. Other buyers in the truck are demo data.

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
