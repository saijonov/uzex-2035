from dataclasses import dataclass


@dataclass(frozen=True)
class Good:
    id: str
    name: str
    family: str
    category: str
    words: tuple[str, ...]


@dataclass(frozen=True)
class Restricted:
    id: str
    name: str
    who: str
    words: tuple[str, ...]


GOODS: dict[str, Good] = {
    g.id: g
    for g in (
        Good("cement", "Sement", "ПОРТЛАНДЦЕМЕНТ", "Qurilish", ("sement", "tsement", "цемент", "семент")),
        Good("rebar", "Po‘lat armatura", "Арматура стальная", "Qurilish", ("armatura", "арматур")),
        Good("gypsum", "Qurilish gipsi", "Гипс", "Qurilish", ("gips", "гипс")),
        Good("lime", "So‘ndirilmagan ohak", "Известь негашеная", "Qurilish", ("ohak", "известь", "извест")),
        Good("flour", "Bug‘doy uni", "МУКА ПШЕНИЧНАЯ", "Oziq-ovqat", ("un", "uni", "unga", "undan", "мука", "муки", "муку")),
        Good("sugar", "Oq shakar", "Сахар белый", "Oziq-ovqat", ("shakar", "сахар", "шакар")),
        Good("rice", "Guruch", "Рис шлифованный", "Oziq-ovqat", ("guruch", "рис", "риса", "рису", "гуруч")),
        Good("cottonseed_oil", "Paxta yog‘i", "Масло хлопковое", "Oziq-ovqat", ("paxta yog", "хлопковое масло", "масло хлопковое", "пахта ёғи")),
        Good("sunflower_oil", "Kungaboqar yog‘i", "Подсолнечное масло", "Oziq-ovqat", ("kungaboqar", "подсолнечн")),
        Good("salt", "Osh tuzi", "Соль пищевая", "Oziq-ovqat", ("tuz", "tuzi", "tuzga", "соль", "соли")),
        Good("feed", "Omuxta yem", "Кормосмесь", "Qishloq xo‘jaligi", ("yem", "yemi", "omuxta", "комбикорм", "корм")),
        Good("polyethylene", "Polietilen", "ПОЛИЭТИЛЕН", "Kimyo", ("polietilen", "полиэтилен")),
    )
}

RESTRICTED: tuple[Restricted, ...] = (
    Restricted("cotton", "Paxta", "faqat qayta ishlash quvvati bor korxonalarga", ("paxta", "хлопок", "хлопк")),
    Restricted("wheat", "Bug‘doy", "faqat ro‘yxatdagi un ishlab chiqaruvchi korxonalarga", ("bug'doy", "bugdoy", "пшениц")),
    Restricted("ai80", "AI-80 benzin", "faqat yoqilg‘i quyish shoxobchalariga", ("ai-80", "ai80", "аи-80", "аи80")),
    Restricted("alcohol", "Etil spirti", "faqat litsenziyasi bor ishlab chiqaruvchilarga", ("spirt", "спирт")),
    Restricted("oil", "Neft va gaz kondensati", "faqat litsenziyasi bor korxonalarga", ("neft", "нефть", "kondensat", "конденсат")),
    Restricted("precious", "Oltin va kumush", "faqat zargarlik buyumlari ishlab chiqaruvchilarga", ("oltin", "kumush", "золот", "серебр")),
)

EXCHANGE_FEE = 0.0013
CLEARING_FEE = 0.0005
FREIGHT_PER_TONNE_KM = 450
TRUCK_TONNES = 20
KM_PER_DAY = 450
