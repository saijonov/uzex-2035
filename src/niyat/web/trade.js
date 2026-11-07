(() => {
  const TT = {
    uz: {
      tabs: { market: "Bozor", chat: "Yordamchi", folio: "Portfel" },
      roundLine: (n, s) => `${n}-raund yakunlandi${s != null ? ` · keyingisi ${s} s` : ""}`,
      perT: "tonnasi",
      market: "Tovarlar narxi (zavod omborida, tonnasi)",
      back: "← Bozor",
      buy: "Sotib olish",
      sell: "Sotish",
      alert: "Narx ogohlantirishi",
      plants: "Zavodlar bo‘yicha narx",
      chartLabel: "Raundlar bo‘yicha narx",
      round: "raund",
      howTo: "Qarz yo‘q, faqat bor pulingiz. Har raundda hamma uchun bitta narx.",
      buyTitle: (n) => `${n}: sotib olish`,
      tonnes: "Necha tonna? (1 qop = 50 kg)",
      limit: "Tonnasi uchun eng ko‘pi (so‘m)",
      mode: "Tovar qayerda tursin?",
      keep: "Zavod omborida",
      deliver: "Uyga yetkazish",
      region: "Qayerga yetkazish",
      held: "Vaqtincha bloklanadi",
      confirm: "Tasdiqlash",
      cancel: "Yopish",
      sellTitle: (n) => `${n}: sotish`,
      which: "Qaysi tovaringiz",
      minPrice: "Tonnasi uchun eng kami (so‘m)",
      sellNote: "Siz eng kam narxni emas, raunddagi bozor narxini olasiz.",
      noGoods: "Bu tovardan portfelingizda hech narsa yo‘q. Avval sotib oling.",
      alertTitle: (n) => `${n}: narx ogohlantirishi`,
      below: "Tushsa",
      above: "Oshsa",
      alertPrice: "Narx (so‘m)",
      alertSaved: "Ogohlantirish qo‘yildi.",
      placed: "Buyurtma qabul qilindi. Natija keyingi raunddan keyin Portfelda.",
      sellPlaced: "Sotuvga qo‘yildi. Natija keyingi raunddan keyin.",
      available: "Bo‘sh pul",
      goods: "Tovarlar qiymati",
      pnl: "Foyda / zarar",
      holdings: "Mening tovarlarim",
      orders: "Buyurtmalar",
      sells: "Sotuvlar",
      alerts: "Ogohlantirishlar",
      nothing: "Hozircha bo‘sh.",
      at: (p) => `${p} narxda`,
      cost: (c, m) => `Olingan: ${c} · hozir: ${m}`,
      onSale: (t) => `${t} t sotuvda`,
      delivering: (r, d) => `${r} ga yo‘lda · ${d}`,
      deliverTitle: "Uyga yetkazish",
      deliverNote: "Yetkazish narxi masofaga qarab hisobdan yechiladi.",
      fired: (v, r) => `Ishladi: ${r}-raundda narx ${v}`,
      waitingAlert: "Kutilmoqda",
      dirBelow: (p) => `${p} dan tushsa`,
      dirAbove: (p) => `${p} dan oshsa`,
      error: "Xatolik. Qayta urinib ko‘ring.",
      status: { waiting: "kutilmoqda", matched: "bajarildi", partial: "qisman", unmatched: "bajarilmadi", delivered: "yetkazildi", cancelled: "bekor", sold: "sotildi", unsold: "sotilmadi" },
    },
    ru: {
      tabs: { market: "Рынок", chat: "Помощник", folio: "Портфель" },
      roundLine: (n, s) => `Раунд №${n} завершён${s != null ? ` · следующий через ${s} с` : ""}`,
      perT: "за тонну",
      market: "Цены товаров (на складе завода, за тонну)",
      back: "← Рынок",
      buy: "Купить",
      sell: "Продать",
      alert: "Уведомление о цене",
      plants: "Цены по заводам",
      chartLabel: "Цена по раундам",
      round: "раунд",
      howTo: "Без кредитного плеча, только ваши деньги. Одна цена для всех в каждом раунде.",
      buyTitle: (n) => `${n}: покупка`,
      tonnes: "Сколько тонн? (1 мешок = 50 кг)",
      limit: "Максимум за тонну (сум)",
      mode: "Где хранить товар?",
      keep: "На складе завода",
      deliver: "Доставить",
      region: "Куда доставить",
      held: "Временно блокируется",
      confirm: "Подтвердить",
      cancel: "Закрыть",
      sellTitle: (n) => `${n}: продажа`,
      which: "Какой товар",
      minPrice: "Минимум за тонну (сум)",
      sellNote: "Вы получаете рыночную цену раунда, а не свой минимум.",
      noGoods: "Этого товара нет в портфеле. Сначала купите.",
      alertTitle: (n) => `${n}: уведомление`,
      below: "Упадёт ниже",
      above: "Вырастет выше",
      alertPrice: "Цена (сум)",
      alertSaved: "Уведомление создано.",
      placed: "Заявка принята. Результат после следующего раунда в Портфеле.",
      sellPlaced: "Выставлено на продажу. Результат после следующего раунда.",
      available: "Свободно",
      goods: "Стоимость товаров",
      pnl: "Прибыль / убыток",
      holdings: "Мои товары",
      orders: "Заявки",
      sells: "Продажи",
      alerts: "Уведомления",
      nothing: "Пока пусто.",
      at: (p) => `по ${p}`,
      cost: (c, m) => `Куплено: ${c} · сейчас: ${m}`,
      onSale: (t) => `${t} т на продаже`,
      delivering: (r, d) => `в пути: ${r} · ${d}`,
      deliverTitle: "Доставка",
      deliverNote: "Стоимость доставки по расстоянию списывается со счёта.",
      fired: (v, r) => `Сработало: в раунде №${r} цена ${v}`,
      waitingAlert: "Ожидает",
      dirBelow: (p) => `ниже ${p}`,
      dirAbove: (p) => `выше ${p}`,
      error: "Ошибка. Попробуйте ещё раз.",
      status: { waiting: "ожидает", matched: "исполнено", partial: "частично", unmatched: "не исполнено", delivered: "доставлено", cancelled: "отменено", sold: "продано", unsold: "не продано" },
    },
  };

  const url = new URLSearchParams(location.search);
  const L = url.get("lang") === "ru" ? "ru" : "uz";
  const t = TT[L];
  const sid = (() => {
    try {
      return localStorage.getItem("niyat-session") || "anon";
    } catch {
      return "anon";
    }
  })();
  let tab = url.get("tab") || "market";
  let selected = null;
  let data = null;
  let folio = null;
  const tip = document.getElementById("tip");
  const fmt = (v) => Math.round(v).toLocaleString("ru-RU").replace(/ /g, " ");
  const short = (v) => (v >= 1e6 ? (v / 1e6).toFixed(3).replace(".", ",") + (L === "uz" ? " mln" : " млн") : fmt(v));

  function h(tag, attrs = {}, kids = []) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v === undefined || v === null) continue;
      if (k === "class") n.className = v;
      else if (k === "text") n.textContent = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    }
    for (const c of [].concat(kids)) if (c !== null && c !== undefined && c !== false) n.append(c);
    return n;
  }
  const S = "http://www.w3.org/2000/svg";
  function s(tag, attrs = {}) {
    const n = document.createElementNS(S, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    return n;
  }

  async function call(path, body) {
    const res = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  function toast(text) {
    const n = h("div", { class: "toast", text });
    document.body.append(n);
    setTimeout(() => n.remove(), 3200);
  }

  function change(c) {
    if (c == null) return h("div", { class: "chg", text: "" });
    const text = `${c > 0 ? "+" : ""}${c.toFixed(2).replace(".", ",")}%`;
    return h("div", { class: `chg ${c > 0 ? "up" : c < 0 ? "down" : ""}`, text });
  }

  function spark(history) {
    const svg = s("svg", { viewBox: "0 0 300 44", preserveAspectRatio: "none", "aria-hidden": "true" });
    if (history.length < 2) return svg;
    const ys = history.map((p) => p.price);
    const lo = Math.min(...ys), hi = Math.max(...ys), span = hi - lo || 1;
    const pts = history.map((p, i) => `${(i / (history.length - 1)) * 300},${40 - ((p.price - lo) / span) * 36}`).join(" ");
    svg.append(s("polyline", { points: pts, fill: "none", stroke: "var(--series-1)", "stroke-width": 2, "stroke-linejoin": "round", "vector-effect": "non-scaling-stroke" }));
    return svg;
  }

  function lineChart(history) {
    const W = 420, H = 220, Lp = 64, R = 10, T = 10, B = 26;
    const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": t.chartLabel });
    if (history.length < 2) return svg;
    const ys = history.map((p) => p.price);
    const lo = Math.min(...ys) * 0.995, hi = Math.max(...ys) * 1.005;
    const x = (i) => Lp + (i / (history.length - 1)) * (W - Lp - R);
    const y = (v) => T + (1 - (v - lo) / (hi - lo)) * (H - T - B);
    for (let k = 0; k <= 4; k++) {
      const v = lo + ((hi - lo) * k) / 4;
      svg.append(s("line", { x1: Lp, x2: W - R, y1: y(v), y2: y(v), stroke: "var(--border)", "stroke-width": 1 }));
      const lab = s("text", { x: Lp - 6, y: y(v) + 4, "text-anchor": "end", "font-size": 10, fill: "var(--text-muted)" });
      lab.textContent = short(v);
      svg.append(lab);
    }
    [0, history.length - 1].forEach((i) => {
      const lab = s("text", { x: x(i), y: H - 8, "text-anchor": i ? "end" : "start", "font-size": 10, fill: "var(--text-muted)" });
      lab.textContent = `${history[i].round}-${t.round}`;
      svg.append(lab);
    });
    const pts = history.map((p, i) => `${x(i)},${y(p.price)}`).join(" ");
    svg.append(s("polyline", { points: pts, fill: "none", stroke: "var(--series-1)", "stroke-width": 2, "stroke-linejoin": "round" }));
    const last = history[history.length - 1];
    svg.append(s("circle", { cx: x(history.length - 1), cy: y(last.price), r: 4, fill: "var(--series-1)", stroke: "var(--surface-1)", "stroke-width": 2 }));
    const cross = s("line", { y1: T, y2: H - B, stroke: "var(--text-muted)", "stroke-width": 1, visibility: "hidden" });
    const dot = s("circle", { r: 4, fill: "var(--series-1)", stroke: "var(--surface-1)", "stroke-width": 2, visibility: "hidden" });
    svg.append(cross, dot);
    const hit = s("rect", { x: Lp, y: T, width: W - Lp - R, height: H - T - B, fill: "transparent" });
    hit.addEventListener("mousemove", (e) => {
      const box = svg.getBoundingClientRect();
      const px = ((e.clientX - box.left) / box.width) * W;
      const i = Math.max(0, Math.min(history.length - 1, Math.round(((px - Lp) / (W - Lp - R)) * (history.length - 1))));
      const p = history[i];
      cross.setAttribute("x1", x(i));
      cross.setAttribute("x2", x(i));
      cross.setAttribute("visibility", "visible");
      dot.setAttribute("cx", x(i));
      dot.setAttribute("cy", y(p.price));
      dot.setAttribute("visibility", "visible");
      tip.hidden = false;
      tip.textContent = `${p.round}-${t.round}: ${fmt(p.price)}`;
      tip.style.left = e.clientX + 12 + "px";
      tip.style.top = e.clientY - 28 + "px";
    });
    hit.addEventListener("mouseleave", () => {
      tip.hidden = true;
      cross.setAttribute("visibility", "hidden");
      dot.setAttribute("visibility", "hidden");
    });
    svg.append(hit);
    return svg;
  }

  function renderMarket() {
    const box = document.getElementById("tab-market");
    if (!data) return;
    const line = h("div", { class: "round-line" }, [h("span", { text: t.roundLine(data.round, data.seconds_to_next) })]);
    if (!selected) {
      box.replaceChildren(
        line,
        h("div", { class: "sub", text: t.market }),
        ...data.instruments.map((i) =>
          h("div", { class: "inst", onclick: () => { selected = i.id; renderMarket(); } }, [
            h("div", {}, [h("div", { class: "name", text: i.name }), h("div", { class: "unit", text: t.perT })]),
            h("div", {}, [h("div", { class: "px", text: i.price_text }), change(i.change)]),
            spark(i.history),
          ])
        ),
        h("div", { class: "fine", text: t.howTo })
      );
      return;
    }
    const i = data.instruments.find((x) => x.id === selected);
    box.replaceChildren(
      h("button", { class: "back", text: t.back, onclick: () => { selected = null; renderMarket(); } }),
      h("div", {}, [h("div", { class: "name", text: i.name }), h("div", { class: "big", text: i.price_text }), change(i.change)]),
      h("div", { class: "chart-box" }, lineChart(i.history)),
      h("div", { class: "row-actions" }, [
        h("button", { class: "primary", text: t.buy, onclick: () => buySheet(i) }),
        h("button", { text: t.sell, onclick: () => sellSheet(i) }),
      ]),
      h("button", { class: "link", text: "🔔 " + t.alert, onclick: () => alertSheet(i) }),
      h("div", { class: "list" }, [
        h("h4", { text: t.plants }),
        ...i.plants.map((p) => h("div", { class: "li" }, [h("div", { text: p.name }), h("div", { class: "num", text: p.text })])),
      ]),
      line
    );
  }

  function openSheet(children) {
    const back = document.getElementById("sheet-back");
    const sheet = document.getElementById("sheet");
    sheet.replaceChildren(...children);
    back.hidden = false;
    back.onclick = (e) => { if (e.target === back) closeSheet(); };
  }
  function closeSheet() {
    document.getElementById("sheet-back").hidden = true;
  }

  function notices(list) {
    return list.map((n) => h("div", { class: `notice ${n.level}` }, [h("span", { class: "ic", text: n.level === "block" ? "!" : "i" }), h("span", { text: n.text })]));
  }

  function buySheet(inst) {
    let keep = true;
    const tonnes = h("input", { type: "number", min: "1", step: "1", value: "5", inputmode: "decimal" });
    const limit = h("input", { type: "number", min: "1", step: "1000", value: String(Math.round((inst.price * 1.03) / 1000) * 1000), inputmode: "numeric" });
    const region = h("select", {}, data.regions.map((r) => h("option", { value: r.id, text: r.name })));
    region.value = "kashkadarya";
    const regionField = h("label", { class: "field", hidden: "" }, [t.region, region]);
    const keepBtn = h("button", { type: "button", class: "on", text: t.keep });
    const delBtn = h("button", { type: "button", text: t.deliver });
    const total = h("div", { class: "total" }, [h("span", { text: t.held }), h("b", { text: "—" })]);
    const box = h("div");
    const ok = h("button", { class: "primary", text: t.confirm });
    const body = () => ({ session: sid, product: inst.id, tonnes: Number(tonnes.value), limit: Number(limit.value), region: keep ? null : region.value, lang: L });
    let timer;
    const preview = () => {
      clearTimeout(timer);
      timer = setTimeout(async () => {
        if (!(Number(tonnes.value) > 0 && Number(limit.value) > 0)) return;
        try {
          const r = await call("/api/order", { ...body(), preview: true });
          total.lastChild.textContent = r.hold_text;
          box.replaceChildren(...notices(r.notices));
          ok.disabled = r.notices.some((n) => n.level === "block");
        } catch {}
      }, 250);
    };
    const setMode = (k) => {
      keep = k;
      keepBtn.classList.toggle("on", k);
      delBtn.classList.toggle("on", !k);
      regionField.hidden = k;
      preview();
    };
    keepBtn.onclick = () => setMode(true);
    delBtn.onclick = () => setMode(false);
    [tonnes, limit, region].forEach((x) => x.addEventListener("input", preview));
    ok.onclick = async () => {
      ok.disabled = true;
      try {
        const r = await call("/api/order", body());
        if (!r.submitted) {
          box.replaceChildren(...notices(r.notices));
          return;
        }
        closeSheet();
        toast(t.placed);
        refresh();
      } catch {
        toast(t.error);
      } finally {
        ok.disabled = false;
      }
    };
    openSheet([
      h("h3", { text: t.buyTitle(inst.name) }),
      h("label", { class: "field" }, [t.tonnes, tonnes]),
      h("label", { class: "field" }, [t.limit, limit]),
      h("div", { class: "field" }, [t.mode, h("div", { class: "seg2" }, [keepBtn, delBtn])]),
      regionField,
      total,
      box,
      h("div", { class: "row-actions" }, [h("button", { text: t.cancel, onclick: closeSheet }), ok]),
    ]);
    preview();
  }

  async function sellSheet(inst) {
    await loadFolio();
    const mine = (folio ? folio.holdings : []).filter((x) => x.product_id === inst.id && x.status === "stored" && x.free > 0);
    if (!mine.length) {
      openSheet([h("h3", { text: t.sellTitle(inst.name) }), h("div", { class: "empty", text: t.noGoods }), h("button", { text: t.cancel, onclick: closeSheet })]);
      return;
    }
    const which = h("select", {}, mine.map((x) => h("option", { value: x.id, text: `${x.free} t · ${x.plant} (${x.region})` })));
    const tonnes = h("input", { type: "number", min: "0.05", step: "0.05", value: String(mine[0].free) });
    const minPrice = h("input", { type: "number", min: "1", step: "1000", value: String(Math.round(((mine[0].mark || inst.price) * 0.97) / 1000) * 1000) });
    which.addEventListener("change", () => {
      const x = mine.find((m) => m.id === which.value);
      tonnes.value = String(x.free);
      minPrice.value = String(Math.round(((x.mark || inst.price) * 0.97) / 1000) * 1000);
    });
    const ok = h("button", { class: "primary", text: t.confirm });
    ok.onclick = async () => {
      ok.disabled = true;
      try {
        await call("/api/sell", { session: sid, receipt: which.value, tonnes: Number(tonnes.value), min_price: Number(minPrice.value), lang: L });
        closeSheet();
        toast(t.sellPlaced);
        refresh();
      } catch {
        toast(t.error);
      } finally {
        ok.disabled = false;
      }
    };
    openSheet([
      h("h3", { text: t.sellTitle(inst.name) }),
      h("label", { class: "field" }, [t.which, which]),
      h("label", { class: "field" }, [t.tonnes, tonnes]),
      h("label", { class: "field" }, [t.minPrice, minPrice]),
      h("div", { class: "notice info" }, [h("span", { class: "ic", text: "i" }), h("span", { text: t.sellNote })]),
      h("div", { class: "row-actions" }, [h("button", { text: t.cancel, onclick: closeSheet }), ok]),
    ]);
  }

  function alertSheet(inst) {
    let dir = "below";
    const price = h("input", { type: "number", min: "1", step: "1000", value: String(Math.round((inst.price * 0.98) / 1000) * 1000) });
    const below = h("button", { type: "button", class: "on", text: t.below });
    const above = h("button", { type: "button", text: t.above });
    below.onclick = () => { dir = "below"; below.classList.add("on"); above.classList.remove("on"); };
    above.onclick = () => { dir = "above"; above.classList.add("on"); below.classList.remove("on"); };
    const ok = h("button", { class: "primary", text: t.confirm });
    ok.onclick = async () => {
      try {
        await call("/api/alerts", { session: sid, product: inst.id, direction: dir, price: Number(price.value) });
        closeSheet();
        toast(t.alertSaved);
        refresh();
      } catch {
        toast(t.error);
      }
    };
    openSheet([
      h("h3", { text: t.alertTitle(inst.name) }),
      h("div", { class: "seg2" }, [below, above]),
      h("label", { class: "field" }, [t.alertPrice, price]),
      h("div", { class: "row-actions" }, [h("button", { text: t.cancel, onclick: closeSheet }), ok]),
    ]);
  }

  function deliverSheet(x) {
    const region = h("select", {}, data.regions.map((r) => h("option", { value: r.id, text: r.name })));
    region.value = "kashkadarya";
    const ok = h("button", { class: "primary", text: t.confirm });
    ok.onclick = async () => {
      try {
        await call(`/api/receipts/${x.id}/deliver`, { session: sid, region: region.value, lang: L });
        closeSheet();
        refresh();
      } catch {
        toast(t.error);
      }
    };
    openSheet([
      h("h3", { text: `${t.deliverTitle}: ${x.tonnes} t ${x.product}` }),
      h("label", { class: "field" }, [t.region, region]),
      h("div", { class: "notice info" }, [h("span", { class: "ic", text: "i" }), h("span", { text: t.deliverNote })]),
      h("div", { class: "row-actions" }, [h("button", { text: t.cancel, onclick: closeSheet }), ok]),
    ]);
  }

  function pnlText(v, text) {
    return `${v > 0 ? "▲ +" : v < 0 ? "▼ −" : ""}${text}`;
  }

  function renderFolio() {
    const box = document.getElementById("tab-folio");
    if (!folio) return;
    const st = (k) => t.status[k] || k;
    const holdings = folio.holdings.length
      ? folio.holdings.map((x) =>
          h("div", { class: "li" }, [
            h("div", {}, [h("div", { text: `${x.product}` }), h("div", { class: "sub", text: `${x.plant} · ${x.region}` }), h("div", { class: "sub", text: t.cost(x.cost_text, x.mark_text) })]),
            h("div", {}, [h("div", { class: "num", text: `${x.tonnes} t` }), h("div", { class: "sub num", text: pnlText(x.pnl, x.pnl_text) })]),
            x.status === "delivering"
              ? h("div", { class: "sub", text: t.delivering(x.delivery_region, x.eta) })
              : h("div", { class: "acts" }, [
                  x.free < x.tonnes ? h("span", { class: "sub", text: t.onSale(Math.round((x.tonnes - x.free) * 100) / 100) }) : null,
                  x.free > 0 ? h("button", { text: t.sell, onclick: () => { const inst = data.instruments.find((i) => i.id === x.product_id); sellSheet(inst); } }) : null,
                  x.free >= x.tonnes ? h("button", { text: t.deliver, onclick: () => deliverSheet(x) }) : null,
                ]),
          ])
        )
      : [h("div", { class: "empty", text: t.nothing })];
    const orders = folio.intents.slice(0, 6).map((o) =>
      h("div", { class: "li" }, [
        h("div", {}, [h("div", { text: `${o.product} · ${o.quantity} t` }), h("div", { class: "sub", text: `${o.region} · ${st(o.status)}` })]),
        h("div", { class: "num", text: o.price_text || o.limit_text }),
        h("ul", {}, [h("li", { text: o.explanation.headline }), ...o.explanation.lines.slice(0, 3).map((l) => h("li", { text: l }))]),
      ])
    );
    const sells = folio.sells.slice(0, 6).map((o) =>
      h("div", { class: "li" }, [
        h("div", {}, [h("div", { text: `${o.product} · ${o.tonnes} t` }), h("div", { class: "sub", text: `${o.plant} · ${st(o.status)}` })]),
        o.status === "waiting" ? h("button", { text: "✕", onclick: async () => { await call(`/api/sells/${o.id}/cancel?lang=${L}`, {}); refresh(); } }) : h("div"),
        h("ul", {}, [h("li", { text: o.explanation.headline }), ...o.explanation.lines.map((l) => h("li", { text: l }))]),
      ])
    );
    const alerts = folio.alerts.slice(0, 6).map((a) =>
      h("div", { class: "li" }, [
        h("div", {}, [h("div", { text: `🔔 ${a.product}` }), h("div", { class: "sub", text: a.direction === "below" ? t.dirBelow(a.price_text) : t.dirAbove(a.price_text) })]),
        h("div", { class: "sub num", text: a.status === "fired" ? t.fired(a.value_text, a.round) : t.waitingAlert }),
      ])
    );
    const parts = [
      h("div", { class: "summary" }, [
        h("div", { class: "tile" }, [h("div", { class: "k", text: t.available }), h("div", { class: "v", text: folio.account.balance_text })]),
        h("div", { class: "tile" }, [h("div", { class: "k", text: t.goods }), h("div", { class: "v", text: folio.value_text })]),
        h("div", { class: "tile" }, [h("div", { class: "k", text: t.pnl }), h("div", { class: "v", text: pnlText(folio.pnl, folio.pnl_text) })]),
      ]),
      h("div", { class: "list" }, [h("h4", { text: t.holdings }), ...holdings]),
      sells.length ? h("div", { class: "list" }, [h("h4", { text: t.sells }), ...sells]) : null,
      orders.length ? h("div", { class: "list" }, [h("h4", { text: t.orders }), ...orders]) : null,
      alerts.length ? h("div", { class: "list" }, [h("h4", { text: t.alerts }), ...alerts]) : null,
    ];
    box.replaceChildren(...parts.filter(Boolean));
  }

  async function loadFolio() {
    try {
      folio = await call(`/api/portfolio?session=${sid}&lang=${L}`);
      document.getElementById("wallet").textContent = folio.account.balance_text;
    } catch {}
  }

  let lastRound = null;
  let marketKey = null;
  let folioKey = null;
  async function refresh() {
    try {
      data = await call(`/api/instruments?lang=${L}`);
      const key = `${data.round}`;
      if (tab === "market" && key !== marketKey) {
        marketKey = key;
        renderMarket();
      } else {
        const line = document.querySelector("#tab-market .round-line span");
        if (line) line.textContent = t.roundLine(data.round, data.seconds_to_next);
      }
    } catch {}
    await loadFolio();
    const fkey = JSON.stringify(folio);
    if (tab === "folio" && fkey !== folioKey) {
      folioKey = fkey;
      renderFolio();
    }
    if (lastRound !== null && data && data.round !== lastRound && folio) {
      const fired = folio.alerts.find((a) => a.status === "fired" && a.round === data.round);
      if (fired) toast(`🔔 ${fired.product}: ${t.fired(fired.value_text, fired.round)}`);
    }
    if (data) lastRound = data.round;
  }

  function show(name) {
    tab = name;
    for (const key of ["market", "chat", "folio"]) {
      document.getElementById(`tab-${key}`).hidden = key !== name;
    }
    document.querySelectorAll("#tabbar button").forEach((b) => b.classList.toggle("on", b.dataset.tab === name));
    const u = new URL(location.href);
    u.searchParams.set("tab", name);
    history.replaceState(null, "", u);
    if (name === "market") renderMarket();
    if (name === "folio") {
      folioKey = JSON.stringify(folio);
      renderFolio();
    }
    window.scrollTo({ top: 0 });
  }

  document.querySelectorAll("#tabbar button").forEach((b) => {
    b.textContent = t.tabs[b.dataset.tab];
    b.addEventListener("click", () => show(b.dataset.tab));
  });
  document.querySelectorAll(".lang button").forEach((b) =>
    b.addEventListener("click", () => {
      const u = new URL(location.href);
      u.searchParams.set("lang", b.dataset.lang);
      u.searchParams.set("tab", tab);
      location.href = u.toString();
    })
  );

  show(tab);
  refresh();
  setInterval(refresh, 2500);
})();
