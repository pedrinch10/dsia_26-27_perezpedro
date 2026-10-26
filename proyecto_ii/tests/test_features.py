"""Tests de build_features: orientación aleatoria sin fuga de información."""

import numpy as np
import pytest

from tenis_ml.config import FEATURE_COLUMNS, TARGET_COLUMN
from tenis_ml.features import build_features
from tenis_ml.validator import MatchValidator


@pytest.fixture
def clean(raw_matches):
    clean, _ = MatchValidator().split(raw_matches)
    return clean


def test_build_features_incluye_todas_las_columnas_del_modelo(clean):
    features = build_features(clean)
    assert set(FEATURE_COLUMNS + [TARGET_COLUMN, "season"]).issubset(features.columns)
    assert len(features) == len(clean)


def test_build_features_es_determinista_con_la_misma_semilla(clean):
    first = build_features(clean, seed=1)
    second = build_features(clean, seed=1)
    assert first.equals(second)


def test_etiqueta_equilibrada_no_filtra_el_ganador(clean):
    features = build_features(clean)
    # Si no hubiera orientación aleatoria la media sería 1.0 (el ganador siempre primero).
    assert 0.35 < features[TARGET_COLUMN].mean() < 0.65


def test_etiqueta_coincide_con_que_jugador_1_sea_el_ganador(clean):
    features = build_features(clean)
    player_1_is_winner = (features["player_1"] == clean["winner_name"]).astype(int)
    assert (player_1_is_winner == features[TARGET_COLUMN]).all()


def test_diferencia_de_ranking_cambia_de_signo_con_la_orientacion(clean):
    features = build_features(clean)
    expected = np.where(
        features[TARGET_COLUMN] == 1,
        clean["winner_rank"] - clean["loser_rank"],
        clean["loser_rank"] - clean["winner_rank"],
    )
    assert (features["rank_diff"].to_numpy() == expected).all()


def test_season_sale_del_tourney_id(clean):
    features = build_features(clean)
    assert set(features["season"]) == {2021, 2022, 2023}
