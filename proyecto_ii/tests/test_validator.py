"""Tests de MatchValidator."""

import pandas as pd
import pytest

from tenis_ml.validator import MatchValidator


@pytest.fixture
def validator() -> MatchValidator:
    return MatchValidator()


def test_split_conserva_todos_los_partidos_validos(validator, raw_matches):
    clean, errors = validator.split(raw_matches)
    assert len(clean) == len(raw_matches)
    assert errors.empty


def test_split_no_muta_el_dataframe_original(validator, raw_matches):
    original = raw_matches.copy()
    validator.split(raw_matches)
    pd.testing.assert_frame_equal(raw_matches, original)


@pytest.mark.parametrize(
    "column, bad_value",
    [
        ("surface", "Hielo"),
        ("surface", None),
        ("best_of", 7),
        ("score", None),
        ("score", "  "),
        ("winner_rank", None),
        ("loser_rank", 0),
        ("winner_rank_points", None),
        ("winner_name", None),
    ],
)
def test_fila_con_dato_invalido_va_a_errores(validator, raw_matches, column, bad_value):
    broken = raw_matches.copy()
    broken[column] = broken[column].astype(object)
    broken.loc[0, column] = bad_value

    clean, errors = validator.split(broken)

    assert len(errors) == 1
    assert len(clean) == len(raw_matches) - 1


def test_edad_o_altura_ausentes_no_invalidan_el_partido(validator, raw_matches):
    matches = raw_matches.astype({"winner_age": float, "loser_ht": float})
    matches.loc[0, ["winner_age", "loser_ht"]] = None
    clean, errors = validator.split(matches)
    assert errors.empty
    assert len(clean) == len(matches)
