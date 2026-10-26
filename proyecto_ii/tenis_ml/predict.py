"""Inferencia: carga del modelo persistido y probabilidades."""

from pathlib import Path

import joblib
import pandas as pd

from .config import FEATURE_COLUMNS


class ModelNotFoundError(Exception):
    """El fichero del modelo no existe (¿falta ejecutar el entrenamiento?)."""


def load_model(model_path: Path):
    model_path = Path(model_path)
    if not model_path.exists():
        raise ModelNotFoundError(
            f"No existe el modelo: {model_path}. Entrena primero con 'train'."
        )
    return joblib.load(model_path)


def predict_proba(model, features: pd.DataFrame) -> pd.Series:
    """Probabilidad de que gane el jugador_1 para cada fila."""
    proba = model.predict_proba(features[FEATURE_COLUMNS])[:, 1]
    return pd.Series(proba, index=features.index, name="prob_player_1_wins")
