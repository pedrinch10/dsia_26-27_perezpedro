"""Repository: encapsula el origen de datos del dataset de tenis (SRP + DIP).

Fuente del dataset: partidos ATP reales 2019/2021/2022/2023 (formato Jeff
Sackmann), ver proyecto_i/README.md para atribución y licencia.
"""

from pathlib import Path
from typing import Protocol

import pandas as pd


class DataLoadError(Exception):
    """Error al cargar datos de origen."""


class TennisRepository(Protocol):
    """Contrato mínimo: cualquier origen debe poder devolver un DataFrame."""

    def load(self) -> pd.DataFrame: ...


class CsvTennisRepository:
    """Implementación concreta: lee el CSV de partidos de tenis."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> pd.DataFrame:
        if not self._path.exists():
            raise DataLoadError(f"No existe el fichero: {self._path}")
        return pd.read_csv(self._path)
