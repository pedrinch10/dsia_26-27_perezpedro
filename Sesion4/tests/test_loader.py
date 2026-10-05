"""Tests de CsvSalesRepository (E3 - pytest)."""

from pathlib import Path

import pytest

from ventas_app.loader import CsvSalesRepository, DataLoadError


def test_load_path_inexistente_raises_dataloadererror():
    repo = CsvSalesRepository(Path("no_existe.csv"))
    with pytest.raises(DataLoadError):
        repo.load()


def test_load_csv_ok(tmp_path):
    csv_path = tmp_path / "mini.csv"
    csv_path.write_text("region,producto,unidades,precio_unitario\nNorte,A,1,10\n", encoding="utf-8")

    repo = CsvSalesRepository(csv_path)
    frame = repo.load()

    assert len(frame) == 1
    assert frame.iloc[0]["region"] == "Norte"
