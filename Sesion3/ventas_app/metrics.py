"""Metrics: agregaciones sobre registros ya validados (SRP + OCP)."""

from .validator import SalesRecord


class SalesMetrics:
    def total_by_region(self, records: list[SalesRecord]) -> dict[str, float]:
        totals: dict[str, float] = {}
        for record in records:
            totals[record.region] = totals.get(record.region, 0.0) + record.amount
        return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))

    def top_products(self, records: list[SalesRecord], n: int = 3) -> dict[str, float]:
        totals: dict[str, float] = {}
        for record in records:
            totals[record.product] = totals.get(record.product, 0.0) + record.amount
        ordered = sorted(totals.items(), key=lambda item: item[1], reverse=True)
        return dict(ordered[:n])