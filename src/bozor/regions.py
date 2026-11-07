import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    id: str
    name: str
    city: str
    lat: float
    lon: float
    words: tuple[str, ...]


REGIONS: dict[str, Region] = {
    r.id: r
    for r in (
        Region("tashkent_city", "Toshkent shahri", "Toshkent", 41.311, 69.279, ("toshkent", "tashkent", "ташкент", "тошкент")),
        Region("tashkent", "Toshkent viloyati", "Nurafshon", 41.040, 69.350, ("toshkent viloyati", "nurafshon", "chirchiq", "olmaliq", "angren", "ташкентская", "чирчик", "алмалык", "ангрен")),
        Region("andijan", "Andijon viloyati", "Andijon", 40.783, 72.344, ("andijon", "andijan", "андижан", "андижон")),
        Region("fergana", "Farg‘ona viloyati", "Farg‘ona", 40.389, 71.784, ("farg'ona", "fargona", "fergana", "qo'qon", "qoqon", "marg'ilon", "фергана", "фарғона", "коканд")),
        Region("namangan", "Namangan viloyati", "Namangan", 40.998, 71.672, ("namangan", "наманган")),
        Region("syrdarya", "Sirdaryo viloyati", "Guliston", 40.489, 68.784, ("sirdaryo", "guliston", "сырдарья", "гулистан", "сирдарё")),
        Region("jizzakh", "Jizzax viloyati", "Jizzax", 40.116, 67.842, ("jizzax", "jizzakh", "джизак", "жиззах")),
        Region("samarkand", "Samarqand viloyati", "Samarqand", 39.654, 66.976, ("samarqand", "samarkand", "самарканд", "самарқанд")),
        Region("kashkadarya", "Qashqadaryo viloyati", "Qarshi", 38.860, 65.790, ("qashqadaryo", "qarshi", "shahrisabz", "kitob", "кашкадарья", "карши", "қарши", "шахрисабз")),
        Region("surkhandarya", "Surxondaryo viloyati", "Termiz", 37.224, 67.278, ("surxondaryo", "termiz", "termez", "сурхандарья", "термез", "термиз")),
        Region("bukhara", "Buxoro viloyati", "Buxoro", 39.768, 64.421, ("buxoro", "bukhara", "бухара", "бухоро")),
        Region("navoi", "Navoiy viloyati", "Navoiy", 40.103, 65.374, ("navoiy", "navoi", "навои", "навоий")),
        Region("khorezm", "Xorazm viloyati", "Urganch", 41.550, 60.631, ("xorazm", "urganch", "urgench", "хорезм", "ургенч", "урганч")),
        Region("karakalpakstan", "Qoraqalpog‘iston", "Nukus", 42.460, 59.603, ("qoraqalpog'iston", "qoraqalpogiston", "nukus", "каракалпакстан", "нукус")),
    )
}

REGISTRY = {
    "Toshkent shahri": "tashkent_city",
    "Toshkent viloyati": "tashkent",
    "Andijon viloyati": "andijan",
    "Farg‘ona viloyati": "fergana",
    "Namangan viloyati": "namangan",
    "Sirdaryo viloyati": "syrdarya",
    "Jizzax viloyati": "jizzakh",
    "Samarqand viloyati": "samarkand",
    "Qashqadaryo viloyati": "kashkadarya",
    "Surxondaryo viloyati": "surkhandarya",
    "Buxoro viloyati": "bukhara",
    "Navoiy viloyati": "navoi",
    "Xorazm viloyati": "khorezm",
    "Qoraqalpog‘iston Respublikasi": "karakalpakstan",
}

LOCAL_KM = 40


def normalize(text: str) -> str:
    return re.sub(r"[ʻʼ’‘`']", "'", text.lower())


def find_region(text: str) -> str | None:
    text = normalize(text)
    hits = [(len(w), r.id) for r in REGIONS.values() for w in r.words if w in text]
    return max(hits)[1] if hits else None


def straight_km(a: str, b: str) -> float:
    ra, rb = REGIONS[a], REGIONS[b]
    p1, p2 = math.radians(ra.lat), math.radians(rb.lat)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(rb.lon - ra.lon) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))
