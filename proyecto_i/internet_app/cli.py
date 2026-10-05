"""CLI: Facade que orquesta loader -> validator -> metrics (DIP)."""

import argparse
from pathlib import Path

import pandas as pd

from .loader import CsvTennisRepository, TennisRepository
from .metrics import TennisMetrics
from .validator import TennisValidator


def run(input_path: Path, output_path: Path) -> None:
    repo: TennisRepository = CsvTennisRepository(input_path)  # DIP: depende del Protocol
    validator = TennisValidator()
    metrics = TennisMetrics()

    frame = repo.load()
    records, errors = validator.split(frame)
    print(f"Válidos: {len(records)} | Inválidos: {len(errors)}")

    print("\nPartidos por superficie:")
    for surface, count in metrics.matches_by_surface(records).items():
        print(f"  {surface}: {count}")

    print("\nTop 10 jugadores por victorias:")
    for player, wins in metrics.top_players_by_wins(records).items():
        print(f"  {player}: {wins}")

    print(f"\nDuración media del partido: {metrics.avg_match_duration(records):.1f} min")

    print("\nPartidos por ronda:")
    for round_name, count in metrics.matches_by_round(records).items():
        print(f"  {round_name}: {count}")

    pd.DataFrame([r.__dict__ for r in records]).to_csv(output_path, index=False)
    print(f"\nExportado: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Procesa partidos de tenis validados")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()
