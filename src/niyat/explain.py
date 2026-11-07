from niyat.catalog import PRODUCTS
from niyat.exchange import LiveIntent, RoundRecord
from niyat.regions import REGIONS


def money(value: float, lang: str = "uz") -> str:
    text = f"{round(value):,}".replace(",", " ")
    return f"{text} so‘m" if lang == "uz" else f"{text} сум"


def tonnes(value: float) -> str:
    return f"{value:g}"


TEXT = {
    "uz": {
        "bought": "{t} t sotib olindi: tonnasi {price}, eshigingizgacha yetkazib berish bilan.",
        "partial": "{t} t sotib olindi ({q} t dan). Tonnasi {price}, yetkazib berish bilan.",
        "plain": "Narx qanday chiqdi: {seller} zavodi narxi {ask} + yetkazish {freight} ({km} km). Bu raundda sement yetarli edi, narx ko‘tarilmadi.",
        "scarce": "Narx qanday chiqdi: bu raundda yaqin zavodlarda sement kam edi. Xaridorlar ko‘p bo‘lgani uchun {seller} zavodi narxi {ask}dan {plant}ga chiqdi, ustiga yetkazish {freight} ({km} km).",
        "same": "{zone} uchun bu raundda yagona narx: {zone_price}. Hamma bir xil qoida bilan to‘laydi.",
        "premium": "Muddatingiz qisqa bo‘lgani uchun faqat yaqin zavodlar mos keldi, shuning uchun narx hudud narxidan ({zone_price}) biroz yuqori.",
        "saved": "Siz tonnasiga {limit} gacha to‘lashga tayyor edingiz. Bozor narxi pastroq chiqdi: {saved} tejaldi.",
        "pool": "Yukingiz yana {others} ta xaridor yuki bilan birga {trucks} ta mashinada keladi. Shuning uchun kichik buyurtma ham ulgurji narxda.",
        "rest": "Qolgan {rest} t uchun pulingiz qaytarildi.",
        "money": "Hisobdan yechildi: sement {cost} + birja yig‘imlari {fees}. Qaytarildi: {refund}. Zavodga pul sement yetib kelgandan keyin o‘tadi.",
        "eta": "Taxminiy yetib kelish: {date}.",
        "none": "Bu raundda sotib olinmadi. Pulingiz to‘liq qaytdi.",
        "above": "{zone}da narx tonnasiga {price} bo‘ldi, sizning chegarangiz {limit}. Keyingi raundda {suggest} qo‘ysangiz, olish ehtimoli yuqori.",
        "deadline": "Muddat juda qisqa: eng yaqin zavod {days} kunda yetkaza oladi.",
        "no_seller": "Bu mahsulotni hozir hech kim sotmayapti.",
        "waiting": "Niyatingiz qabul qilindi. Pul bloklandi va {round}-raundni kutmoqda.",
        "delivered": "Sement yetib keldi. Pul zavodga va tashuvchiga o‘tkazildi.",
        "cancelled": "Niyat bekor qilindi. Pul to‘liq qaytdi.",
        "held": "{t} t sotib olindi va zavod omborida saqlanmoqda. Tonnasi {price}.",
        "plain_hold": "Narx qanday chiqdi: {seller} zavodi narxi {ask}. Bu raundda sement yetarli edi, narx ko‘tarilmadi.",
        "scarce_hold": "Narx qanday chiqdi: xaridorlar ko‘p bo‘lgani uchun {seller} zavodi narxi {ask}dan {plant}ga chiqdi.",
        "receipt": "Portfelingizda turibdi: istalgan raundda sotishingiz yoki uyga yetkazishni so‘rashingiz mumkin.",
        "above_hold": "Bu raundda zavod narxi tonnasiga {price} bo‘ldi, sizning chegarangiz {limit}. Keyingi raundda {suggest} qo‘ysangiz, olish ehtimoli yuqori.",
        "sell_waiting": "{t} t sotuvga qo‘yildi, eng kami tonnasiga {min}. {round}-raundni kutmoqda.",
        "sell_sold": "{t} t sotildi: tonnasi {price}. Hisobingizga {net} tushdi (yig‘imlar {fees}).",
        "sell_partial": "{t} t sotildi ({q} t dan): tonnasi {price}. Hisobingizga {net} tushdi. Qolgani portfelda.",
        "sell_unsold": "Bu raundda sotilmadi: bozor narxi siz so‘ragan {min}dan past bo‘ldi. Tovar portfelda qoldi.",
        "sell_note": "Siz so‘ragan eng kam narxni emas, raunddagi bozor narxini olasiz.",
        "sell_cancelled": "Sotuv bekor qilindi.",
    },
    "ru": {
        "bought": "Куплено {t} т: {price} за тонну с доставкой до вас.",
        "partial": "Куплено {t} т (из {q} т). {price} за тонну с доставкой.",
        "plain": "Как сложилась цена: цена завода {seller} {ask} + доставка {freight} ({km} км). Цемента в этом раунде хватало, цена не выросла.",
        "scarce": "Как сложилась цена: на ближних заводах цемента было мало. Покупателей было больше, поэтому цена завода {seller} выросла с {ask} до {plant}, плюс доставка {freight} ({km} км).",
        "same": "Единая цена для региона «{zone}» в этом раунде: {zone_price}. Все платят по одному правилу.",
        "premium": "Из-за короткого срока подошли только ближние заводы, поэтому цена чуть выше цены региона ({zone_price}).",
        "saved": "Вы были готовы платить до {limit} за тонну. Рынок дал дешевле: экономия {saved}.",
        "pool": "Ваш груз едет в общей машине с другими покупателями (ещё {others}), машин: {trucks}. Поэтому даже малый заказ — по оптовой цене.",
        "rest": "За оставшиеся {rest} т деньги возвращены.",
        "money": "Списано: цемент {cost} + сборы биржи {fees}. Возвращено: {refund}. Заводу деньги уйдут после доставки.",
        "eta": "Ожидаемая доставка: {date}.",
        "none": "В этом раунде не куплено. Деньги полностью возвращены.",
        "above": "Цена в регионе «{zone}» была {price} за тонну, ваш предел {limit}. Поставьте {suggest} в следующем раунде — шанс высокий.",
        "deadline": "Срок слишком короткий: ближайший завод доставит за {days} дн.",
        "no_seller": "Сейчас этот товар никто не продаёт.",
        "waiting": "Намерение принято. Деньги заблокированы, ждём раунд №{round}.",
        "delivered": "Цемент доставлен. Деньги переведены заводу и перевозчику.",
        "cancelled": "Намерение отменено. Деньги полностью возвращены.",
        "held": "Куплено {t} т, хранится на складе завода. {price} за тонну.",
        "plain_hold": "Как сложилась цена: цена завода {seller} {ask}. Цемента хватало, цена не выросла.",
        "scarce_hold": "Как сложилась цена: покупателей было больше, цена завода {seller} выросла с {ask} до {plant}.",
        "receipt": "Товар в вашем портфеле: можно продать в любом раунде или заказать доставку.",
        "above_hold": "Цена завода в этом раунде была {price} за тонну, ваш предел {limit}. Поставьте {suggest} в следующем раунде — шанс высокий.",
        "sell_waiting": "{t} т выставлено на продажу, минимум {min} за тонну. Ждём раунд №{round}.",
        "sell_sold": "Продано {t} т по {price} за тонну. На счёт поступило {net} (сборы {fees}).",
        "sell_partial": "Продано {t} т (из {q} т) по {price} за тонну. На счёт поступило {net}. Остаток в портфеле.",
        "sell_unsold": "В этом раунде не продано: рынок был ниже вашего минимума {min}. Товар остался в портфеле.",
        "sell_note": "Вы получаете рыночную цену раунда, а не свой минимум.",
        "sell_cancelled": "Продажа отменена.",
    },
}


def region_name(region: str, lang: str) -> str:
    r = REGIONS[region]
    return r.uz if lang == "uz" else r.ru


def explain(
    live: LiveIntent, record: RoundRecord | None, lang: str = "uz", next_round: int = 1
) -> dict:
    t = TEXT[lang]
    intent = live.intent
    fill = live.fill
    lines: list[str] = []
    m = lambda v: money(v, lang)  # noqa: E731
    if live.status == "waiting":
        return {"headline": t["waiting"].format(round=next_round), "lines": []}
    if live.status == "cancelled":
        return {"headline": t["cancelled"], "lines": []}
    assert fill is not None and record is not None
    zone = region_name(intent.region, lang) if intent.region else None
    if fill.filled and live.hold:
        return explain_hold(live, record, lang)
    if fill.filled:
        key = "bought" if fill.reason == "filled" else "partial"
        headline = t[key].format(
            t=tonnes(fill.filled), q=tonnes(intent.quantity), price=m(fill.price)
        )
        offers = {o.id: o for o in record.offers}
        main = max(fill.allocations, key=lambda a: a.tonnes)
        offer = offers[main.offer_id]
        rent = record.result.seller_rents.get(offer.id, 0.0)
        source = f"{offer.seller} ({region_name(offer.region, lang)})"
        common = {
            "seller": source,
            "ask": m(offer.ask),
            "freight": m(main.freight),
            "km": round(main.km),
        }
        if rent < 1:
            lines.append(t["plain"].format(**common))
        else:
            lines.append(t["scarce"].format(plant=m(main.plant_price), **common))
        zone_price = record.result.zone_prices.get((intent.region, intent.product))
        if zone_price and abs(zone_price - fill.price) < 1:
            lines.append(t["same"].format(zone=zone, zone_price=m(zone_price)))
        elif zone_price:
            lines.append(t["premium"].format(zone_price=m(zone_price)))
        saved = (intent.limit - fill.price) * fill.filled
        if saved >= 1:
            lines.append(t["saved"].format(limit=m(intent.limit), saved=m(saved)))
        if live.shipment and live.shipment.buyers > 1:
            lines.append(
                t["pool"].format(others=live.shipment.buyers - 1, trucks=live.shipment.trucks)
            )
        if fill.reason == "partial":
            lines.append(t["rest"].format(rest=tonnes(round(intent.quantity - fill.filled, 3))))
        lines.append(t["money"].format(cost=m(live.cost), fees=m(live.fees), refund=m(live.refund)))
        if live.status == "delivered":
            lines.append(t["delivered"])
        elif live.eta:
            lines.append(t["eta"].format(date=live.eta.strftime("%d.%m.%Y")))
        return {"headline": headline, "lines": lines}
    if fill.reason == "price_above_limit" and live.hold:
        suggest = round(fill.price * 1.02, -3)
        lines.append(
            t["above_hold"].format(price=m(fill.price), limit=m(intent.limit), suggest=m(suggest))
        )
    elif fill.reason == "price_above_limit":
        suggest = round(fill.price * 1.02, -3)
        lines.append(
            t["above"].format(
                zone=zone, price=m(fill.price), limit=m(intent.limit), suggest=m(suggest)
            )
        )
    elif fill.reason == "deadline":
        lines.append(t["deadline"].format(days="?"))
    else:
        lines.append(t["no_seller"])
    return {"headline": t["none"], "lines": lines}


def product_name(product: str, lang: str) -> str:
    p = PRODUCTS[product]
    return p.uz if lang == "uz" else p.ru


def explain_hold(live: LiveIntent, record: RoundRecord, lang: str) -> dict:
    t = TEXT[lang]
    m = lambda v: money(v, lang)  # noqa: E731
    fill = live.fill
    intent = live.intent
    offers = {o.id: o for o in record.offers}
    main = max(fill.allocations, key=lambda a: a.tonnes)
    offer = offers[main.offer_id]
    rent = record.result.seller_rents.get(offer.id, 0.0)
    source = f"{offer.seller} ({region_name(offer.region, lang)})"
    lines = []
    if rent < 1:
        lines.append(t["plain_hold"].format(seller=source, ask=m(offer.ask)))
    else:
        lines.append(
            t["scarce_hold"].format(seller=source, ask=m(offer.ask), plant=m(main.plant_price))
        )
    saved = (intent.limit - fill.price) * fill.filled
    if saved >= 1:
        lines.append(t["saved"].format(limit=m(intent.limit), saved=m(saved)))
    if fill.reason == "partial":
        lines.append(t["rest"].format(rest=tonnes(round(intent.quantity - fill.filled, 3))))
    lines.append(t["money"].format(cost=m(live.cost), fees=m(live.fees), refund=m(live.refund)))
    lines.append(t["receipt"])
    return {
        "headline": t["held"].format(t=tonnes(fill.filled), price=m(fill.price)),
        "lines": lines,
    }


def explain_sell(order, lang: str = "uz", next_round: int = 1) -> dict:
    t = TEXT[lang]
    m = lambda v: money(v, lang)  # noqa: E731
    if order.status == "waiting":
        return {
            "headline": t["sell_waiting"].format(
                t=tonnes(order.tonnes), min=m(order.min_price), round=next_round
            ),
            "lines": [t["sell_note"]],
        }
    if order.status == "cancelled":
        return {"headline": t["sell_cancelled"], "lines": []}
    if order.status == "unsold":
        return {"headline": t["sell_unsold"].format(min=m(order.min_price)), "lines": []}
    key = "sell_sold" if order.status == "sold" else "sell_partial"
    net = order.proceeds - order.fees
    headline = t[key].format(
        t=tonnes(order.sold),
        q=tonnes(order.tonnes),
        price=m(order.price),
        net=m(net),
        fees=m(order.fees),
    )
    lines = [t["sell_note"]] if order.price and order.price > order.min_price + 1 else []
    return {"headline": headline, "lines": lines}
