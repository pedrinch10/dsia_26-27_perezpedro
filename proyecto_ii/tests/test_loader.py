"""Tests de CsvMatchRepository."""

from pathlib import Path

import pytest

from tenis_ml.loader import CsvMatchRepository, DataLoadError


def test_load_path_inexistente_raises_dataloaderror():
    repo = CsvMatchRepository(Path("no_existe.csv"))
    with pytest.raises(DataLoadError):
        repo.load()


def test_load_csv_ok(raw_matches_csv, raw_matches):
    frame = CsvMatchRepository(raw_matches_csv).load()
    assert len(frame) == len(raw_matches)
    assert "winner_rank" in frame.columns
