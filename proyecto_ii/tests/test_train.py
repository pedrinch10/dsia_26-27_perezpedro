"""Tests de entrenamiento: split temporal, métricas y persistencia."""

import json

import pytest

from tenis_ml.features import build_features
from tenis_ml.train import (
    TrainingError,
    build_model,
    save_artifacts,
    temporal_split,
    train_and_evaluate,
)
from tenis_ml.validator import MatchValidator


@pytest.fixture
def features(raw_matches):
    clean, _ = MatchValidator().split(raw_matches)
    return build_features(clean)


def test_temporal_split_separa_por_temporada(features):
    train, test = temporal_split(features, test_season=2023)
    assert train["season"].max() < 2023
    assert set(test["season"]) == {2023}


def test_temporal_split_sin_datos_de_test_lanza_error(features):
    with pytest.raises(TrainingError):
        temporal_split(features, test_season=2030)


def test_train_and_evaluate_devuelve_metricas_validas(features):
    model, metrics = train_and_evaluate(features)

    assert hasattr(model, "predict_proba")
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    # Los datos sintéticos tienen señal clara (mejor ranking gana ~75 %).
    assert metrics["accuracy"] > 0.55
    assert metrics["train_rows"] > 0 and metrics["test_rows"] > 0


def test_build_model_incluye_preprocesado_y_clasificador():
    model = build_model()
    assert [name for name, _ in model.steps] == ["preprocess", "clf"]


def test_save_artifacts_escribe_modelo_e_informe(features, tmp_path):
    model, metrics = train_and_evaluate(features)
    model_path = tmp_path / "sub" / "modelo.joblib"
    report_path = tmp_path / "sub" / "metrics.json"

    save_artifacts(model, metrics, model_path, report_path)

    assert model_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8"))["accuracy"] == metrics["accuracy"]
