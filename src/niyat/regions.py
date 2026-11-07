import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    id: str
    uz: str
    ru: str
    lat: float
    lon: float
    aliases: tuple[str, ...]


REGIONS: dict[str, Region] = {
    r.id: r
    for r in [
        Region(
            "tashkent_city",
            "Toshkent shahri",
            "г. Ташкент",
            41.311,
            69.279,
            ("toshkent shahri", "toshkent", "tashkent", "ташкент", "тошкент"),
        ),
        Region(
            "tashkent",
            "Toshkent viloyati",
            "Ташкентская обл.",
            41.040,
            69.350,
            (
                "toshkent viloyati",
                "chirchiq",
                "olmaliq",
                "angren",
                "ташкентская",
                "тошкент вилояти",
                "чирчик",
                "алмалык",
            ),
        ),
        Region(
            "andijan",
            "Andijon viloyati",
            "Андижанская обл.",
            40.783,
            72.344,
            ("andijon", "andijan", "андижан", "андижон"),
        ),
        Region(
            "fergana",
            "Farg‘ona viloyati",
            "Ферганская обл.",
            40.389,
            71.784,
            (
                "farg'ona",
                "fargona",
                "farg‘ona",
                "fergana",
                "qo'qon",
                "qoqon",
                "margilon",
                "фергана",
                "фарғона",
                "коканд",
            ),
        ),
        Region(
            "namangan",
            "Namangan viloyati",
            "Наманганская обл.",
            40.998,
            71.672,
            ("namangan", "наманган"),
        ),
        Region(
            "syrdarya",
            "Sirdaryo viloyati",
            "Сырдарьинская обл.",
            40.489,
            68.784,
            ("sirdaryo", "guliston", "сырдарья", "гулистан", "сирдарё"),
        ),
        Region(
            "jizzakh",
            "Jizzax viloyati",
            "Джизакская обл.",
            40.116,
            67.842,
            ("jizzax", "jizzakh", "джизак", "жиззах"),
        ),
        Region(
            "samarkand",
            "Samarqand viloyati",
            "Самаркандская обл.",
            39.654,
            66.976,
            ("samarqand", "samarkand", "самарканд", "самарқанд"),
        ),
        Region(
            "kashkadarya",
            "Qashqadaryo viloyati",
            "Кашкадарьинская обл.",
            38.860,
            65.790,
            (
                "qashqadaryo",
                "qarshi",
                "kashkadarya",
                "karshi",
                "kitob",
                "shahrisabz",
                "кашкадарья",
                "карши",
                "қарши",
                "китаб",
                "шахрисабз",
            ),
        ),
        Region(
            "surkhandarya",
            "Surxondaryo viloyati",
            "Сурхандарьинская обл.",
            37.224,
            67.278,
            ("surxondaryo", "termiz", "surkhandarya", "termez", "сурхандарья", "термез", "термиз"),
        ),
        Region(
            "bukhara",
            "Buxoro viloyati",
            "Бухарская обл.",
            39.768,
            64.421,
            ("buxoro", "bukhara", "бухара", "бухоро"),
        ),
        Region(
            "navoi",
            "Navoiy viloyati",
            "Навоийская обл.",
            40.103,
            65.374,
            ("navoiy", "navoi", "навои", "навоий"),
        ),
        Region(
            "khorezm",
            "Xorazm viloyati",
            "Хорезмская обл.",
            41.550,
            60.631,
            ("xorazm", "urganch", "khorezm", "urgench", "хорезм", "ургенч", "урганч"),
        ),
        Region(
            "karakalpakstan",
            "Qoraqalpog‘iston Respublikasi",
            "Республика Каракалпакстан",
            42.460,
            59.603,
            (
                "qoraqalpog'iston",
                "qoraqalpogiston",
                "qoraqalpog‘iston",
                "nukus",
                "karakalpakstan",
                "каракалпакстан",
                "нукус",
            ),
        ),
    ]
}

REGISTRY_NAMES = {r.uz: r.id for r in REGIONS.values()}

ROAD_FACTOR = 1.3
LOCAL_KM = 40.0


def distance_km(a: str, b: str) -> float:
    if a == b:
        return LOCAL_KM
    ra, rb = REGIONS[a], REGIONS[b]
    p1, p2 = math.radians(ra.lat), math.radians(rb.lat)
    dp = p2 - p1
    dl = math.radians(rb.lon - ra.lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * 6371.0 * math.asin(math.sqrt(h)) * ROAD_FACTOR, 1)


def normalize(text: str) -> str:
    return re.sub(r"[ʻʼ’‘`']", "'", text.lower())


def find_region(text: str) -> str | None:
    t = normalize(text)
    best: tuple[int, str] | None = None
    for region in REGIONS.values():
        for alias in region.aliases:
            a = normalize(alias)
            if re.search(r"(?<![\w])" + re.escape(a), t):
                if best is None or len(a) > best[0]:
                    best = (len(a), region.id)
    return best[1] if best else None
