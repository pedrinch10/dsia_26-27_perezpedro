"""Fixtures compartidas: datos sintéticos con el mismo formato que el CSV real."""

import numpy as np
import pandas as pd
import pytest

SURFACES = ["Hard", "Clay", "Grass"]
ROUNDS = ["R32", "R16", "QF", "SF", "F"]


def make_raw_matches(n_per_season: int = 120, seed: int = 0) -> pd.DataFrame:
    """Partidos sintéticos: el mejor ranking gana ~75 % de las veces."""
    rng = np.random.default_rng(seed)
    rows = []
    for season in (2021, 2022, 2023):
        for i in range(n_per_season):
            rank_a, rank_b = rng.integers(1, 200, size=2)
            if rank_a == rank_b:
                rank_b += 1
            better, worse = (rank_a, rank_b) if rank_a < rank_b else (rank_b, rank_a)
            better_wins = rng.random() < 0.75
            w_rank, l_rank = (better, worse) if better_wins else (worse, better)
            rows.append(
                {
                    "tourney_id": f"{season}-M{i:03d}",
                    "surface": SURFACES[i % len(SURFACES)],
                    "best_of": 3 if i % 5 else 5,
                    "round": ROUNDS[i % len(ROUNDS)],
                    "score": "6-4 6-3",
                    "winner_name": f"Jugador {w_rank}",
                    "loser_name": f"Jugador {l_rank}",
                    "winner_rank": int(w_rank),
                    "loser_rank": int(l_rank),
                    "winner_rank_points": 10000 // int(w_rank),
                    "loser_rank_points": 10000 // int(l_rank),
                    "winner_age": 20 + int(rng.integers(0, 15)),
                    "loser_age": 20 + int(rng.integers(0, 15)),
                    "winner_ht": 175 + int(rng.integers(0, 25)),
                    "loser_ht": 175 + int(rng.integers(0, 25)),
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture
def raw_matches() -> pd.DataFrame:
    return make_raw_matches()


@pytest.fixture
def raw_matches_csv(tmp_path, raw_matches):
    path = tmp_path / "partidos.csv"
    raw_matches.to_csv(path, index=False)
    return path
