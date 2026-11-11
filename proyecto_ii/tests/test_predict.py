"""Tests de carga e inferencia del modelo sklearn."""

import pytest

from tenis_ml.features import build_features
from tenis_ml.predict import ModelNotFoundError, load_model, predict_proba
from tenis_ml.train import save_artifacts, train_and_evaluate
from tenis_ml.validator import MatchValidator


@pytest.fixture
def features(raw_matches):
    clean, _ = MatchValidator().split(raw_matches)
    return build_features(clean)


@pytest.fixture
def saved_model_path(features, tmp_path):
    model, metrics = train_and_evaluate(features)
    path = tmp_path / "modelo.joblib"
    save_artifacts(model, metrics, path, tmp_path / "metrics.json")
    return path


def test_load_model_inexistente_lanza_error(tmp_path):
    with pytest.raises(ModelNotFoundError):
        load_model(tmp_path / "no_existe.joblib")


def test_modelo_guardado_se_carga_y_predice(saved_model_path, features):
    model = load_model(saved_model_path)
    proba = predict_proba(model, features)
    assert len(proba) == len(features)
    assert proba.between(0.0, 1.0).all()


def test_predict_proba_favorece_al_mejor_clasificado(saved_model_path, features):
    model = load_model(saved_model_path)
    proba = predict_proba(model, features)
    favorite_wins_pred = (proba >= 0.5).astype(int)
    agreement = (favorite_wins_pred == (features["rank_diff"] < 0).astype(int)).mean()
    assert agreement > 0.7
