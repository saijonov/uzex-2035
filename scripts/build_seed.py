import json
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from niyat.regions import REGISTRY_NAMES

QUERY = """
with cement as (
  select
    seller_name,
    seller_region,
    buyer_region,
    case when product || ' ' || coalesce(brand, '') like '%42,5%' then 'cement_425' else 'cement_325' end as product_id,
    unit_price,
    mass_t
  from registry
  where product_family = 'ПОРТЛАНДЦЕМЕНТ'
    and deal_date >= date '2026-01-01'
    and currency ilike '%сум%'
    and not is_cancelled
)
select seller_name, seller_region, product_id,
       count(*) as deals,
       round(median(unit_price)) as median_price,
       round(sum(mass_t)) as tonnes
from cement
group by all
having count(*) >= 40
order by tonnes desc
"""

BUYERS = """
select buyer_region, count(*) as deals, round(median(mass_t), 1) as median_tonnes
from registry
where product_family = 'ПОРТЛАНДЦЕМЕНТ' and deal_date >= date '2026-01-01' and not is_cancelled
group by all
"""


def main() -> None:
    registry, output = Path(sys.argv[1]), Path(sys.argv[2])
    con = duckdb.connect(str(registry), read_only=True)
    sellers = []
    for name, region, product_id, deals, price, tonnes in con.sql(QUERY).fetchall():
        if region not in REGISTRY_NAMES:
            continue
        sellers.append(
            {
                "name": name.strip(),
                "region": REGISTRY_NAMES[region],
                "product": product_id,
                "deals": int(deals),
                "median_price": float(price),
                "tonnes": float(tonnes),
            }
        )
    buyers = {
        REGISTRY_NAMES[region]: {"deals": int(deals), "median_tonnes": float(median)}
        for region, deals, median in con.sql(BUYERS).fetchall()
        if region in REGISTRY_NAMES
    }
    output.write_text(
        json.dumps(
            {
                "source": "Fictional UZEX hackathon registry, cement deals in 2026",
                "sellers": sellers,
                "buyers": buyers,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n"
    )
    print(f"{len(sellers)} seller lines, {len(buyers)} buyer regions -> {output}")


if __name__ == "__main__":
    main()
