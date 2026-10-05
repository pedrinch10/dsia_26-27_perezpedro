"""Hace que ventas_app e internet_app sean importables desde los tests de proyecto_i."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
