"""Tests de ventas_app.cli (Proyecto I - Parte A)."""

from pathlib import Path

import pandas as pd
import pytest

from ventas_app import cli


@pytest.fixture
def csv_mini(tmp_path: Path) -> Path:
    path = tmp_path / "ventas_mini.csv"
    path.write_text(
        "region,producto,unidades,precio_unitario\n"
        "Norte,A,2,10\n"
        "Sur,B,1,5\n"
        "Norte,A,0,10\n",  # fila inválida: 0 unidades
        encoding="utf-8",
    )
    return path


def test_run_exporta_solo_los_registros_validos(csv_mini: Path, tmp_path: Path):
    # Arrange
    output_path = tmp_path / "salida.csv"
    # Act
    cli.run(csv_mini, output_path)
    # Assert
    assert output_path.exists()
    exportado = pd.read_csv(output_path)
    assert len(exportado) == 2  # la fila con 0 unidades se descarta


def test_run_imprime_el_resumen_por_consola(csv_mini: Path, tmp_path: Path, capsys):
    output_path = tmp_path / "salida.csv"

    cli.run(csv_mini, output_path)

    salida = capsys.readouterr().out
    assert "Válidas: 2" in salida
    assert "Inválidas: 1" in salida
    assert "Importe por región" in salida


def test_main_con_argumentos_de_linea_de_comandos(csv_mini: Path, tmp_path: Path, monkeypatch):
    output_path = tmp_path / "salida_cli.csv"
    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "--input", str(csv_mini), "--output", str(output_path)],
    )

    cli.main()

    assert output_path.exists()


@pytest.mark.integration
def test_run_con_csv_real_del_curso(tmp_path: Path):
    """Integración end-to-end con el ventas.csv real (checkpoint: 140 válidas)."""
    input_path = Path(__file__).resolve().parents[2] / "data" / "ventas.csv"
    output_path = tmp_path / "ventas_validas.csv"

    cli.run(input_path, output_path)

    exportado = pd.read_csv(output_path)
    assert len(exportado) == 140
