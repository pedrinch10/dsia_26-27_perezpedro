"""Orquestación (Facade): loader -> validator -> features -> modelo -> cliente HF."""

import logging
from pathlib import Path

import pandas as pd

from .features import build_features
from .hf_client import ExplanationClient, HFRequestError
from .loader import CsvMatchRepository, MatchRepository
from .predict import load_model, predict_proba
from .train import save_artifacts, train_and_evaluate
from .validator import MatchValidator

logger = logging.getLogger(__name__)


def prepare_features(input_path: Path) -> pd.DataFrame:
    repo: MatchRepository = CsvMatchRepository(input_path)  # DIP: depende del Protocol
    frame = repo.load()
    clean, errors = MatchValidator().split(frame)
    logger.info("Partidos cargados: %d (válidos %d, descartados %d)", len(frame), len(clean), len(errors))
    return build_features(clean)


def run_train(input_path: Path, model_path: Path, report_path: Path) -> dict:
    features = prepare_features(input_path)
    model, metrics = train_and_evaluate(features)
    save_artifacts(model, metrics, model_path, report_path)
    return metrics


def run_predict(
    input_path: Path,
    model_path: Path,
    output_path: Path,
    client: ExplanationClient,
    season: int | None = None,
    explain: int = 0,
) -> pd.DataFrame:
    features = prepare_features(input_path)
    if season is not None:
        features = features[features["season"] == season].reset_index(drop=True)

    model = load_model(model_path)
    result = features[["season", "player_1", "player_2", "surface", "round"]].copy()
    result["prob_player_1_wins"] = predict_proba(model, features)
    result["explanation"] = ""

    for index in result.head(explain).index:
        context = {**features.loc[index].to_dict(), "prob_player_1_wins": result.at[index, "prob_player_1_wins"]}
        try:
            result.at[index, "explanation"] = client.explain(context)
            logger.info("Explicación generada para la fila %d", index)
        except HFRequestError as error:
            # Degradación controlada: la predicción sklearn se exporta aunque falle el borde HF.
            logger.warning("Sin explicación para la fila %d: %s", index, error)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    logger.info("Predicciones exportadas a %s (%d filas)", output_path, len(result))
    return result
