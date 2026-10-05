"""Tests de internet_app.cli (Proyecto I - Parte B)."""

from pathlib import Path

import pandas as pd
import pytest

from internet_app import cli


@pytest.fixture
def csv_mini(tmp_path: Path) -> Path:
    path = tmp_path / "partidos_mini.csv"
    path.write_text(
        "tourney_name,surface,winner_name,loser_name,score,best_of,round,minutes,winner_rank,loser_rank\n"
        "Open A,Hard,Jugador A,Jugador B,6-4 6-3,3,F,90,1,2\n"
        "Open B,Clay,Jugador C,Jugador D,7-5 6-3,3,QF,100,5,8\n"
        "Open C,Hielo,Jugador E,Jugador F,6-0 6-0,3,R16,60,20,30\n",  # fila inválida: superficie
        encoding="utf-8",
    )
    return path


def test_run_exporta_solo_los_partidos_validos(csv_mini: Path, tmp_path: Path):
    output_path = tmp_path / "salida.csv"

    cli.run(csv_mini, output_path)

    assert output_path.exists()
    exportado = pd.read_csv(output_path)
    assert len(exportado) == 2  # la fila con superficie "Hielo" se descarta


def test_run_imprime_el_resumen_por_consola(csv_mini: Path, tmp_path: Path, capsys):
    output_path = tmp_path / "salida.csv"

    cli.run(csv_mini, output_path)

    salida = capsys.readouterr().out
    assert "Válidos: 2" in salida
    assert "Inválidos: 1" in salida
    assert "Partidos por superficie" in salida


def test_main_con_argumentos_de_linea_de_comandos(csv_mini: Path, tmp_path: Path, monkeypatch):
    output_path = tmp_path / "salida_cli.csv"
    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "--input", str(csv_mini), "--output", str(output_path)],
    )

    cli.main()

    assert output_path.exists()


@pytest.mark.integration
def test_run_con_dataset_real_de_tenis(tmp_path: Path):
    """Integración end-to-end con el dataset real (checkpoint: 10689 válidos)."""
    input_path = Path(__file__).resolve().parents[2] / "data" / "tenis_matches_2019_2023.csv"
    output_path = tmp_path / "partidos_validos.csv"

    cli.run(input_path, output_path)

    exportado = pd.read_csv(output_path)
    assert len(exportado) == 10689
