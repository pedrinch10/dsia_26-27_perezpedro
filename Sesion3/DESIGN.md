# DESIGN.md — Sesión 3

## Principios SOLID aplicados

**S — Single Responsibility**
`validator.py` solo decide qué es válido; no lee ficheros ni exporta. `loader.py` solo sabe leer; `metrics.py` solo agrega.

**O — Open/Closed**
Para añadir una métrica nueva (ej. ticket medio) solo toco `metrics.py`, añadiendo un método. No necesito tocar `validator.py` ni `loader.py`.

**D — Dependency Inversion**
`cli.py` declara `repo: SalesRepository = CsvSalesRepository(...)`. El tipo es la interfaz (`SalesRepository`), no el detalle concreto. Si mañana hay un `JsonSalesRepository`, `cli.py` no cambia.