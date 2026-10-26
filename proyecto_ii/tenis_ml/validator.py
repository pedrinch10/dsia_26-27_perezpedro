"""Validator: reglas de dominio para quedarnos con partidos utilizables (SRP)."""

import logging

import pandas as pd

from .config import VALID_BEST_OF, VALID_SURFACES

logger = logging.getLogger(__name__)

NUMERIC_COLUMNS = [
    "best_of",
    "winner_rank",
    "loser_rank",
    "winner_rank_points",
    "loser_rank_points",
    "winner_age",
    "loser_age",
    "winner_ht",
    "loser_ht",
]


class MatchValidator:
    """Separa partidos válidos de inválidos.

    Un partido es válido si tiene superficie reconocida, marcador, formato a 3 o 5
    sets, nombres de ambos jugadores y ranking y puntos ATP de los dos (son la base
    del modelo). Edad y altura pueden faltar: se imputan al entrenar.
    """

    def split(self, frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        work = frame.copy()
        for column in NUMERIC_COLUMNS:
            work[column] = pd.to_numeric(work[column], errors="coerce")

        ok = (
            work["surface"].isin(VALID_SURFACES)
            & work["score"].notna()
            & (work["score"].astype(str).str.strip() != "")
            & work["best_of"].isin(VALID_BEST_OF)
            & work["winner_name"].notna()
            & work["loser_name"].notna()
            & (work["winner_rank"] > 0)
            & (work["loser_rank"] > 0)
            & work["winner_rank_points"].notna()
            & work["loser_rank_points"].notna()
        )

        clean = work.loc[ok].reset_index(drop=True)
        errors = work.loc[~ok].copy()
        logger.info("Validación: %d válidos, %d inválidos", len(clean), len(errors))
        return clean, errors
