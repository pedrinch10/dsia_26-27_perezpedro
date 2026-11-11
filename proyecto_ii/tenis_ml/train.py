"""Entrenamiento del modelo sklearn: split temporal, métricas y persistencia."""

import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    RANDOM_SEED,
    TARGET_COLUMN,
    TEST_SEASON,
)

logger = logging.getLogger(__name__)


class TrainingError(Exception):
    """No se puede entrenar con los datos recibidos."""


def build_model() -> Pipeline:
    """Preprocesado + regresión logística en un único objeto persistible."""
    numeric = Pipeline(
        [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    preprocess = ColumnTransformer(
        [
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("preprocess", preprocess),
            ("clf", LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)),
        ]
    )


def temporal_split(
    features: pd.DataFrame, test_season: int = TEST_SEASON
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Entrena con temporadas anteriores y evalúa en test_season (sin fuga temporal)."""
    train = features[features["season"] < test_season]
    test = features[features["season"] == test_season]
    if train.empty or test.empty:
        raise TrainingError(
            f"Split temporal vacío: train={len(train)} filas, test={len(test)} filas "
            f"(test_season={test_season})"
        )
    return train, test


def train_and_evaluate(
    features: pd.DataFrame, test_season: int = TEST_SEASON
) -> tuple[Pipeline, dict]:
    train, test = temporal_split(features, test_season)
    model = build_model()
    model.fit(train[FEATURE_COLUMNS], train[TARGET_COLUMN])

    predictions = model.predict(test[FEATURE_COLUMNS])
    baseline = (test["rank_diff"] < 0).astype(int)  # "gana el mejor ranking"
    metrics = {
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "test_season": int(test_season),
        "accuracy": float(accuracy_score(test[TARGET_COLUMN], predictions)),
        "f1": float(f1_score(test[TARGET_COLUMN], predictions)),
        "baseline_accuracy_better_rank": float(
            accuracy_score(test[TARGET_COLUMN], baseline)
        ),
    }
    logger.info("Métricas: %s", metrics)
    return model, metrics


def save_artifacts(model: Pipeline, metrics: dict, model_path: Path, report_path: Path) -> None:
    model_path, report_path = Path(model_path), Path(report_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.info("Modelo guardado en %s e informe en %s", model_path, report_path)
