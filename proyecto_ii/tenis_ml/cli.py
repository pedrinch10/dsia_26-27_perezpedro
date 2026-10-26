"""CLI: `train` entrena y guarda el modelo; `predict` infiere y explica."""

import argparse
import logging
from pathlib import Path

from .config import DEFAULT_DATA_PATH, DEFAULT_MODEL_PATH, DEFAULT_REPORT_PATH
from .hf_client import get_client
from .pipeline import run_predict, run_train


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Predicción de partidos ATP (sklearn + Hugging Face)")
    sub = parser.add_subparsers(dest="command", required=True)

    train = sub.add_parser("train", help="entrena el modelo sklearn")
    train.add_argument("--input", type=Path, default=DEFAULT_DATA_PATH)
    train.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    train.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)

    predict = sub.add_parser("predict", help="predice y explica con el cliente HF")
    predict.add_argument("--input", type=Path, default=DEFAULT_DATA_PATH)
    predict.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    predict.add_argument("--output", type=Path, required=True)
    predict.add_argument("--client", choices=["mock", "hf"], default="mock")
    predict.add_argument("--season", type=int, default=None)
    predict.add_argument("--explain", type=int, default=0, help="nº de partidos a explicar")
    return parser


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)

    if args.command == "train":
        metrics = run_train(args.input, args.model, args.report)
        print(f"Accuracy: {metrics['accuracy']:.3f} | F1: {metrics['f1']:.3f} | "
              f"Baseline (mejor ranking): {metrics['baseline_accuracy_better_rank']:.3f}")
    else:
        client = get_client(args.client)
        run_predict(args.input, args.model, args.output, client, args.season, args.explain)


if __name__ == "__main__":
    main()
