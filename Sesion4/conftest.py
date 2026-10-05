"""Hace que ventas_app (definido en Sesion3) sea importable desde los tests de esta sesión."""

import sys
from pathlib import Path

SESION3_DIR = Path(__file__).resolve().parents[1] / "Sesion3"
sys.path.insert(0, str(SESION3_DIR))
