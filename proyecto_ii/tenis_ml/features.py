"""Features: pasa del formato ganador/perdedor al formato jugador_1/jugador_2.

Si dejáramos winner_* y loser_* tal cual, el ganador estaría siempre en el mismo
lado y el modelo "sabría" el resultado (fuga de información). Por eso se asigna
cada jugador a jugador_1 o jugador_2 al azar, con semilla fija, y la etiqueta
pasa a ser "gana el jugador_1".
"""

import numpy as np
import pandas as pd

from .config import RANDOM_SEED, TARGET_COLUMN


def build_features(clean: pd.DataFrame, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    swap = rng.random(len(clean)) < 0.5  # True: el jugador_1 es el perdedor

    def pick(winner_col: str, loser_col: str) -> tuple[pd.Series, pd.Series]:
        winner = clean[winner_col].reset_index(drop=True)
        loser = clean[loser_col].reset_index(drop=True)
        p1 = winner.where(~swap, loser)
        p2 = loser.where(~swap, winner)
        return p1, p2

    name_1, name_2 = pick("winner_name", "loser_name")
    rank_1, rank_2 = pick("winner_rank", "loser_rank")
    points_1, points_2 = pick("winner_rank_points", "loser_rank_points")
    age_1, age_2 = pick("winner_age", "loser_age")
    height_1, height_2 = pick("winner_ht", "loser_ht")

    features = pd.DataFrame(
        {
            "season": clean["tourney_id"].astype(str).str[:4].astype(int),
            "player_1": name_1,
            "player_2": name_2,
            "rank_diff": rank_1 - rank_2,
            "log_rank_ratio": np.log(rank_1 / rank_2),
            "points_diff": points_1 - points_2,
            "age_diff": age_1 - age_2,
            "height_diff": height_1 - height_2,
            "best_of": clean["best_of"].astype(int),
            "surface": clean["surface"],
            "round": clean["round"],
            TARGET_COLUMN: (~swap).astype(int),
        }
    )
    return features
