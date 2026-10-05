"""Tests de TennisValidator (Proyecto I - Parte B)."""

import pandas as pd
import pytest

from internet_app.validator import TennisMatchRecord, TennisValidator


@pytest.fixture
def partidos_mini() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "tourney_name": ["Open A", "Open B", "Open C"],
            "surface": ["Hard", "Clay", "Hielo"],  # "Hielo" no es una superficie válida
            "winner_name": ["Jugador A", "Jugador C", "Jugador E"],
            "loser_name": ["Jugador B", "Jugador D", "Jugador F"],
            "score": ["6-4 6-3", None, "6-0 6-0"],  # score ausente en la fila 2
            "best_of": [3, 3, 3],
            "round": ["F", "SF", "QF"],
            "minutes": [90, 80, 70],
            "winner_rank": [1, 5, 10],
            "loser_rank": [2, 6, 11],
        }
    )


@pytest.fixture
def validator() -> TennisValidator:
    return TennisValidator()


def test_split_cuenta_validos_e_invalidos(validator, partidos_mini):
    # Arrange: 1 fila válida (Open A), 2 inválidas (score nulo, superficie inválida)
    # Act
    validos, errores = validator.split(partidos_mini)
    # Assert
    assert len(validos) == 1
    assert len(errores) == 2


def test_split_conserva_los_datos_del_partido_valido(validator, partidos_mini):
    validos, _ = validator.split(partidos_mini)
    assert validos[0].winner_name == "Jugador A"
    assert validos[0].surface == "Hard"
    assert validos[0].minutes == 90.0


def test_split_no_muta_el_dataframe_original(validator, partidos_mini):
    original = partidos_mini.copy()
    validator.split(partidos_mini)
    pd.testing.assert_frame_equal(partidos_mini, original)


def test_tennis_match_record_es_inmutable(validator, partidos_mini):
    validos, _ = validator.split(partidos_mini)
    record = validos[0]
    with pytest.raises(AttributeError):
        record.winner_name = "Otro jugador"  # frozen=True debe impedir la mutación


@pytest.mark.parametrize("surface", ["Tierra batida", "indoor", "", None])
def test_superficie_no_reconocida_no_es_valida(validator, surface):
    df = pd.DataFrame(
        {
            "tourney_name": ["Open X"],
            "surface": [surface],
            "winner_name": ["Jugador A"],
            "loser_name": ["Jugador B"],
            "score": ["6-4 6-3"],
            "best_of": [3],
            "round": ["F"],
            "minutes": [90],
            "winner_rank": [1],
            "loser_rank": [2],
        }
    )
    validos, errores = validator.split(df)
    assert len(validos) == 0
    assert len(errores) == 1


@pytest.mark.parametrize("minutes", [0, -10, None])
def test_duracion_no_positiva_o_nula_no_es_valida(validator, minutes):
    df = pd.DataFrame(
        {
            "tourney_name": ["Open X"],
            "surface": ["Hard"],
            "winner_name": ["Jugador A"],
            "loser_name": ["Jugador B"],
            "score": ["6-4 6-3"],
            "best_of": [3],
            "round": ["F"],
            "minutes": [minutes],
            "winner_rank": [1],
            "loser_rank": [2],
        }
    )
    validos, errores = validator.split(df)
    assert len(validos) == 0
    assert len(errores) == 1


def test_split_devuelve_tennis_match_record(validator, partidos_mini):
    validos, _ = validator.split(partidos_mini)
    assert isinstance(validos[0], TennisMatchRecord)


@pytest.mark.integration
def test_split_con_csv_real_checkpoint():
    """Checkpoint con el dataset real de tenis: 10689 válidos / 753 inválidos."""
    from pathlib import Path

    from internet_app.loader import CsvTennisRepository

    path = Path(__file__).resolve().parents[2] / "data" / "tenis_matches_2019_2023.csv"
    repo = CsvTennisRepository(path)
    frame = repo.load()

    validator = TennisValidator()
    validos, errores = validator.split(frame)

    assert len(validos) == 10689
    assert len(errores) == 753
