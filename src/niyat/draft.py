from dataclasses import asdict, dataclass, replace


@dataclass(frozen=True)
class Draft:
    product: str | None = None
    quantity: float | None = None
    region: str | None = None
    deadline_days: int | None = None
    limit: float | None = None
    budget: float | None = None
    cement: bool = False
    other_product: str | None = None
    restricted: str | None = None

    def merge(self, update: "Draft") -> "Draft":
        changes = {k: v for k, v in asdict(update).items() if v not in (None, False)}
        merged = replace(self, **changes)
        if merged.product:
            merged = replace(merged, cement=True, other_product=None)
        if merged.limit is None and merged.budget and merged.quantity:
            merged = replace(merged, limit=round(merged.budget / merged.quantity, -3))
        return merged

    def missing(self) -> list[str]:
        order = [
            ("product", self.product),
            ("quantity", self.quantity),
            ("region", self.region),
            ("limit", self.limit),
        ]
        return [name for name, value in order if value is None]

    def to_dict(self) -> dict:
        return asdict(self)
