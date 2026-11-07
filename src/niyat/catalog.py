from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    id: str
    uz: str
    ru: str
    unit: str


PRODUCTS: dict[str, Product] = {
    "cement_325": Product("cement_325", "Sement M400 (ЦЕМ 32,5)", "Цемент М400 (ЦЕМ 32,5)", "t"),
    "cement_425": Product("cement_425", "Sement M500 (ЦЕМ 42,5)", "Цемент М500 (ЦЕМ 42,5)", "t"),
}


@dataclass(frozen=True)
class Restriction:
    id: str
    uz: str
    ru: str
    who_uz: str
    who_ru: str
    keywords: tuple[str, ...]


RESTRICTED: tuple[Restriction, ...] = (
    Restriction("ai80", "AI-80 benzin", "бензин АИ-80", "faqat yoqilg‘i quyish shoxobchalari", "только автозаправочные станции", ("ai-80", "ai80", "аи-80", "аи80")),
    Restriction("wheat", "Bug‘doy", "пшеница", "un ishlab chiqaruvchi korxonalar ro‘yxati bo‘yicha", "мукомольные предприятия по списку", ("bug'doy", "bugdoy", "bug‘doy", "пшениц")),
    Restriction("cotton", "Paxta tolasi", "хлопковое волокно", "qayta ishlash quvvati bor korxonalar", "предприятия с мощностями переработки", ("paxta tolasi", "хлопковое волокно", "хлопок")),
    Restriction("alcohol", "Iste’mol etil spirti", "пищевой этиловый спирт", "litsenziyasi bor ishlab chiqaruvchilar", "лицензированные производители", ("spirt", "спирт")),
    Restriction("oil", "Neft va gaz kondensati", "нефть и газовый конденсат", "litsenziyasi bor korxonalar", "лицензированные предприятия", ("neft", "нефть", "kondensat", "конденсат")),
    Restriction("precious", "Oltin va kumush", "золото и серебро", "zargarlik buyumlari ishlab chiqaruvchilar", "производители ювелирных изделий", ("oltin", "kumush", "золот", "серебр")),
)

EXCHANGE_FEE_BUYER = 0.0013
CLEARING_FEE = 0.0005
TRUCK_TONNES = 20.0
FREIGHT_PER_TONNE_KM = 450.0
KM_PER_DAY = 450.0


def delivery_days(km: float) -> int:
    return 1 + int(km // KM_PER_DAY)


def freight_per_tonne(km: float) -> float:
    return round(km * FREIGHT_PER_TONNE_KM, 2)
