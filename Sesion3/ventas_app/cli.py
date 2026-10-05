"""CLI: Facade que orquesta loader -> validator -> metrics (DIP)."""

import argparse
from pathlib import Path

from .loader import CsvSalesRepository, SalesRepository
from .metrics import SalesMetrics
from .validator import SalesValidator


def run(input_path: Path, output_path: Path) -> None:
    repo: SalesRepository = CsvSalesRepository(input_path)  # DIP: depende del Protocol
    validator = SalesValidator()
    metrics = SalesMetrics()

    frame = repo.load()
    records, errors = validator.split(frame)
    print(f"Válidas: {len(records)} | Inválidas: {len(errors)}")

    print("\nImporte por región:")
    for region, total in metrics.total_by_region(records).items():
        print(f"  {region}: {total:.2f}")

    print("\nTop 3 productos:")
    for product, total in metrics.top_products(records).items():
        print(f"  {product}: {total:.2f}")

    import pandas as pd
    pd.DataFrame([r.__dict__ for r in records]).to_csv(output_path, index=False)
    print(f"\nExportado: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Procesa ventas validadas")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()