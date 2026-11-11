"""Tests del pipeline completo y de la CLI (siempre con el cliente mock)."""

import json

import pandas as pd
import pytest

from tenis_ml import cli
from tenis_ml.hf_client import HFRequestError, MockExplanationClient
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


class FailingClient:
    """Simula un fallo del borde HF (p. ej. 429 o modelo no disponible)."""

    def explain(self, context: dict) -> str:
        raise HFRequestError("servicio no disponible")


def test_run_predict_exporta_aunque_falle_la_explicacion(raw_matches_csv, trained, tmp_path, caplog):
    model_path, _, _ = trained
    output = tmp_path / "pred.csv"

    with caplog.at_level("WARNING"):
        result = run_predict(raw_matches_csv, model_path, output, FailingClient(), explain=2)

    assert output.exists()
    assert result["prob_player_1_wins"].between(0, 1).all()
    assert (result["explanation"] == "").all()
    assert "Sin explicación" in caplog.text


def test_cli_sin_modelo_termina_con_error_y_exit_1(raw_matches_csv, tmp_path, caplog):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["predict", "--input", str(raw_matches_csv), "--model", str(tmp_path / "no.joblib"),
                  "--output", str(tmp_path / "p.csv")])

    assert excinfo.value.code == 1
    assert "No existe el modelo" in caplog.text


def test_cli_cliente_hf_sin_token_termina_con_error_y_exit_1(raw_matches_csv, trained, tmp_path, monkeypatch):
    model_path, _, _ = trained
    monkeypatch.setenv("HF_TOKEN", "")  # vacío: ni el entorno ni un .env local aportan token

    with pytest.raises(SystemExit) as excinfo:
        cli.main(["predict", "--input", str(raw_matches_csv), "--model", str(model_path),
                  "--output", str(tmp_path / "p.csv"), "--client", "hf"])

    assert excinfo.value.code == 1


@pytest.mark.integration
def test_pipeline_con_csv_real_supera_un_umbral_minimo(tmp_path):
    """Entrena con las temporadas 2019-2022 y evalúa en 2023 con el CSV real."""
    from tenis_ml.config import DEFAULT_DATA_PATH

    metrics = run_train(DEFAULT_DATA_PATH, tmp_path / "m.joblib", tmp_path / "r.json")

    assert metrics["test_season"] == 2023
    assert metrics["test_rows"] > 2000
    assert metrics["accuracy"] > 0.58
