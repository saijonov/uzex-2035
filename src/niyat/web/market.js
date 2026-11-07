const T = {
  uz: {
    round: (n) => (n ? `${n}-raund yakunlandi` : "Hali raund o‘tmadi"),
    clear: (n) => `${n}-raundni o‘tkazish`,
    next: (s) => `Keyingi raund: ${s} s`,
    tiles: [["sellers", "Zavodlar", ""], ["buyers", "Xaridorlar", ""], ["small", "Kichik xaridorlar", "≤10 t"], ["supply", "Taklif", "t"], ["demand", "Talab", "t"], ["traded", "Savdo", "t"], ["pooled", "Birlashtirilgan yuklar", ""], ["live", "Jonli niyatlar", ""]],
    zones: "Hududlar bo‘yicha yagona narx (tonnasi, yetkazib berish bilan)",
    region: "Hudud",
    price: "Narx",
    change: "O‘zgarish",
    chart: (r) => `${r}: narx qanday shakllandi`,
    chartSub: "Ko‘k — bu hududga yetkaza oladigan zavodlar (zavod narxi + yetkazish). To‘q sariq — shu hudud xaridorlari chegaralari. Uzuq chiziq — raund narxi.",
    supply: "Taklif",
    demand: "Talab",
    clearing: "Raund narxi",
    tonnes: "t",
    table: "Jadval ko‘rinishi",
    ships: "Birlashtirilgan yuklar: kichik buyurtmalar bitta mashinada",
    ship: (b, tr, t) => `${b} xaridor · ${tr} mashina · ${t} t`,
    noShips: "Hali birlashtirilgan yuk yo‘q.",
    empty: "Raundni o‘tkazing — narxlar shu yerda chiqadi.",
    foot: "Simulyatsiya: xakaton reyestridagi uydirma ma’lumotlar asosida. Narxni AI emas, ochiq algoritm belgilaydi: hamma niyatlar bir raundda yopiq holda yig‘iladi, eng katta umumiy foyda topiladi, har hududga bitta narx.",
    tipSupply: (s, p, q) => `${s}\n${p} · ${q} t`,
    tipDemand: (p, q, live) => `${live ? "Jonli niyat · " : ""}chegara ${p} · ${q} t`,
    live: "jonli",
  },
  ru: {
    round: (n) => (n ? `Раунд №${n} завершён` : "Раундов ещё не было"),
    clear: (n) => `Провести раунд №${n}`,
    next: (s) => `Следующий раунд: ${s} с`,
    tiles: [["sellers", "Заводы", ""], ["buyers", "Покупатели", ""], ["small", "Малые покупатели", "≤10 т"], ["supply", "Предложение", "т"], ["demand", "Спрос", "т"], ["traded", "Сделки", "т"], ["pooled", "Сборные грузы", ""], ["live", "Живые намерения", ""]],
    zones: "Единая цена по регионам (за тонну, с доставкой)",
    region: "Регион",
    price: "Цена",
    change: "Изм.",
    chart: (r) => `${r}: как сложилась цена`,
    chartSub: "Синяя — заводы, которые могут доставить в регион (цена завода + доставка). Оранжевая — пределы покупателей региона. Пунктир — цена раунда.",
    supply: "Предложение",
    demand: "Спрос",
    clearing: "Цена раунда",
    tonnes: "т",
    table: "Таблица",
    ships: "Сборные грузы: малые заказы в одной машине",
    ship: (b, tr, t) => `${b} покуп. · ${tr} маш. · ${t} т`,
    noShips: "Сборных грузов пока нет.",
    empty: "Проведите раунд — здесь появятся цены.",
    foot: "Симуляция на вымышленных данных реестра хакатона. Цену задаёт не ИИ, а открытый алгоритм: все намерения собираются в закрытый раунд, ищется максимальная общая выгода, у каждого региона одна цена.",
    tipSupply: (s, p, q) => `${s}\n${p} · ${q} т`,
    tipDemand: (p, q, live) => `${live ? "Живое намерение · " : ""}предел ${p} · ${q} т`,
    live: "живое",
  },
};

const params = new URLSearchParams(location.search);
let lang = params.get("lang") === "ru" ? "ru" : "uz";
let region = "kashkadarya";
let product = "cement_325";
let data = null;
const tip = document.getElementById("tip");

const fmt = (v) => Math.round(v).toLocaleString("ru-RU").replace(/ /g, " ");
const moneyShort = (v) => (v >= 1e6 ? (v / 1e6).toFixed(2).replace(".", ",") + (lang === "uz" ? " mln" : " млн") : fmt(v / 1000) + (lang === "uz" ? " ming" : " тыс"));

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of [].concat(children)) if (c !== null && c !== undefined) node.append(c);
  return node;
}

const SVG = "http://www.w3.org/2000/svg";
function s(tag, attrs = {}) {
  const node = document.createElementNS(SVG, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  return node;
}

async function load() {
  const res = await fetch(`/api/market?lang=${lang}&region=${region}&product=${product}`);
  data = await res.json();
  render();
}

function render() {
  const t = T[lang];
  document.documentElement.lang = lang;
  document.querySelectorAll(".lang button").forEach((b) => b.classList.toggle("on", b.dataset.lang === lang));
  document.getElementById("round").textContent = t.round(data.round);
  document.getElementById("clear").textContent = t.clear(data.next_round);
  document.getElementById("countdown").textContent = data.seconds_to_next != null ? t.next(data.seconds_to_next) : "";
  document.getElementById("zones-title").textContent = t.zones;
  document.getElementById("ship-title").textContent = t.ships;
  document.getElementById("table-label").textContent = t.table;
  document.getElementById("foot").textContent = t.foot;

  const products = document.getElementById("products");
  products.replaceChildren(
    ...data.products.map((p) => el("button", { class: p.id === product ? "on" : "", text: p.name.split(" (")[0], onclick: () => { product = p.id; load(); } }))
  );

  const tiles = document.getElementById("tiles");
  tiles.replaceChildren(
    ...t.tiles.map(([key, label, unit]) =>
      el("div", { class: "tile" }, [
        el("div", { class: "k", text: label }),
        el("div", { class: "v" }, [document.createTextNode(data.stats ? fmt(data.stats[key]) : "—"), unit ? el("span", { class: "u", text: unit }) : null]),
      ])
    )
  );

  renderZones();
  renderChart();
  renderShips();
}

function renderZones() {
  const t = T[lang];
  const table = document.getElementById("zones");
  if (!data.zones.length) {
    table.replaceChildren(el("tr", {}, el("td", { class: "empty", text: t.empty })));
    return;
  }
  const head = el("tr", {}, [el("th", { text: t.region }), el("th", { class: "n", text: t.price }), el("th", { class: "n", text: t.change })]);
  const rows = data.zones.map((z) => {
    const p = z.prices[product];
    const change = p.change;
    const delta = change == null ? "" : `${change > 0 ? "+" : ""}${change.toFixed(1).replace(".", ",")}%`;
    return el("tr", { class: `row${z.id === region ? " sel" : ""}`, onclick: () => { region = z.id; load(); } }, [
      el("td", { text: z.name }),
      el("td", { class: "n", text: p.text }),
      el("td", { class: "n" }, el("span", { class: `delta ${change > 0 ? "up" : change < 0 ? "down" : ""}`, text: delta })),
    ]);
  });
  table.replaceChildren(el("thead", {}, head), el("tbody", {}, rows));
}

function steps(points) {
  let x = 0;
  return points.map((p) => {
    const start = x;
    x += p.tonnes;
    return { ...p, x0: start, x1: x };
  });
}

function renderChart() {
  const t = T[lang];
  const zone = data.zones.find((z) => z.id === region);
  document.getElementById("chart-title").textContent = t.chart(zone ? zone.name : "");
  document.getElementById("chart-sub").textContent = t.chartSub;
  const legend = document.getElementById("legend");
  legend.replaceChildren(
    el("span", {}, [el("i", { style: "background:var(--series-1)" }), document.createTextNode(t.supply)]),
    el("span", {}, [el("i", { style: "background:var(--series-2)" }), document.createTextNode(t.demand)]),
    el("span", {}, [el("i", { class: "dash" }), document.createTextNode(t.clearing)])
  );
  const box = document.getElementById("chart");
  const tableBox = document.getElementById("chart-table");
  const c = data.curve;
  if (!c || !c.supply.length) {
    box.replaceChildren(el("div", { class: "empty", text: t.empty }));
    tableBox.replaceChildren();
    return;
  }
  const demand = steps(c.demand);
  const demandTotal = demand.length ? demand[demand.length - 1].x1 : 0;
  const xMax = Math.max(demandTotal * 1.6, 40);
  const supply = steps(c.supply).filter((p) => p.x0 < xMax);
  const prices = [...supply.map((p) => p.price), ...demand.map((p) => p.price), c.price].filter(Boolean);
  const yMin = Math.min(...prices) * 0.97;
  const yMax = Math.max(...prices) * 1.02;

  const W = 720, H = 360, L = 74, R = 16, TOP = 12, B = 34;
  const x = (v) => L + (Math.min(v, xMax) / xMax) * (W - L - R);
  const y = (v) => TOP + (1 - (v - yMin) / (yMax - yMin)) * (H - TOP - B);
  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": t.chart(zone ? zone.name : "") });

  const ticks = 5;
  for (let i = 0; i <= ticks; i++) {
    const v = yMin + ((yMax - yMin) * i) / ticks;
    svg.append(s("line", { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: "var(--border)", "stroke-width": 1 }));
    const label = s("text", { x: L - 8, y: y(v) + 4, "text-anchor": "end", "font-size": 11, fill: "var(--text-muted)" });
    label.textContent = moneyShort(v);
    svg.append(label);
  }
  for (let i = 0; i <= 4; i++) {
    const v = (xMax * i) / 4;
    const label = s("text", { x: x(v), y: H - 12, "text-anchor": "middle", "font-size": 11, fill: "var(--text-muted)" });
    label.textContent = `${Math.round(v)} ${t.tonnes}`;
    svg.append(label);
  }
  svg.append(s("line", { x1: L, x2: W - R, y1: H - B, y2: H - B, stroke: "var(--text-muted)", "stroke-width": 1 }));

  const path = (pts) => {
    let d = "";
    pts.forEach((p, i) => {
      d += `${i ? "L" : "M"}${x(p.x0)},${y(p.price)}L${x(p.x1)},${y(p.price)}`;
    });
    return d;
  };
  svg.append(s("path", { d: path(supply), fill: "none", stroke: "var(--series-1)", "stroke-width": 2, "stroke-linejoin": "round" }));
  if (demand.length) svg.append(s("path", { d: path(demand), fill: "none", stroke: "var(--series-2)", "stroke-width": 2, "stroke-linejoin": "round" }));

  if (c.price) {
    svg.append(s("line", { x1: L, x2: W - R, y1: y(c.price), y2: y(c.price), stroke: "var(--text-secondary)", "stroke-width": 1.5, "stroke-dasharray": "5 4" }));
    const label = s("text", { x: W - R - 4, y: y(c.price) - 6, "text-anchor": "end", "font-size": 12, "font-weight": 600, fill: "var(--text-primary)" });
    label.textContent = `${t.clearing}: ${fmt(c.price)}`;
    svg.append(label);
  }

  demand.filter((p) => p.live).forEach((p) => {
    svg.append(s("circle", { cx: x((p.x0 + p.x1) / 2), cy: y(p.price), r: 5, fill: "var(--series-2)", stroke: "var(--surface-1)", "stroke-width": 2 }));
  });

  const hit = (pts, kind) =>
    pts.forEach((p) => {
      const rect = s("rect", { x: x(p.x0), y: y(p.price) - 8, width: Math.max(x(p.x1) - x(p.x0), 6), height: 16, fill: "transparent" });
      rect.addEventListener("mousemove", (e) => {
        tip.hidden = false;
        tip.style.whiteSpace = "pre-line";
        tip.textContent = kind === "s" ? t.tipSupply(p.seller, fmt(p.price), p.tonnes) : t.tipDemand(fmt(p.price), p.tonnes, p.live);
        tip.style.left = e.clientX + 12 + "px";
        tip.style.top = e.clientY + 12 + "px";
      });
      rect.addEventListener("mouseleave", () => (tip.hidden = true));
      svg.append(rect);
    });
  hit(supply, "s");
  hit(demand, "d");
  box.replaceChildren(svg);

  const rows = [
    ...supply.map((p) => [t.supply, p.seller, fmt(p.price), p.tonnes]),
    ...demand.map((p) => [t.demand, p.live ? t.live : "", fmt(p.price), p.tonnes]),
  ];
  tableBox.replaceChildren(
    el("table", {}, [
      el("tr", {}, ["", "", t.price, t.tonnes].map((h) => el("th", { text: h }))),
      ...rows.map((r) => el("tr", {}, r.map((v) => el("td", { text: String(v) })))),
    ])
  );
}

function renderShips() {
  const t = T[lang];
  const box = document.getElementById("ships");
  if (!data.shipments.length) {
    box.replaceChildren(el("div", { class: "empty", text: t.noShips }));
    return;
  }
  box.replaceChildren(
    ...data.shipments.map((sh) =>
      el("div", { class: "ship" }, [
        el("div", { class: "route", text: `${sh.from} → ${sh.to}` }),
        el("div", { class: "meta", text: `${sh.product} · ${sh.seller}` }),
        el("div", { class: "meta", text: t.ship(sh.buyers, sh.trucks, sh.tonnes) }),
        el("div", { class: "bar-fill" }, el("span", { style: `width:${Math.round(sh.fill * 100)}%` })),
      ])
    )
  );
}

document.getElementById("clear").addEventListener("click", async (e) => {
  e.target.disabled = true;
  try {
    await fetch(`/api/round?lang=${lang}`, { method: "POST" });
    await load();
  } finally {
    e.target.disabled = false;
  }
});

document.querySelectorAll(".lang button").forEach((b) =>
  b.addEventListener("click", () => {
    lang = b.dataset.lang;
    load();
  })
);

setInterval(load, 2000);
load();
