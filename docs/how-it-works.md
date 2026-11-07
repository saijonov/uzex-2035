# How UzCom works

## Code

The app is three static files served by a small FastAPI server (`src/uzcom/app.py`).

- `web/index.html` holds every screen as a `<template>`, named like `Y1Home` or `N1Checkout`. The markup and styles are
  the team's design, unchanged.
- `web/app.js` has the logic of the five screens that react to taps: the chart and tonnes on the product page, the
  shared truck and payment on checkout, the target price for auto-buy, and the checklist and rating on arrival. Each one
  returns the values the template shows.
- A small renderer fills `{{value}}`, repeats `sc-for` blocks, shows `sc-if` blocks and wires `onClick` and `onChange`.
  After a tap it patches the page in place, so dragging a slider is never interrupted.
- A link to `#Name` opens that screen.

## Fitting the phone

The design is 390 × 844. The app scales it to the screen width. When the window is shorter (Telegram shows its own
header), the screen shrinks just enough that the content and the bottom buttons do not overlap. The map screen keeps
its full height, and its drawing continues past the design's right edge so it fills wider shapes too.

## Telegram

The Mini App opens full height with a white header. Telegram's back button appears on screens that have a back arrow
and does the same thing. Taps give a light vibration.

## Numbers

All numbers are demo values and agree with each other:

- cement M400 from the seller: 907 700 so'm a tonne;
- delivery in a shared truck: 18 000 so'm a tonne, 36 000 in an own truck, so 10 t is 180 000 cheaper shared;
- exchange fee 0.13% and clearing 0.05% of the goods value;
- price at the door: 907 700 + 18 000 + fees = 927 334 so'm a tonne; 10 t comes to 9 273 338 so'm;
- the 40 t order on the map: 37 093 354 so'm held on the exchange, two 20 t trucks;
- the chart has 52 weekly prices up to 26 October 2026, drawn from fixed key prices.

## Money

The buyer's money is frozen on the exchange when the order is confirmed. The seller is paid only after the buyer checks
the cargo and closes the order. If something is wrong, the money stays on the exchange and an inspector checks the
cargo.
