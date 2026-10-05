"""Tests de TennisMetrics (Proyecto I - Parte B)."""

import pytest

from internet_app.metrics import TennisMetrics
from internet_app.validator import TennisMatchRecord


@pytest.fixture
def records() -> list[TennisMatchRecord]:
    return [
        TennisMatchRecord("Open A", "Hard", "A", "B", "6-4 6-3", 3, "F", 90, 1, 2),
        TennisMatchRecord("Open A", "Hard", "A", "C", "6-4 6-3", 3, "SF", 80, 1, 5),
        TennisMatchRecord("Open B", "Clay", "C", "A", "7-5 6-3", 3, "QF", 100, 5, 1),
    ]


@pytest.fixture
def metrics() -> TennisMetrics:
    return TennisMetrics()


def test_matches_by_surface_agrupa_y_cuenta(metrics, records):
    por_superficie = metrics.matches_by_surface(records)
    assert por_superficie["Hard"] == 2
    assert por_superficie["Clay"] == 1


def test_matches_by_surface_ordena_de_mayor_a_menor(metrics, records):
    por_superficie = metrics.matches_by_surface(records)
    assert list(por_superficie.keys())[0] == "Hard"  # 2 > 1


def test_top_players_by_wins_cuenta_victorias(metrics, records):
    top = metrics.top_players_by_wins(records)
    assert top["A"] == 2
    assert top["C"] == 1


@pytest.mark.parametrize("n, esperado", [(1, 1), (2, 2)])
def test_top_players_by_wins_respeta_el_limite_n(metrics, records, n, esperado):
    top = metrics.top_players_by_wins(records, n=n)
    assert len(top) == esperado


def test_avg_match_duration_calcula_la_media(metrics, records):
    media = metrics.avg_match_duration(records)
    assert media == pytest.approx((90 + 80 + 100) / 3)


def test_avg_match_duration_con_lista_vacia_no_falla(metrics):
    assert metrics.avg_match_duration([]) == 0.0


def test_matches_by_round_agrupa_correctamente(metrics, records):
    por_ronda = metrics.matches_by_round(records)
    assert por_ronda["F"] == 1
    assert por_ronda["SF"] == 1
    assert por_ronda["QF"] == 1
