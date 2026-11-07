import json
import math
import sys
import time
import urllib.request
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bozor.regions import REGIONS

OSRM = "https://router.project-osrm.org/route/v1/driving/{}?overview=simplified&geometries=geojson"
VALLEY = {"andijan", "fergana", "namangan"}
KAMCHIK = [(41.0167, 70.1436), (40.8736, 71.1092)]
GUZAR = (38.6206, 66.2481)
ABROAD = {
    "Xo‘jand": (40.2833, 69.6222),
    "Chimkent": (42.3000, 69.6000),
    "Turkmanobod": (39.0733, 63.5786),
    "Dashoguz": (41.8363, 59.9666),
    "O‘sh": (40.5300, 72.8000),
    "Dushanbe": (38.5600, 68.7900),
}


def km(a: tuple[float, float], b: tuple[float, float]) -> float:
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = (
        math.sin((p2 - p1) / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2
    )
    return 2 * 6371 * math.asin(math.sqrt(h))


def fetch(points: list[tuple[float, float]]) -> dict:
    path = ";".join(f"{lon},{lat}" for lat, lon in points)
    request = urllib.request.Request(OSRM.format(path), headers={"User-Agent": "bozor-demo/0.2"})
    with urllib.request.urlopen(request, timeout=30) as response:
        route = json.load(response)["routes"][0]
    line = [(round(lat, 3), round(lon, 3)) for lon, lat in route["geometry"]["coordinates"]]
    return {
        "km": round(route["distance"] / 1000),
        "hours": round(route["duration"] / 3600, 1),
        "line": line,
    }


def main() -> None:
    output = Path(sys.argv[1])
    routes = json.loads(output.read_text()) if output.exists() else {}
    for a, b in combinations(sorted(REGIONS), 2):
        key = f"{a}|{b}"
        if key in routes:
            continue
        ra, rb = REGIONS[a], REGIONS[b]
        start, end = (ra.lat, ra.lon), (rb.lat, rb.lon)
        via = KAMCHIK if (a in VALLEY) != (b in VALLEY) else []
        via = via + [GUZAR] if "surkhandarya" in (a, b) else via
        routes[key] = fetch([start, *sorted(via, key=lambda p: km(start, p)), end])
        near = [n for n, p in ABROAD.items() if min(km(p, q) for q in routes[key]["line"]) < 15]
        print(key, routes[key]["km"], "km", "near " + ", ".join(near) if near else "")
        output.write_text(json.dumps(routes, ensure_ascii=False, separators=(",", ":")))
        time.sleep(1.2)


if __name__ == "__main__":
    main()
