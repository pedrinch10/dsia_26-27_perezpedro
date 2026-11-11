"""Constantes compartidas por todo el pipeline (un único sitio donde cambiarlas)."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "tenis_matches_2019_2023.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "tenis_model.joblib"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "metrics.json"

RANDOM_SEED = 42
TEST_SEASON = 2023  # se entrena con temporadas anteriores y se evalúa en esta

VALID_SURFACES = {"Hard", "Clay", "Grass", "Carpet"}
VALID_BEST_OF = {3, 5}

NUMERIC_FEATURES = [
    "rank_diff",
    "log_rank_ratio",
    "points_diff",
    "age_diff",
    "height_diff",
    "best_of",
]
CATEGORICAL_FEATURES = ["surface", "round"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "player_1_wins"
