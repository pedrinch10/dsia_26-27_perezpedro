"""Validator: reglas de negocio de calidad de datos (SRP)."""

from dataclasses import dataclass

import pandas as pd


class ValidationError(Exception):
    """Datos que no cumplen reglas de negocio."""


MIN_UNITS = 0
MIN_PRICE = 0


@dataclass(frozen=True)
class SalesRecord:
    region: str
    product: str
    units: float
    unit_price: float

    @property
    def amount(self) -> float:
        return self.units * self.unit_price


class SalesValidator:
    def split(self, frame: pd.DataFrame) -> tuple[list[SalesRecord], pd.DataFrame]:
        work = frame.copy()
        work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
        work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")

        ok = (
            work["unidades"].notna() & (work["unidades"] > MIN_UNITS)
            & work["precio_unitario"].notna() & (work["precio_unitario"] > MIN_PRICE)
        )

        validos = [
            SalesRecord(
                region=str(row.region),
                product=str(row.producto),
                units=float(row.unidades),
                unit_price=float(row.precio_unitario),
            )
            for row in work.loc[ok].itertuples(index=False)
        ]
        errores = work.loc[~ok].copy()
        return validos, errores
