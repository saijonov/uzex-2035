from niyat.catalog import RESTRICTED
from niyat.draft import Draft
from niyat.exchange import FEE_RATE, Exchange
from niyat.explain import money

MIN_TONNES = 1.0
LARGE_TONNES = 500.0
LOW_RATIO = 0.9
HIGH_RATIO = 1.35

TEXT = {
    "uz": {
        "restricted": "{name} faqat {who} uchun sotiladi (UZEX qoidasi). Bu buyurtmani qabul qila olmaymiz.",
        "other": "Pilotda hozircha faqat sement bor. Boshqa tovarlar keyingi bosqichda qo‘shiladi.",
        "small": "Eng kami 1 tonna (20 qop).",
        "large": "Katta hajm: {q} t. Kompaniya hisobidan tasdiqlash kerak bo‘ladi.",
        "low": "Chegarangiz hozirgi narxdan past ({ref}). Bu raundda olish ehtimoli kam.",
        "high": "Chegarangiz odatdagidan ancha yuqori (hozir {ref}). Siz chegaradan emas, bozor narxidan to‘laysiz, lekin taklif kam bo‘lsa narx shu chegaragacha chiqishi mumkin.",
        "deadline": "Eng tez yetkazish {days} kun. Muddatni {days} kunga uzaytirsangiz, ko‘proq zavod mos keladi.",
        "funds": "Hisobda yetarli pul yo‘q: {need} kerak, {have} bor.",
    },
    "ru": {
        "restricted": "{name} продаётся только для: {who} (правило UZEX). Эту заявку принять нельзя.",
        "other": "В пилоте пока только цемент. Другие товары добавим на следующем этапе.",
        "small": "Минимум 1 тонна (20 мешков).",
        "large": "Большой объём: {q} т. Нужно подтверждение от компании.",
        "low": "Ваш предел ниже текущей цены ({ref}). В этом раунде шанс купить низкий.",
        "high": "Ваш предел заметно выше обычного (сейчас {ref}). Вы платите рыночную цену, а не предел, но при нехватке товара цена может дойти до предела.",
        "deadline": "Самая быстрая доставка — {days} дн. Если продлить срок до {days} дн., подойдёт больше заводов.",
        "funds": "Недостаточно денег на счёте: нужно {need}, есть {have}.",
    },
}


def check(draft: Draft, exchange: Exchange, account_id: str, lang: str = "uz") -> list[dict]:
    t = TEXT[lang]
    notices: list[dict] = []

    def add(level: str, code: str, text: str) -> None:
        notices.append({"level": level, "code": code, "text": text})

    if draft.restricted:
        r = next(x for x in RESTRICTED if x.id == draft.restricted)
        add(
            "block",
            "restricted",
            t["restricted"].format(
                name=r.uz if lang == "uz" else r.ru, who=r.who_uz if lang == "uz" else r.who_ru
            ),
        )
        return notices
    if draft.other_product and not draft.product:
        add("block", "other", t["other"])
        return notices
    if draft.quantity is not None:
        if draft.quantity < MIN_TONNES:
            add("block", "small", t["small"])
        elif draft.quantity > LARGE_TONNES:
            add("warn", "large", t["large"].format(q=f"{draft.quantity:g}"))
    if draft.region and draft.product and draft.limit:
        ref = exchange.reference_price(draft.region, draft.product)
        if ref:
            ratio = draft.limit / ref
            if ratio < LOW_RATIO:
                add("warn", "low", t["low"].format(ref=money(ref, lang)))
            elif ratio > HIGH_RATIO:
                add("warn", "high", t["high"].format(ref=money(ref, lang)))
    if draft.region and draft.product:
        fastest = exchange.fastest_days(draft.region, draft.product)
        if fastest and (draft.deadline_days or 7) < fastest:
            add("warn", "deadline", t["deadline"].format(days=fastest))
    if draft.quantity and draft.limit:
        need = draft.quantity * draft.limit * (1 + FEE_RATE)
        account = exchange.account(account_id)
        have = account.balance - account.held
        if need > have:
            add("block", "funds", t["funds"].format(need=money(need, lang), have=money(have, lang)))
    return notices
