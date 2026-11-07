const tg = window.Telegram?.WebApp
const page = document.getElementById('screen')
const HOLE = /\{\{\s*([^}]+?)\s*\}\}/g
const fmt = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')

const LOGIC = {
  Y2Product (st, set) {
    const qty = st.qty ?? 10
    const range = st.range ?? 26
    const short = n => n >= 1000000 ? (n / 1000000).toFixed(2).replace('.', ',') + ' млн' : Math.round(n / 1000) + ' тыс'
    const keys = [[0, 955000], [6, 990000], [12, 1033400], [18, 1005000], [24, 978000], [30, 921300], [36, 948000], [42, 1001000], [46, 998000], [49, 985000], [52, 965900]]
    const all = []
    for (let i = 0; i <= 52; i++) {
      let k = 0
      while (k < keys.length - 2 && keys[k + 1][0] < i) k++
      const a = keys[k]
      const b = keys[k + 1]
      const t = (i - a[0]) / (b[0] - a[0])
      const wob = (i === 52 || i === 12 || i === 30) ? 0 : Math.sin(i * 2.1) * 6500 + Math.cos(i * 0.7) * 3500
      all.push(Math.round(a[1] + (b[1] - a[1]) * t + wob))
    }
    const months = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
    const end = new Date(2026, 9, 26)
    const dateOf = i => {
      const d = new Date(end.getTime() - (52 - i) * 7 * 86400000)
      return d.getDate() + ' ' + months[d.getMonth()]
    }
    const start = 52 - range
    const win = all.slice(start)
    const n = win.length
    const idx = Math.min(st.idx ?? n - 1, n - 1)
    const lo = Math.min(...win)
    const hi = Math.max(...win)
    const pad = (hi - lo) * 0.12 + 1
    const W = 316
    const H = 140
    const top = 14
    const bot = 126
    const X = i => (i / (n - 1)) * W
    const Y = v => top + (1 - (v - (lo - pad)) / (hi - lo + 2 * pad)) * (bot - top)
    const line = win.map((v, i) => (i ? ' L' : 'M') + X(i).toFixed(1) + ' ' + Y(v).toFixed(1)).join('')
    const cx = X(idx)
    const cy = Y(win[idx])
    const pct = (win[idx] - win[0]) / win[0] * 100
    const opts = [[13, '3 мес'], [26, '6 мес'], [52, '1 год']]
    const goods = qty * 907700
    return {
      tipDate: dateOf(start + idx),
      qty,
      line,
      area: line + ' L' + W + ' ' + H + ' L0 ' + H + ' Z',
      cx: cx.toFixed(1),
      cy: cy.toFixed(1),
      tipLeft: Math.max(0, Math.min(W - 104, cx - 52)).toFixed(0),
      tipTop: (cy < 62 ? cy + 14 : cy - 58).toFixed(0),
      idx,
      maxIdx: n - 1,
      selPrice: fmt(win[idx]),
      selShort: fmt(win[idx]) + ' сум',
      selDate: dateOf(start + idx) + (start + idx === 52 ? ', последняя неделя' : ''),
      maxLabel: short(hi),
      minLabel: short(lo),
      change: (pct >= 0 ? '+' : '−') + Math.abs(pct).toFixed(1).replace('.', ',') + '% за период',
      ranges: opts.map(([w, label]) => ({
        label,
        bg: w === range ? '#111111' : '#F4F4F1',
        fg: w === range ? '#FFFFFF' : '#111111',
        pick: () => set({ range: w, idx: undefined })
      })),
      total: fmt(goods + qty * 18000 + Math.floor(goods * 0.0013) + Math.floor(goods * 0.0005)),
      onSlide: e => set({ idx: Number(e.target.value) }),
      minus: () => set({ qty: Math.max(1, qty - 1) }),
      plus: () => set({ qty: Math.min(400, qty + 1) })
    }
  },

  N1Checkout (st, set) {
    const qty = 10
    const share = st.share ?? true
    const pay = st.pay ?? 'click'
    const goods = qty * 907700
    const delivery = qty * (share ? 18000 : 36000)
    const fee1 = Math.floor(goods * 0.0013)
    const fee2 = Math.floor(goods * 0.0005)
    const opts = [['click', 'Click'], ['payme', 'Payme'], ['bank', 'Счёт фирмы']]
    return {
      qty,
      pays: opts.map(([id, label]) => ({
        label,
        aria: id === pay ? 'true' : 'false',
        bg: id === pay ? '#FFDD2D' : '#F4F4F1',
        border: id === pay ? '2px solid #111111' : '2px solid transparent',
        pick: () => set({ pay: id })
      })),
      goods: fmt(goods),
      delivery: fmt(delivery),
      fee1: fmt(fee1),
      fee2: fmt(fee2),
      total: fmt(goods + delivery + fee1 + fee2),
      shareAria: share ? 'true' : 'false',
      shareBg: share ? '#FFF6CC' : '#F4F4F1',
      switchBg: share ? '#111111' : '#DCDCD6',
      knobBg: share ? '#FFDD2D' : '#FFFFFF',
      knob: share ? 24 : 4,
      toggleShare: () => set({ share: !share })
    }
  },

  N2Success () {
    return {
      steps: [
        { n: '1', title: 'Продавец подтверждает', sub: 'Сейчас, обычно до 2 часов', bg: '#FFDD2D', fg: '#111111' },
        { n: '2', title: 'Машина загружается', sub: 'Сегодня вечером в Самарканде', bg: '#F4F4F1', fg: '#111111' },
        { n: '3', title: 'Груз в пути', sub: 'Около 1 дня, следите на карте', bg: '#F4F4F1', fg: '#111111' },
        { n: '4', title: 'Вы принимаете груз', sub: 'И деньги уходят продавцу', bg: '#F4F4F1', fg: '#111111' }
      ]
    }
  },

  N5AutoBuy (st, set) {
    const target = st.target ?? 930000
    const qty = st.qty ?? 10
    const wait = st.wait ?? 7
    const now = 965900
    const opts = [[3, '3 дня'], [7, 'Неделя'], [30, 'Месяц']]
    return {
      target: fmt(target),
      targetNum: target,
      qty,
      waits: opts.map(([d, label]) => ({
        label,
        aria: d === wait ? 'true' : 'false',
        bg: d === wait ? '#111111' : '#F4F4F1',
        fg: d === wait ? '#FFFFFF' : '#111111',
        pick: () => set({ wait: d })
      })),
      pct: ((now - target) / now * 100).toFixed(1).replace('.', ',') + '%',
      sum: fmt(target * qty),
      onTarget: e => set({ target: Number(e.target.value) }),
      minus: () => set({ qty: Math.max(1, qty - 1) }),
      plus: () => set({ qty: Math.min(400, qty + 1) })
    }
  },

  N4Arrived (st, set) {
    const marks = st.marks ?? [true, true, false]
    const done = st.done ?? false
    const rating = st.rating ?? 0
    const labels = ['40 тонн, 800 мешков', 'На мешках марка М400', 'Мешки целые и сухие']
    const ready = marks.every(Boolean)
    return {
      checks: labels.map((label, i) => ({
        label,
        aria: marks[i] ? 'true' : 'false',
        boxBg: marks[i] ? '#FFDD2D' : '#FFFFFF',
        tick: marks[i] ? '#111111' : 'transparent',
        toggle: () => set({ marks: marks.map((m, j) => j === i ? !m : m) })
      })),
      stars: [1, 2, 3, 4, 5].map(n => ({
        aria: 'Оценка ' + n,
        bg: n <= rating ? '#FFDD2D' : '#F4F4F1',
        fill: n <= rating ? '#111111' : 'none',
        pick: () => set({ rating: n })
      })),
      done,
      notDone: !done,
      notReady: !ready,
      closeBg: ready ? '#111111' : '#EFEFEA',
      closeFg: ready ? '#FFFFFF' : '#8A8980',
      close: () => ready && set({ done: true })
    }
  }
}

let current
let state
let handlers

function lookup (path, scope) {
  const [head, ...rest] = path.split('.')
  const found = scope.find(s => head in s)
  return found && rest.reduce((v, key) => v?.[key], found[head])
}

const fill = (text, scope) => text.replace(HOLE, (_, path) => lookup(path, scope) ?? '')
const whole = text => text?.match(/^\{\{\s*([^}]+?)\s*\}\}$/)?.[1]

function build (node, scope, out) {
  for (const child of node.childNodes) {
    if (child.nodeType === Node.TEXT_NODE) {
      out.append(fill(child.nodeValue, scope))
      continue
    }
    if (child.nodeType !== Node.ELEMENT_NODE) continue
    if (child.localName === 'sc-for') {
      const as = child.getAttribute('as')
      for (const item of lookup(whole(child.getAttribute('list')), scope) ?? []) {
        build(child, [{ [as]: item }, ...scope], out)
      }
      continue
    }
    if (child.localName === 'sc-if') {
      if (lookup(whole(child.getAttribute('value')), scope)) build(child, scope, out)
      continue
    }
    const el = document.createElementNS(child.namespaceURI, child.localName)
    for (const { name, value } of child.attributes) {
      const path = whole(value)
      if (/^on[a-z]+$/.test(name)) {
        const fn = path && lookup(path, scope)
        const event = name === 'onchange' ? 'input' : name.slice(2)
        if (typeof fn === 'function') el.setAttribute('data-on-' + event, handlers.push(fn) - 1)
      } else if (path) {
        const val = lookup(path, scope)
        if (val !== false && val != null) el.setAttribute(name, val === true ? '' : val)
      } else {
        el.setAttribute(name, fill(value, scope))
      }
    }
    build(child, scope, el)
    out.append(el)
  }
}

function morph (from, to) {
  const old = [...from.childNodes]
  const next = [...to.childNodes]
  next.forEach((node, i) => {
    const prev = old[i]
    if (!prev) return from.append(node)
    if (prev.nodeType !== node.nodeType || prev.nodeName !== node.nodeName) return prev.replaceWith(node)
    if (prev.nodeType === Node.TEXT_NODE) {
      if (prev.nodeValue !== node.nodeValue) prev.nodeValue = node.nodeValue
      return
    }
    if (prev.nodeType !== Node.ELEMENT_NODE) return
    for (const { name } of [...prev.attributes]) if (!node.hasAttribute(name)) prev.removeAttribute(name)
    for (const { name, value } of node.attributes) if (prev.getAttribute(name) !== value) prev.setAttribute(name, value)
    if (prev.localName === 'input' && node.hasAttribute('value') && prev.value !== node.getAttribute('value')) {
      prev.value = node.getAttribute('value')
    }
    morph(prev, node)
  })
  for (const node of old.slice(next.length)) node.remove()
}

function fit () {
  const root = page.firstElementChild
  let flow = 0
  let foot = 0
  for (const el of root.children) {
    const { position, bottom } = el.style
    if (position !== 'absolute') flow = Math.max(flow, el.offsetTop + el.offsetHeight)
    else if (bottom) foot = Math.max(foot, el.offsetHeight + parseFloat(bottom))
  }
  const need = flow ? Math.min(844, flow + foot + 16) : 844
  const scale = Math.min(innerWidth / 390, innerHeight / need)
  page.style.width = innerWidth / scale + 'px'
  page.style.height = innerHeight / scale + 'px'
  page.style.transform = `scale(${scale})`
}

function render () {
  handlers = []
  const box = document.createElement('div')
  build(document.getElementById(current).content, [LOGIC[current]?.(state, set) ?? {}], box)
  morph(page, box)
  fit()
}

function set (patch) {
  state = { ...state, ...patch }
  render()
}

const back = () => page.querySelector('a[aria-label="Назад"]')

function go (name) {
  if (!(document.getElementById(name) instanceof HTMLTemplateElement)) return
  current = name
  state = {}
  page.replaceChildren()
  render()
  tg?.BackButton[back() ? 'show' : 'hide']()
}

page.addEventListener('click', event => {
  const target = event.target.closest('[data-on-click]')
  if (target && !target.disabled) handlers[target.dataset.onClick](event)
  const link = event.target.closest('a[href^="#"]')
  if (link) {
    event.preventDefault()
    go(link.getAttribute('href').slice(1))
  }
  if (target || link) tg?.HapticFeedback.selectionChanged()
})

page.addEventListener('input', event => {
  const target = event.target.closest('[data-on-input]')
  if (target) handlers[target.dataset.onInput](event)
})

addEventListener('resize', fit)

if (tg) {
  tg.ready()
  tg.expand()
  tg.disableVerticalSwipes?.()
  tg.setHeaderColor('#FFFFFF')
  tg.setBackgroundColor('#FFFFFF')
  tg.BackButton.onClick(() => back()?.click())
  tg.onEvent('viewportChanged', fit)
}

go(location.hash.slice(1))
current || go('Y1Home')
