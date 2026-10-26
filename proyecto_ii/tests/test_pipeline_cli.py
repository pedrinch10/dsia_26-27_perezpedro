"""Tests del pipeline completo y de la CLI (siempre con el cliente mock)."""

import json

import pandas as pd
import pytest

from tenis_ml import cli
from tenis_ml.hf_client import MockExplanationClient
from tenis_ml.pipeline import run_predict, run_train
from tenis_ml.predict import ModelNotFoundError


@pytest.fixture
def trained(raw_matches_csv, tmp_path):
    model_path = tmp_path / "modelo.joblib"
    report_path = tmp_path / "metrics.json"
    metrics = run_train(raw_matches_csv, model_path, report_path)
    return model_path, report_path, metrics


def test_run_train_guarda_modelo_e_informe(trained):
    model_path, report_path, metrics = trained
    assert model_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8"))["test_season"] == metrics["test_season"]


def test_run_predict_exporta_probabilidades_y_explicaciones(raw_matches_csv, trained, tmp_path):
    model_path, _, _ = trained
    output = tmp_path / "pred.csv"

    result = run_predict(raw_matches_csv, model_path, output, MockExplanationClient(), explain=3)

    exported = pd.read_csv(output).fillna("")
    assert len(exported) == len(result)
    assert exported["prob_player_1_wins"].between(0, 1).all()
    assert (exported["explanation"].head(3) != "").all()
    assert (exported["explanation"].iloc[3:] == "").all()


def test_run_predict_filtra_por_temporada(raw_matches_csv, trained, tmp_path):
    model_path, _, _ = trained
    result = run_predict(
        raw_matches_csv, model_path, tmp_path / "p.csv", MockExplanationClient(), season=2023
    )
    assert set(result["season"]) == {2023}


def test_run_predict_sin_modelo_lanza_error(raw_matches_csv, tmp_path):
    with pytest.raises(ModelNotFoundError):
        run_predict(raw_matches_csv, tmp_path / "no.joblib", tmp_path / "p.csv", MockExplanationClient())


def test_cli_train_y_predict_de_extremo_a_extremo(raw_matches_csv, tmp_path, capsys):
    model_path = tmp_path / "m.joblib"
    output = tmp_path / "salida.csv"

    cli.main(["train", "--input", str(raw_matches_csv), "--model", str(model_path),
              "--report", str(tmp_path / "r.json")])
    cli.main(["predict", "--input", str(raw_matches_csv), "--model", str(model_path),
              "--output", str(output), "--client", "mock", "--explain", "2"])

    assert "Accuracy" in capsys.readouterr().out
    assert output.exists()


@pytest.mark.integration
def test_pipeline_con_csv_real_supera_un_umbral_minimo(tmp_path):
    """Entrena con las temporadas 2019-2022 y evalúa en 2023 con el CSV real."""
    from tenis_ml.config import DEFAULT_DATA_PATH

    metrics = run_train(DEFAULT_DATA_PATH, tmp_path / "m.joblib", tmp_path / "r.json")

    assert metrics["test_season"] == 2023
    assert metrics["test_rows"] > 2000
    assert metrics["accuracy"] > 0.58
