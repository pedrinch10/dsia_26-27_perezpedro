"""Tests de CsvTennisRepository (Proyecto I - Parte B)."""

from pathlib import Path

import pytest

from internet_app.loader import CsvTennisRepository, DataLoadError


def test_load_path_inexistente_raises_dataloadererror():
    repo = CsvTennisRepository(Path("no_existe.csv"))
    with pytest.raises(DataLoadError):
        repo.load()


def test_load_csv_ok(tmp_path):
    csv_path = tmp_path / "mini.csv"
    csv_path.write_text(
        "surface,score,minutes,best_of,winner_name,loser_name,round,winner_rank,loser_rank,tourney_name\n"
        "Hard,6-4 6-3,90,3,Jugador A,Jugador B,F,1,2,Mini Open\n",
        encoding="utf-8",
    )

    repo = CsvTennisRepository(csv_path)
    frame = repo.load()

    assert len(frame) == 1
    assert frame.iloc[0]["surface"] == "Hard"
