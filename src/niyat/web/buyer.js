const T = {
  uz: {
    hello: "Assalomu alaykum! Nima kerakligini oddiy so‘z bilan yozing yoki ayting. Birja, lot, broker — hech narsani bilish shart emas.",
    examples: [
      "Qarshiga juma kunigacha 60 qop M400 sement kerak",
      "Toshkentga 5 tonna sement, tonnasi 1,1 mln dan oshmasin",
      "AI-80 benzin 10 tonna kerak",
    ],
    placeholder: "Masalan: Samarqandga 2 tonna sement kerak",
    send: "Yuborish",
    wallet: "Hisobingizda (simulyatsiya):",
    card: "Niyatingiz",
    product: "Mahsulot",
    quantity: "Miqdor",
    to: "Qayerga",
    by: "Muddat",
    limit: "Tonnasi uchun eng ko‘pi",
    hold: "Vaqtincha bloklanadi",
    market: "Hozirgi bozor narxi",
    confirm: "Tasdiqlash",
    edit: "O‘zgartirish",
    fine: "Pul faqat sement yetib kelgach zavodga o‘tadi. Siz chegarangizni emas, raunddagi bozor narxini to‘laysiz. Demo: E-IMZO o‘rniga tugma.",
    tonnes: (t, b) => `${t} t (${b} qop)`,
    until: (d) => `${d} gacha`,
    waiting: "Kutilmoqda",
    cancel: "Bekor qilish",
    delivered: "Yetib keldi",
    newIntent: "Yangi niyat",
    status: { waiting: "Raund kutilmoqda", matched: "Sotib olindi", partial: "Qisman sotib olindi", unmatched: "Sotib olinmadi", delivered: "Yetkazildi", cancelled: "Bekor qilindi" },
    round: (n) => `${n}-raund`,
    ai: "AI tushundi",
    rules: "qoidalar bilan tushunildi",
    error: "Xatolik. Qayta urinib ko‘ring.",
  },
  ru: {
    hello: "Здравствуйте! Напишите или скажите своими словами, что нужно. Биржу, лоты и брокеров знать не нужно.",
    examples: [
      "Нужно 60 мешков цемента М400 в Карши до пятницы",
      "5 тонн цемента в Ташкент, не дороже 1,1 млн за тонну",
      "Нужна пшеница 30 тонн",
    ],
    placeholder: "Например: 2 тонны цемента в Самарканд",
    send: "Отправить",
    wallet: "На счёте (симуляция):",
    card: "Ваше намерение",
    product: "Товар",
    quantity: "Объём",
    to: "Куда",
    by: "Срок",
    limit: "Максимум за тонну",
    hold: "Временно блокируется",
    market: "Цена рынка сейчас",
    confirm: "Подтвердить",
    edit: "Изменить",
    fine: "Деньги уйдут заводу только после доставки. Вы платите рыночную цену раунда, а не свой предел. Демо: кнопка вместо E-IMZO.",
    tonnes: (t, b) => `${t} т (${b} мешков)`,
    until: (d) => `до ${d}`,
    waiting: "Ожидание",
    cancel: "Отменить",
    delivered: "Доставлено",
    newIntent: "Новое намерение",
    status: { waiting: "Ждём раунд", matched: "Куплено", partial: "Куплено частично", unmatched: "Не куплено", delivered: "Доставлено", cancelled: "Отменено" },
    round: (n) => `раунд №${n}`,
    ai: "понято с помощью ИИ",
    rules: "понято по правилам",
    error: "Ошибка. Попробуйте ещё раз.",
  },
};

const params = new URLSearchParams(location.search);
let lang = params.get("lang") === "ru" ? "ru" : "uz";
const session = (() => {
  try {
    const saved = localStorage.getItem("niyat-session");
    if (saved) return saved;
    const id = "u" + Math.random().toString(36).slice(2, 10);
    localStorage.setItem("niyat-session", id);
    return id;
  } catch {
    return "u" + Math.random().toString(36).slice(2, 10);
  }
})();

const thread = document.getElementById("thread");
const input = document.getElementById("input");
const tracked = new Map();

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of [].concat(children)) if (c) node.append(c);
  return node;
}

function scroll() {
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

function say(text, who = "bot", source) {
  const bubble = el("div", { class: `msg ${who}`, text });
  if (source) bubble.append(el("span", { class: "src", text: T[lang][source] }));
  thread.append(bubble);
  scroll();
  return bubble;
}

async function api(path, body) {
  const res = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function setWallet(account) {
  if (!account) return;
  document.getElementById("wallet").textContent = account.balance_text;
}

function notices(list) {
  return list.map((n) =>
    el("div", { class: `notice ${n.level}` }, [el("span", { class: "ic", text: n.level === "block" ? "!" : "i" }), el("span", { text: n.text })])
  );
}

function renderCard(reply) {
  const t = T[lang];
  const c = reply.card;
  const rows = [
    [t.product, c.product],
    [t.quantity, t.tonnes(c.quantity, c.bags)],
    [t.to, c.region],
    [t.by, t.until(c.deadline_date)],
    [t.limit, c.limit_text],
    [t.market, c.reference_text || "—"],
    [t.hold, c.hold_text],
  ];
  const dl = el("dl");
  for (const [k, v] of rows) dl.append(el("dt", { text: k }), el("dd", { text: v }));
  const confirm = el("button", { class: "primary", text: t.confirm, onclick: () => submit(card, confirm) });
  confirm.disabled = !reply.can_submit;
  const card = el("div", { class: "card" }, [
    el("h3", { text: t.card }),
    dl,
    ...notices(reply.notices),
    el("div", { class: "actions" }, [el("button", { text: t.edit, onclick: () => input.focus() }), confirm]),
    el("div", { class: "fine", text: t.fine }),
  ]);
  thread.append(card);
  scroll();
}

async function send(text) {
  if (!text.trim()) return;
  say(text, "me");
  input.value = "";
  const typing = el("div", { class: "typing", text: "…" });
  thread.append(typing);
  try {
    const reply = await api("/api/chat", { session, message: text, lang });
    typing.remove();
    setWallet(reply.account);
    if (reply.question) say(reply.question, "bot", reply.source);
    else if (!reply.card && reply.notices.length) {
      const box = el("div", { class: "card" }, notices(reply.notices));
      thread.append(box);
      api("/api/new", { session, lang });
    }
    if (reply.card) renderCard(reply);
    else if (reply.question && reply.notices.length) thread.append(el("div", { class: "card" }, notices(reply.notices)));
  } catch {
    typing.remove();
    say(T[lang].error);
  }
  scroll();
}

async function submit(card, button) {
  button.disabled = true;
  try {
    const res = await api("/api/submit", { session, lang });
    setWallet(res.account);
    card.querySelector(".actions").remove();
    const holder = el("div", { class: "card result" });
    thread.append(holder);
    tracked.set(res.intent.id, holder);
    renderIntent(holder, res.intent);
    scroll();
  } catch {
    button.disabled = false;
    say(T[lang].error);
  }
}

function renderIntent(holder, intent) {
  const t = T[lang];
  holder.replaceChildren();
  const head = el("div", { style: "display:flex;justify-content:space-between;align-items:center;gap:8px" }, [
    el("span", { class: `status ${intent.status}`, text: t.status[intent.status] }),
    el("span", { class: "typing", text: intent.round ? t.round(intent.round) : "" }),
  ]);
  holder.append(head, el("div", { class: "headline", text: intent.explanation.headline }));
  if (intent.explanation.lines.length) {
    holder.append(el("ul", {}, intent.explanation.lines.map((line) => el("li", { text: line }))));
  }
  const actions = el("div", { class: "actions" });
  if (intent.status === "waiting") {
    actions.append(el("button", { text: t.cancel, onclick: () => act(intent.id, "cancel") }));
  }
  if (intent.status === "matched" || intent.status === "partial") {
    actions.append(el("button", { class: "primary", text: t.delivered, onclick: () => act(intent.id, "delivered") }));
  }
  if (!["waiting"].includes(intent.status)) {
    actions.append(el("button", { text: t.newIntent, onclick: () => { api("/api/new", { session, lang }); input.focus(); } }));
  }
  if (actions.children.length) holder.append(actions);
}

async function act(id, what) {
  try {
    const res = await api(`/api/intents/${id}/${what}?lang=${lang}`, {});
    renderIntent(tracked.get(id), res.intent);
    refresh();
  } catch {
    say(T[lang].error);
  }
}

async function refresh() {
  try {
    const data = await api(`/api/intents?session=${session}&lang=${lang}`);
    setWallet(data.account);
    for (const intent of [...data.intents].reverse()) {
      if (!tracked.has(intent.id)) {
        const created = el("div", { class: "card result" });
        thread.append(created);
        tracked.set(intent.id, created);
      }
      const holder = tracked.get(intent.id);
      if (holder && holder.dataset.status !== intent.status + intent.round) {
        holder.dataset.status = intent.status + intent.round;
        renderIntent(holder, intent);
        scroll();
      }
    }
  } catch {}
}

function start() {
  const t = T[lang];
  document.documentElement.lang = lang;
  document.querySelectorAll(".lang button").forEach((b) => b.classList.toggle("on", b.dataset.lang === lang));
  document.getElementById("wallet-label").textContent = t.wallet;
  document.getElementById("send").textContent = t.send;
  input.placeholder = t.placeholder;
  thread.replaceChildren();
  tracked.clear();
  say(t.hello);
  thread.append(el("div", { class: "chips" }, t.examples.map((x) => el("button", { type: "button", text: x, onclick: () => send(x) }))));
  api("/api/new", { session, lang });
  refresh();
}

document.querySelectorAll(".lang button").forEach((b) =>
  b.addEventListener("click", () => {
    lang = b.dataset.lang;
    start();
  })
);

document.getElementById("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  send(input.value);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send(input.value);
  }
});

const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (Recognition) {
  const mic = document.getElementById("mic");
  mic.hidden = false;
  let rec = null;
  mic.addEventListener("click", () => {
    if (rec) {
      rec.stop();
      return;
    }
    rec = new Recognition();
    rec.lang = lang === "ru" ? "ru-RU" : "uz-UZ";
    rec.interimResults = false;
    rec.onresult = (e) => send(e.results[0][0].transcript);
    rec.onend = () => {
      mic.classList.remove("on");
      rec = null;
    };
    mic.classList.add("on");
    rec.start();
  });
}

setInterval(refresh, 2000);
start();
