"""Validator: reglas de dominio de calidad de datos de tenis (SRP)."""

from dataclasses import dataclass

import pandas as pd

VALID_SURFACES = {"Hard", "Clay", "Grass", "Carpet"}
VALID_BEST_OF = {3, 5}
MIN_MINUTES = 0


@dataclass(frozen=True)
class TennisMatchRecord:
    tourney_name: str
    surface: str
    winner_name: str
    loser_name: str
    score: str
    best_of: int
    round: str
    minutes: float
    winner_rank: float
    loser_rank: float


class TennisValidator:
    """Separa partidos válidos de inválidos según reglas de dominio del tenis.

    Un partido se considera válido cuando:
    - la superficie es una de las reconocidas por el circuito ATP,
    - tiene marcador (score) registrado,
    - la duración en minutos es un número positivo,
    - el formato (best_of) es 3 o 5 sets,
    - tiene nombre de ganador y de perdedor.
    """

    def split(self, frame: pd.DataFrame) -> tuple[list[TennisMatchRecord], pd.DataFrame]:
        work = frame.copy()
        work["minutes"] = pd.to_numeric(work["minutes"], errors="coerce")
        work["best_of"] = pd.to_numeric(work["best_of"], errors="coerce")
        work["winner_rank"] = pd.to_numeric(work["winner_rank"], errors="coerce")
        work["loser_rank"] = pd.to_numeric(work["loser_rank"], errors="coerce")

        surface_ok = work["surface"].isin(VALID_SURFACES)
        score_ok = work["score"].notna() & (work["score"].astype(str).str.strip() != "")
        minutes_ok = work["minutes"].notna() & (work["minutes"] > MIN_MINUTES)
        best_of_ok = work["best_of"].isin(VALID_BEST_OF)
        names_ok = work["winner_name"].notna() & work["loser_name"].notna()

        ok = surface_ok & score_ok & minutes_ok & best_of_ok & names_ok

        validos = [
            TennisMatchRecord(
                tourney_name=str(row.tourney_name),
                surface=str(row.surface),
                winner_name=str(row.winner_name),
                loser_name=str(row.loser_name),
                score=str(row.score),
                best_of=int(row.best_of),
                round=str(row.round),
                minutes=float(row.minutes),
                winner_rank=float(row.winner_rank) if pd.notna(row.winner_rank) else float("nan"),
                loser_rank=float(row.loser_rank) if pd.notna(row.loser_rank) else float("nan"),
            )
            for row in work.loc[ok].itertuples(index=False)
        ]
        errores = work.loc[~ok].copy()
        return validos, errores
