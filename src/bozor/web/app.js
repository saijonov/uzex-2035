const tg = window.Telegram?.WebApp
const inTg = Boolean(tg?.initData)
const DAY_MS = 120000
const LOAD = 0.08
const MONTHS = ['yan', 'fev', 'mar', 'apr', 'may', 'iyn', 'iyl', 'avg', 'sen', 'okt', 'noy', 'dek']
const CATS = ['Hammasi', 'Qurilish', 'Oziq-ovqat', 'Qishloq xo‘jaligi', 'Kimyo']
const RANGES = [[13, '3 oy'], [26, '6 oy'], [52, '1 yil']]
const HINTS = ['Samarqandga 10 tonna shakar kerak', '20 t shakar, faqat hammasi bo‘lsa', '10 tonna paxta kerak']
const GREETING = 'Salom! Nima kerakligini oddiy so‘z bilan yozing. Sotuvchini o‘zim topaman, bittasida yetmasa — bir nechtasidan yig‘aman.'
const ICON = {
  store: '<path d="M4 10v9a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-9"/><path d="M3 10l1.5-5h15L21 10a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0z"/>',
  box: '<path d="M21 8l-9-5-9 5 9 5 9-5z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/>',
  spark: '<path d="M12 3l1.8 4.9L19 9.7l-5.2 1.8L12 16.5l-1.8-5L5 9.7l5.2-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
  pin: '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
  back: '<path d="M15 5l-7 7 7 7"/>',
  close: '<path d="M6 6l12 12M18 6L6 18"/>',
  send: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  shield: '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
  alert: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9L2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',
  truck: '<path d="M3 6h11v10H3z"/><path d="M14 9h4l3 3v4h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
  check: '<path d="M5 12.5l4.5 4.5L19 7"/>',
  chevron: '<path d="M6 9l6 6 6-6"/>'
}

const $ = sel => document.querySelector(sel)
const icon = (name, cls = 'i') => `<svg class="${cls}" viewBox="0 0 24 24">${ICON[name]}</svg>`
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c])
const num = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
const som = n => `${num(n)} so‘m`
const short = n => n >= 1e6 ? `${(n / 1e6).toFixed(1).replace('.', ',')} mln` : `${num(n / 1000)} ming`
const pct = r => `${r > 0 ? '+' : r < 0 ? '−' : ''}${Math.abs(r * 100).toFixed(1).replace('.', ',')}%`
const day = iso => { const [, m, d] = iso.split('-'); return `${+d}-${MONTHS[m - 1]}` }
const norm = s => s.toLowerCase().replace(/[ʻʼ’‘`']/g, "'").trim()
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v))
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim()
const line = (label, value, cls = '') => `<div class="line ${cls}"><span>${label}</span><span>${value}</span></div>`
const closeBtn = `<button class="x" data-act="close" aria-label="Yopish">${icon('close')}</button>`
const store = {
  get (key, fallback) { try { return JSON.parse(localStorage.getItem('bozor.' + key)) ?? fallback } catch { return fallback } },
  set (key, value) { try { localStorage.setItem('bozor.' + key, JSON.stringify(value)) } catch {} }
}

const S = {
  meta: null,
  region: store.get('region', 'tashkent_city'),
  goods: [],
  tab: 'market',
  view: null,
  sheet: null,
  query: '',
  cat: 'Hammasi',
  range: 52,
  buy: null,
  orders: store.get('orders', null),
  chat: { log: [{ who: 'bot', text: GREETING }], draft: null, asked: null, busy: false }
}

async function api (path, body) {
  const res = await fetch(path, body ? { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) } : undefined)
  if (!res.ok) throw new Error(res.status)
  return res.json()
}

const regionOf = id => S.meta.regions.find(r => r.id === id)
const cityOf = id => regionOf(id).city
const save = () => store.set('orders', S.orders)

function toast (text) {
  const el = $('#toast')
  el.textContent = text
  el.classList.add('show')
  clearTimeout(toast.t)
  toast.t = setTimeout(() => el.classList.remove('show'), 2600)
}

function spark (values) {
  const lo = Math.min(...values), k = Math.max(...values) - lo || 1
  const pts = values.map((v, i) => `${(i / (values.length - 1) * 56).toFixed(1)},${(22 - (v - lo) / k * 20).toFixed(1)}`).join(' ')
  return `<svg class="spark" viewBox="0 0 56 24"><polyline points="${pts}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/></svg>`
}

const change = r => `<span class="chg ${r >= 0 ? 'up' : 'down'}">${r >= 0 ? '▲' : '▼'} ${pct(r)}</span>`

function matches (g) {
  const q = norm(S.query)
  if (S.cat !== 'Hammasi' && g.category !== S.cat) return false
  const tokens = q.split(/\s+/).filter(Boolean)
  return !q || norm(g.name).includes(q) || tokens.some(t => g.words.some(w => norm(w).startsWith(t) || (t.startsWith(norm(w)) && norm(w).length > 2)))
}

function listHtml () {
  const found = S.goods.filter(matches)
  if (!found.length) return `<div class="card empty">«${esc(S.query)}» topilmadi.<br>AI yordamchiga yozib ko‘ring.</div>`
  return `<div class="list">${found.map(g => `
    <button class="row" data-act="good" data-id="${g.id}">
      <span class="grow"><span class="name">${esc(g.name)}</span><span class="sub">${g.sellers} sotuvchi · ${num(g.stock)} t</span></span>
      ${spark(g.spark)}
      <span class="end"><span class="price">${short(g.price)}/t</span>${change(g.change)}</span>
    </button>`).join('')}</div>`
}

function marketView () {
  return `
    <div class="top">
      <div class="title-row"><h1>Bozor</h1><button class="chip-btn" data-act="region">${icon('pin')}${esc(cityOf(S.region))}${icon('chevron')}</button></div>
      <label class="search">${icon('search')}<input id="q" type="search" placeholder="Qidirish: sement, shakar, un…" value="${esc(S.query)}" autocomplete="off" enterkeyhint="search"></label>
      <div class="cats">${CATS.map(c => `<button class="cat ${c === S.cat ? 'on' : ''}" data-act="cat" data-id="${esc(c)}">${esc(c)}</button>`).join('')}</div>
    </div>
    <div id="list">${listHtml()}</div>
    <p class="note">Demo. Narx va sotuvchilar hakaton reestridan (namunaviy ma’lumot, ${day(S.meta.as_of)} 2026 gacha). Narx — birjadagi haftalik o‘rtacha, 1 tonna uchun.</p>`
}

function goodView (d) {
  return `
    <div class="top"><button class="back" data-act="back">${icon('back')}Bozor</button></div>
    <div class="hero">
      <div class="faint">${esc(d.category)}</div>
      <h1>${esc(d.name)}</h1>
      <div style="margin-top:8px"><span class="big">${num(d.price)}</span> <span class="unit">so‘m / t</span></div>
      <div class="faint">Birjadagi o‘rtacha narx, ${day(d.weeks.at(-1)[0])} haftasi · ${change(d.change).replace('class="chg', 'class="inline chg')} 1 oyda</div>
    </div>
    <div class="card" style="margin-top:14px">
      <div class="chart" id="chart"></div>
      <div class="ranges">${RANGES.map(([n, label]) => `<button class="${n === S.range ? 'on' : ''}" data-act="range" data-id="${n}">${label}</button>`).join('')}</div>
    </div>
    <div class="stats">
      <div class="stat"><span class="faint">1 yilda eng past</span><b>${num(d.low)}</b></div>
      <div class="stat"><span class="faint">1 yilda eng yuqori</span><b>${num(d.high)}</b></div>
    </div>
    <h2>Sotuvchilar</h2>
    <div class="faint" style="margin:-6px 0 10px">Narx ${esc(cityOf(S.region))}ga yetkazib berish bilan, 1 t uchun</div>
    <div class="list">${d.offers.map(o => `
      <button class="row" data-act="seller" data-id="${o.id}">
        <span class="grow"><span class="name">${esc(o.name)}</span><span class="sub">${esc(o.city)} · ${Math.round(o.on_time * 100)}% vaqtida · ${num(o.km)} km</span></span>
        <span class="end"><span class="price">${num(o.delivered)}</span><span class="sub">${o.available} t bor · ${o.days} kun</span></span>
      </button>`).join('')}</div>
    <div class="cta"><button class="btn" data-act="buy">Sotib olish</button></div>`
}

function drawChart () {
  const el = $('#chart')
  if (!el) return
  const weeks = S.view.data.weeks.slice(-S.range), W = el.clientWidth, H = el.clientHeight, top = 26, bottom = 22
  const vals = weeks.map(w => w[1]), lo = Math.min(...vals), hi = Math.max(...vals), pad = (hi - lo) * 0.15 || hi * 0.02
  const x = i => i / (weeks.length - 1) * W
  const y = v => top + (1 - (v - lo + pad) / (hi - lo + 2 * pad)) * (H - top - bottom)
  const d = weeks.map((w, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${y(w[1]).toFixed(1)}`).join('')
  const grid = [lo, hi].map(v => `<line class="gl" x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}"/><text x="${W}" y="${y(v) - 5}" text-anchor="end">${short(v)}</text>`).join('')
  const ticks = [0, Math.floor((weeks.length - 1) / 2), weeks.length - 1].map((i, k) => `<text x="${x(i)}" y="${H - 4}" text-anchor="${['start', 'middle', 'end'][k]}">${day(weeks[i][0])}</text>`).join('')
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}">${grid}<path class="ar" d="${d}L${W} ${H - bottom}L0 ${H - bottom}Z"/><path class="ln" d="${d}"/>${ticks}<line class="cx" id="cx" y1="${top - 6}" y2="${H - bottom}" visibility="hidden"/><circle class="cd" id="cd" r="5" visibility="hidden"/></svg><div class="tip" id="tip" hidden></div>`
  const show = on => ['#cx', '#cd'].forEach(s => $(s).setAttribute('visibility', on ? 'visible' : 'hidden'))
  const move = e => {
    const i = clamp(Math.round((e.clientX - el.getBoundingClientRect().left) / W * (weeks.length - 1)), 0, weeks.length - 1)
    $('#cx').setAttribute('x1', x(i))
    $('#cx').setAttribute('x2', x(i))
    $('#cd').setAttribute('cx', x(i))
    $('#cd').setAttribute('cy', y(weeks[i][1]))
    show(true)
    const tip = $('#tip')
    tip.hidden = false
    tip.textContent = `${day(weeks[i][0])} haftasi · ${num(weeks[i][1])} so‘m`
    tip.style.left = `${clamp(x(i), 80, W - 80)}px`
  }
  el.onpointermove = el.onpointerdown = move
  el.onpointerleave = () => { show(false); $('#tip').hidden = true }
}

function planCard (p, bare = false) {
  if (!p.parts.length) return ''
  const to = cityOf(p.region)
  const body = `
    <div class="faint">${p.parts.length > 1 ? `${p.parts.length} ta sotuvchidan yig‘ildi` : 'Bitta sotuvchidan'} · ${esc(p.region_name)}ga</div>
    ${p.parts.map((x, i) => `
      <div class="part">
        <span class="num">${i + 1}</span>
        <div class="grow"><span class="name">${esc(x.seller.name)}</span><span class="sub">${esc(x.seller.city)} → ${esc(to)} · ${num(x.km)} km · ${x.days} kun</span></div>
        <div class="end"><span class="price">${x.tonnes} t</span><span class="sub">${num(x.price + x.freight)}/t</span></div>
      </div>`).join('')}
    <div class="sum">
      ${line(`Tovar, ${p.filled} t`, som(p.cost))}
      ${line('Yetkazish', som(p.delivery))}
      ${line('Birja yig‘imi, 0,13%', som(p.exchange_fee))}
      ${line('Kliring, 0,05%', som(p.clearing_fee))}
      ${line('Jami', som(p.total), 'total')}
    </div>
    <div class="faint" style="margin-top:6px">${p.trucks} ta mashina · ${p.days} kunda yetib keladi</div>`
  return bare ? `<div class="plan">${body}</div>` : `<div class="card plan" style="margin-top:12px">${body}</div>`
}

const escrow = `<div class="info">${icon('shield')}<div>Pul birja hisobida bloklanadi. Yukni qabul qilganingizdan keyingina sotuvchiga o‘tadi.</div></div>`

function sellerSheet (o) {
  return `
    <div class="sheet-head"><h3>${esc(o.name)}</h3>${closeBtn}</div>
    <div class="muted">${esc(o.city)}, ${esc(o.region_name)}</div>
    <div class="trust">
      <div><b>${num(o.deals)}</b><span>bitim, 2026</span></div>
      <div><b>${Math.round(o.on_time * 100)}%</b><span>vaqtida yetkazgan</span></div>
      <div><b>${o.since}</b><span>yildan birjada</span></div>
    </div>
    <div class="card" style="margin-top:12px">
      ${o.grade ? line('Navi', esc(o.grade)) : ''}
      ${line('Qadoq', esc(o.packaging))}
      ${line('Sotuvda', `${o.available} t`)}
      <div class="sum">
        ${line('Ombordagi narx', som(o.price))}
        ${line(`Yetkazish, ${num(o.km)} km`, som(o.freight))}
        ${line(`${esc(cityOf(S.region))}gacha, 1 t`, som(o.delivered), 'total')}
      </div>
    </div>
    <p class="faint">Ishonch ko‘rsatkichi bitimlar tarixidan olinadi: va’da qilingan muddatda yetkazilgan bitimlar ulushi.</p>
    <button class="btn" data-act="buy" data-id="${o.id}">Shu sotuvchidan olish</button>`
}

function buyBody () {
  const b = S.buy, p = b.plan, d = S.view.data
  const seller = b.seller && d.offers.find(o => o.id === b.seller)
  const warn = p.short ? `<div class="info warn">${icon('alert')}<div>Hozir faqat ${p.filled} t bor.${b.whole ? ' Siz hammasini birdan so‘radingiz, shuning uchun xarid bo‘lmaydi.' : ` ${p.filled} t olinadi.`}</div></div>` : ''
  return `
    <div class="card">
      <div class="qty">
        <div><b>Miqdor, tonna</b><div class="faint">${seller ? `${esc(seller.name)}da ${seller.available} t bor` : `Bozorda ${num(d.stock)} t bor`}</div></div>
        <div class="stepper"><button data-act="qty" data-id="-1" aria-label="Kamaytirish">−</button><input id="tonnes" inputmode="numeric" value="${b.tonnes}"><button data-act="qty" data-id="1" aria-label="Ko‘paytirish">+</button></div>
      </div>
      ${seller ? '' : `<div class="toggle"><div><b>Hammasi yoki hech narsa</b><div class="faint">Yetarli bo‘lmasa, xarid qilinmaydi</div></div><button class="switch ${b.whole ? 'on' : ''}" data-act="whole" aria-label="Hammasi yoki hech narsa"></button></div>`}
    </div>
    ${planCard(p)}${warn}${escrow}
    <button class="btn" style="margin-top:14px" data-act="pay" ${p.ready ? '' : 'disabled'}>${p.ready ? `To‘lash · ${som(p.total)}` : 'Yetarli tovar yo‘q'}</button>`
}

function regionSheet () {
  return `
    <div class="sheet-head"><h3>Yetkazish manzili</h3>${closeBtn}</div>
    <div class="list">${S.meta.regions.map(r => `
      <button class="row" data-act="set-region" data-id="${r.id}">
        <span class="grow"><span class="name">${esc(r.name)}</span><span class="sub">${esc(r.city)}</span></span>
        ${r.id === S.region ? `<span style="color:var(--accent)">${icon('check')}</span>` : ''}
      </button>`).join('')}</div>`
}

function msgHtml (m, i) {
  if (m.who === 'me') return `<div class="msg me">${esc(m.text)}</div>`
  let html = `<div class="msg bot">${esc(m.text)}</div>`
  if (m.plan?.parts.length) {
    const p = m.plan
    const actions = m.done
      ? `<div class="info">${icon('check')}<div>${esc(m.done)}</div></div>`
      : p.ready
        ? `${escrow}<button class="btn" style="margin-top:12px" data-act="chat-pay" data-id="${i}">Tasdiqlash va to‘lash</button>`
        : `<div class="btns"><button class="btn" data-act="chat-partial" data-id="${i}">${p.filled} t olish</button><button class="btn ghost" data-act="chat-wait" data-id="${i}">Kutaman</button></div>`
    html += `<div class="msg card-msg">${planCard(p, true)}${actions}</div>`
  }
  return html
}

function drawChat () {
  const log = $('#log')
  if (!log) return
  log.innerHTML = S.chat.log.map(msgHtml).join('') + (S.chat.busy ? '<div class="typing">Yozmoqda…</div>' : '')
  log.scrollTop = log.scrollHeight
  $('#hints').hidden = S.chat.log.length > 1
}

function chatSheet () {
  return `
    <div class="sheet-head"><h3>AI yordamchi</h3>${closeBtn}</div>
    <div class="chat-log" id="log"></div>
    <div class="hints" id="hints">${HINTS.map(h => `<button data-act="hint" data-id="${esc(h)}">${esc(h)}</button>`).join('')}</div>
    <form class="composer" id="composer"><input id="say" placeholder="Masalan: Qarshiga 60 qop sement" autocomplete="off" enterkeyhint="send"><button class="send" aria-label="Yuborish">${icon('send')}</button></form>`
}

function drawSheet () {
  document.documentElement.style.overflow = S.sheet ? 'hidden' : ''
  if (!S.sheet) { $('#layer').innerHTML = ''; return backButton() }
  const { type, data } = S.sheet
  const inner = { seller: () => sellerSheet(data), buy: () => `<div class="sheet-head"><h3>${esc(S.view.data.name)}</h3>${closeBtn}</div><div id="buy">${buyBody()}</div>`, region: regionSheet, chat: chatSheet }[type]()
  $('#layer').innerHTML = `<div class="scrim" data-act="close"></div><div class="sheet ${type === 'chat' ? 'full' : ''}"><div class="grab"></div>${inner}</div>`
  if (type === 'chat') drawChat()
  backButton()
}

function progress (o, part) {
  return clamp((Date.now() - o.created) / (part.days * DAY_MS), 0, 1)
}

function orderState (o) {
  const ps = o.plan.parts.map(x => progress(o, x))
  const avg = ps.reduce((a, b) => a + b, 0) / ps.length
  if (o.confirmed) return { label: 'Qabul qilindi', cls: 'done', progress: 1, arrived: true }
  if (ps.every(p => p >= 1)) return { label: 'Yetib keldi', cls: 'wait', progress: 1, arrived: true }
  return { label: ps.every(p => p < LOAD) ? 'Yuklanmoqda' : 'Yo‘lda', cls: '', progress: avg, arrived: false }
}

function when (ts) {
  const d = new Date(ts)
  return `${d.getDate()}-${MONTHS[d.getMonth()]}, ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function ordersView () {
  return `
    <div class="top"><div class="title-row"><h1>Xaridlarim</h1></div></div>
    ${S.orders.length
      ? `<div class="list">${S.orders.map(o => {
          const st = orderState(o)
          return `
            <button class="order" data-act="order" data-id="${o.id}">
              <span class="title-row"><span class="name">${esc(o.plan.good_name)} · ${o.plan.filled} t</span><span class="status ${st.cls}">${st.label}</span></span>
              <span class="sub">${o.plan.parts.length} ta sotuvchi · ${o.plan.trucks} ta mashina · ${esc(o.plan.region_name)}</span>
              <span class="title-row" style="margin-top:4px"><span class="faint">${when(o.created)}</span><b>${som(o.plan.total)}</b></span>
              <span class="bar" style="display:block"><i style="width:${Math.round(st.progress * 100)}%"></i></span>
            </button>`
        }).join('')}</div>`
      : '<div class="card empty">Hali xarid yo‘q.<br>Bozordan tanlang yoki AI yordamchiga yozing.</div>'}
    <p class="note"><button class="link" data-act="reset">Demo xaridlarni qaytadan boshlash</button></p>`
}

function partLabel (p) {
  return p >= 1 ? 'Yetib keldi' : p < LOAD ? 'Yuklanmoqda' : 'Yo‘lda'
}

function orderLive (o) {
  const st = orderState(o), to = cityOf(o.plan.region)
  const ps = o.plan.parts.map(x => progress(o, x))
  const steps = [
    ['To‘lov birjada bloklandi', true],
    ['Yuk mashinaga ortildi', ps.every(p => p >= LOAD)],
    ['Yuk yetib keldi', st.arrived],
    ['Siz qabul qildingiz', o.confirmed],
    ['Pul sotuvchiga o‘tdi', o.confirmed]
  ]
  const now = steps.findIndex(s => !s[1])
  return `
    <h2>Yuklar</h2>
    <div class="list">${o.plan.parts.map((x, i) => {
      const p = ps[i], left = Math.ceil((1 - p) * x.days * 24)
      return `
        <div class="row">
          <span class="num">${i + 1}</span>
          <span class="grow"><span class="name">${esc(x.seller.name)}</span><span class="sub">${esc(x.seller.city)} → ${esc(to)} · ${x.tonnes} t · ${num(x.km)} km</span><span class="bar" style="display:block"><i style="width:${Math.round(p * 100)}%"></i></span></span>
          <span class="end"><span class="status ${p >= 1 ? 'done' : ''}">${partLabel(p)}</span><span class="sub" style="margin-top:4px">${p < 1 ? `~${left} soat qoldi` : ''}</span></span>
        </div>`
    }).join('')}</div>
    <h2>Holat</h2>
    <div class="card"><ul class="steps">${steps.map(([label, done], i) => `<li class="${done ? 'done' : i === now ? 'now' : ''}"><i>${done ? icon('check') : ''}</i>${label}</li>`).join('')}</ul></div>
    <h2>To‘lov</h2>
    <div class="card">
      ${line('Jami', som(o.plan.total), 'total')}
      ${line('Pul qayerda', o.confirmed ? 'Sotuvchi va tashuvchida' : 'Birja hisobida, bloklangan')}
      <div class="info">${icon('shield')}<div>${o.confirmed ? 'Yuk qabul qilindi. Pul sotuvchilarga va tashuvchiga o‘tkazildi.' : 'Yukni qabul qilmaguningizcha pul sotuvchiga o‘tmaydi. Muammo bo‘lsa, nizo birja orqali hal qilinadi.'}</div></div>
    </div>
    ${o.confirmed ? '' : `<div style="margin-top:12px"><button class="btn" data-act="confirm" data-id="${o.id}" ${st.arrived ? '' : 'disabled'}>${st.arrived ? 'Yukni qabul qildim' : 'Yuk yetib kelgach tasdiqlaysiz'}</button></div>`}`
}

function orderView (o) {
  return `
    <div class="top"><button class="back" data-act="back">${icon('back')}Xaridlarim</button></div>
    <h1>${esc(o.plan.good_name)} · ${o.plan.filled} t</h1>
    <div class="muted">${esc(o.plan.region_name)}ga · ${o.plan.parts.length} ta sotuvchi · ${o.plan.trucks} ta mashina</div>
    <div class="map" id="map"></div>
    <div id="live">${orderLive(o)}</div>
    <p class="note">Demo: 1 kunlik yo‘l 2 daqiqada ko‘rsatiladi. Haqiqiy ilovada mashina joyi tashuvchining GPS’idan olinadi. Yo‘llar OpenStreetMap ma’lumotidan.</p>`
}

const MAP = { map: null, trucks: [], live: '', tabs: '' }

function lengths (line) {
  const out = [0]
  for (let i = 1; i < line.length; i++) {
    const [a, b] = [line[i - 1], line[i]], k = Math.cos(a[0] * Math.PI / 180)
    out.push(out[i - 1] + Math.hypot(b[0] - a[0], (b[1] - a[1]) * k))
  }
  return out
}

function along (t) {
  const { line, cum } = t, goal = cum.at(-1) * t.travel
  const i = clamp(cum.findIndex(c => c >= goal), 1, line.length - 1)
  const f = (goal - cum[i - 1]) / ((cum[i] - cum[i - 1]) || 1)
  const point = [line[i - 1][0] + (line[i][0] - line[i - 1][0]) * f, line[i - 1][1] + (line[i][1] - line[i - 1][1]) * f]
  return { point, done: [...line.slice(0, i), point] }
}

function moveTrucks (o) {
  for (const t of MAP.trucks) {
    t.travel = clamp((progress(o, t.part) - LOAD) / (1 - LOAD), 0, 1)
    const { point, done } = along(t)
    t.marker.setLatLng(point)
    t.done.setLatLngs(done)
  }
}

function mountMap (o) {
  MAP.map?.remove()
  MAP.map = null
  if (!window.L || !$('#map')) return
  const accent = css('--accent')
  const map = L.map('map', { zoomControl: false })
  map.attributionControl.setPrefix(false)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 12, attribution: '© OpenStreetMap' }).addTo(map)
  const pin = cls => L.divIcon({ className: '', html: `<div class="pin ${cls}"></div>`, iconSize: cls ? [18, 18] : [14, 14] })
  MAP.trucks = o.plan.parts.map(part => {
    L.polyline(part.line, { color: accent, weight: 4, opacity: 0.25 }).addTo(map)
    const done = L.polyline([], { color: accent, weight: 4 }).addTo(map)
    L.marker(part.line[0], { icon: pin('') }).addTo(map).bindTooltip(esc(part.seller.city), { direction: 'top', offset: [0, -6] })
    const marker = L.marker(part.line[0], { icon: L.divIcon({ className: '', html: `<div class="truck">${icon('truck', '')}</div>`, iconSize: [34, 34] }), zIndexOffset: 1000 }).addTo(map)
    return { part, line: part.line, cum: lengths(part.line), done, marker, travel: 0 }
  })
  L.marker(o.plan.parts[0].line.at(-1), { icon: pin('home') }).addTo(map).bindTooltip(esc(cityOf(o.plan.region)), { permanent: true, direction: 'right', offset: [10, 0] })
  map.fitBounds(o.plan.parts.flatMap(p => p.line), { padding: [36, 36], maxZoom: 9 })
  MAP.map = map
  moveTrucks(o)
}

function tabs () {
  const active = S.orders.filter(o => !o.confirmed).length
  const [market, orders] = document.querySelectorAll('.tabs button')
  if (MAP.tabs !== String(active)) {
    market.innerHTML = `${icon('store')}<span>Bozor</span>`
    orders.innerHTML = `${icon('box')}<span>Xaridlarim</span>${active ? `<b class="dot">${active}</b>` : ''}`
    MAP.tabs = String(active)
  }
  market.className = S.tab === 'market' ? 'on' : ''
  orders.className = S.tab === 'orders' ? 'on' : ''
}

function backButton () {
  if (!inTg) return
  S.sheet || S.view ? tg.BackButton.show() : tg.BackButton.hide()
}

function render () {
  const v = S.view
  document.body.classList.toggle('detail', v?.type === 'good')
  if (v?.type !== 'order') { MAP.map?.remove(); MAP.map = null }
  $('#screen').innerHTML = v?.type === 'good' ? goodView(v.data) : v?.type === 'order' ? orderView(S.orders.find(o => o.id === v.id)) : S.tab === 'market' ? marketView() : ordersView()
  if (v?.type === 'good') drawChart()
  if (v?.type === 'order') { MAP.live = ''; mountMap(S.orders.find(o => o.id === v.id)) }
  tabs()
  backButton()
}

function tick () {
  tabs()
  const v = S.view
  if (v?.type === 'order') {
    const o = S.orders.find(x => x.id === v.id), html = orderLive(o)
    if ($('#live') && MAP.live !== html) { $('#live').innerHTML = html; MAP.live = html }
    if (MAP.map) moveTrucks(o)
  } else if (!v && S.tab === 'orders') {
    for (const el of document.querySelectorAll('.order')) {
      const st = orderState(S.orders.find(o => o.id === el.dataset.id))
      el.querySelector('.bar i').style.width = `${Math.round(st.progress * 100)}%`
      const badge = el.querySelector('.status')
      if (badge.textContent !== st.label) { badge.textContent = st.label; badge.className = `status ${st.cls}` }
    }
  }
}

async function quote () {
  const b = S.buy
  b.plan = await api('/api/plan', { good: b.good, tonnes: b.tonnes, region: S.region, whole: b.whole, seller: b.seller })
  if ($('#buy')) $('#buy').innerHTML = buyBody()
}

function place (plan) {
  const id = 'o' + Date.now().toString(36)
  S.orders.unshift({ id, created: Date.now(), plan, confirmed: false })
  save()
  S.sheet = null
  drawSheet()
  if (inTg) tg.HapticFeedback?.notificationOccurred('success')
  S.tab = 'orders'
  S.view = { type: 'order', id }
  render()
  window.scrollTo(0, 0)
  toast('To‘lov bloklandi. Yuk yo‘lga tayyorlanmoqda.')
}

async function seed () {
  const demo = await api(`/api/demo?region=${S.region}`)
  const now = Date.now()
  S.orders = demo.map(({ plan, progress }, i) => {
    const longest = Math.max(...plan.parts.map(x => x.days)) * DAY_MS
    return { id: `demo${i}${now.toString(36)}`, created: now - longest * progress - (progress >= 1 ? 60000 : 0), plan, confirmed: false }
  })
  save()
}

async function send (text) {
  text = text.trim()
  if (!text || S.chat.busy) return
  S.chat.log.push({ who: 'me', text })
  S.chat.busy = true
  drawChat()
  try {
    const r = await api('/api/chat', { message: text, region: S.region, draft: S.chat.draft, asked: S.chat.asked })
    S.chat.draft = r.draft
    S.chat.asked = r.asked
    S.chat.log.push({ who: 'bot', text: r.reply, plan: r.plan })
  } catch {
    S.chat.log.push({ who: 'bot', text: 'Aloqa uzildi. Qayta yozib ko‘ring.' })
  }
  S.chat.busy = false
  drawChat()
}

async function openGood (id) {
  S.view = { type: 'good', id, data: await api(`/api/goods/${id}?region=${S.region}`) }
  render()
  window.scrollTo(0, 0)
}

function back () {
  if (S.sheet) { S.sheet = null; return drawSheet() }
  if (S.view) { S.view = null; render() }
}

const ACTIONS = {
  tab: id => { S.tab = id; S.view = null; render(); window.scrollTo(0, 0) },
  good: id => openGood(id),
  back,
  close: back,
  cat: id => { S.cat = id; render() },
  range: id => { S.range = +id; render() },
  region: () => { S.sheet = { type: 'region' }; drawSheet() },
  'set-region': async id => {
    S.region = id
    store.set('region', id)
    if (S.chat.draft) S.chat.draft.region = id
    S.goods = await api(`/api/goods?region=${id}`)
    S.sheet = null
    drawSheet()
    if (S.view?.type === 'good') S.view.data = await api(`/api/goods/${S.view.id}?region=${id}`)
    render()
  },
  seller: id => { S.sheet = { type: 'seller', data: S.view.data.offers.find(o => o.id === id) }; drawSheet() },
  buy: async id => {
    const good = S.view.data.id
    const seller = id && S.view.data.offers.find(o => o.id === id)
    S.buy = { good, seller: id || null, tonnes: seller ? Math.min(seller.available, 10) : S.buy?.good === good && !S.buy.seller ? S.buy.tonnes : 10, whole: false, plan: null }
    await quote()
    S.sheet = { type: 'buy' }
    drawSheet()
  },
  qty: id => { S.buy.tonnes = clamp(S.buy.tonnes + +id, 1, 1000); quote() },
  whole: () => { S.buy.whole = !S.buy.whole; quote() },
  pay: () => S.buy.plan.ready && place(S.buy.plan),
  chat: () => { S.sheet = { type: 'chat' }; drawSheet() },
  hint: text => send(text),
  'chat-pay': i => {
    const m = S.chat.log[i]
    m.done = 'To‘landi. Xaridlarimda kuzatishingiz mumkin.'
    S.chat.draft = null
    S.chat.asked = null
    place(m.plan)
  },
  'chat-partial': async i => {
    const m = S.chat.log[i], p = m.plan
    m.done = `${p.filled} t olindi.`
    S.chat.draft = null
    place(await api('/api/plan', { good: p.good, tonnes: p.filled, region: p.region, whole: false }))
  },
  'chat-wait': i => {
    const m = S.chat.log[i]
    m.done = 'Kutyapmiz.'
    S.chat.log.push({ who: 'bot', text: `Yaxshi. ${m.plan.asked} t to‘liq yig‘ilishi bilan shu yerda xabar beraman. Pulingiz bloklanmaydi.` })
    S.chat.draft = null
    drawChat()
  },
  order: id => { S.view = { type: 'order', id }; render(); window.scrollTo(0, 0) },
  confirm: id => {
    const o = S.orders.find(x => x.id === id)
    o.confirmed = true
    save()
    if (inTg) tg.HapticFeedback?.notificationOccurred('success')
    render()
    toast('Rahmat! Pul sotuvchilarga o‘tkazildi.')
  },
  reset: async () => { await seed(); render() }
}

document.addEventListener('click', e => {
  const el = e.target.closest('[data-act]')
  if (!el || el.disabled) return
  ACTIONS[el.dataset.act]?.(el.dataset.id, el)
})

document.addEventListener('input', e => {
  if (e.target.id === 'q') { S.query = e.target.value; $('#list').innerHTML = listHtml() }
})

document.addEventListener('change', e => {
  if (e.target.id === 'tonnes') { S.buy.tonnes = clamp(parseInt(e.target.value, 10) || 1, 1, 1000); quote() }
})

document.addEventListener('submit', e => {
  if (e.target.id !== 'composer') return
  e.preventDefault()
  const input = $('#say')
  send(input.value)
  input.value = ''
})

document.addEventListener('keydown', e => { if (e.key === 'Escape') back() })
addEventListener('resize', () => S.view?.type === 'good' && drawChart())

function theme () {
  if (!inTg) return
  document.documentElement.dataset.theme = tg.colorScheme
  tg.setHeaderColor?.(css('--bg'))
  tg.setBackgroundColor?.(css('--bg'))
  tg.setBottomBarColor?.(css('--card'))
}

async function start () {
  if (inTg) {
    tg.ready()
    tg.expand()
    tg.disableVerticalSwipes?.()
    tg.BackButton.onClick(back)
    tg.onEvent('themeChanged', () => { theme(); render() })
    theme()
  }
  $('#ai').innerHTML = `${icon('spark')}<span>AI</span>`
  S.meta = await api('/api/meta')
  if (!S.meta.regions.some(r => r.id === S.region)) S.region = 'tashkent_city'
  S.goods = await api(`/api/goods?region=${S.region}`)
  if (!Array.isArray(S.orders)) await seed()
  render()
  setInterval(tick, 1000)
}

start()
