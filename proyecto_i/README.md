# Proyecto I — DSIA

Pipeline de datos en dos partes, siguiendo la arquitectura `loader -> validator -> metrics -> cli`
(principios SOLID: SRP en cada módulo, OCP en `metrics`, DIP en `cli` a través de los `Protocol`
`SalesRepository` / `TennisRepository`).

## Estructura

```
proyecto_i/
  ventas_app/        # Parte A: ventas del curso
  internet_app/       # Parte B: partidos de tenis (ATP)
  tests/
    ventas/          # tests de ventas_app
    internet/        # tests de internet_app
  data/              # CSV de entrada usados por los tests de integración
  requirements.txt
  conftest.py        # hace importables ventas_app / internet_app desde los tests
  pytest.ini
```

El workflow de CI está en la raíz real del repositorio: `.github/workflows/ci.yml`
(tiene que estar ahí para que GitHub Actions lo detecte).

## Parte A — `ventas_app`

Reutiliza y completa el pipeline de ventas construido en las Sesiones 3 y 4:

- `loader.py`: `CsvSalesRepository`, lee el CSV de ventas.
- `validator.py`: `SalesValidator.split()` separa filas válidas (`SalesRecord`, `frozen=True`)
  de inválidas (unidades/precio no positivos o nulos).
- `metrics.py`: `SalesMetrics` — importe total por región, top N productos.
- `cli.py`: orquesta loader → validator → metrics y exporta las filas válidas a CSV.

Checkpoint de integración con `data/ventas.csv`: **140 válidas / 10 inválidas**.

## Parte B — `internet_app` (dataset de tenis)

### Origen de los datos

- **Contenido**: partidos individuales masculinos del circuito ATP, temporadas **2019, 2021,
  2022 y 2023** (formato estándar de Jeff Sackmann: jugadores, ranking, superficie, marcador,
  estadísticas de saque, duración, etc.).
- **Fuente**: mirror en GitHub (`farhadGithub/tennis-atp-data`) de los datos originales de
  Jeff Sackmann (`github.com/JeffSackmann`), re-publicados porque el repositorio original dejó
  de estar disponible.
- **Licencia**: CC BY-NC-SA 4.0 (atribución, uso no comercial, compartir igual). Uso aquí:
  exclusivamente académico, para la asignatura DSIA.
- **Fecha de descarga**: 5 de octubre de 2026.
- **Fichero**: `data/tenis_matches_2019_2023.csv` — **11.442 filas** (partidos), 49 columnas.

### Módulos

- `loader.py`: `CsvTennisRepository`, lee el CSV de partidos.
- `validator.py`: `TennisValidator.split()` separa partidos válidos (`TennisMatchRecord`,
  `frozen=True`) de inválidos. Reglas de dominio:
  - superficie reconocida (`Hard`, `Clay`, `Grass`, `Carpet`);
  - marcador (`score`) registrado;
  - duración (`minutes`) numérica y positiva;
  - formato (`best_of`) a 3 o 5 sets;
  - nombre de ganador y perdedor presentes.
- `metrics.py`: `TennisMetrics` con 4 métricas:
  - `matches_by_surface`: partidos por superficie;
  - `top_players_by_wins`: jugadores con más victorias;
  - `avg_match_duration`: duración media del partido (min);
  - `matches_by_round`: partidos por ronda del torneo.
- `cli.py`: orquesta loader → validator → metrics y exporta los partidos válidos a CSV.

Checkpoint de integración con `data/tenis_matches_2019_2023.csv`: **10.689 válidos / 753
inválidos** (los inválidos son casi todos partidos sin duración registrada: walkovers,
retirados o Davis Cup).

## Cómo ejecutar

Desde la raíz del repositorio (usa el entorno `uv` ya configurado):

```bash
uv sync
cd proyecto_i
uv run python -m ventas_app.cli --input data/ventas.csv --output /tmp/ventas_validas.csv
uv run python -m internet_app.cli --input data/tenis_matches_2019_2023.csv --output /tmp/partidos_validos.csv
```

## Cómo ejecutar los tests

```bash
cd proyecto_i
uv run pytest --cov=ventas_app --cov=internet_app --cov-report=term-missing --cov-fail-under=60
```

- Tests marcados con `@pytest.mark.integration` usan los CSV reales de `data/`.
- Se cubren los 4 módulos (`loader`, `validator`, `metrics`, `cli`) en ambas partes, con
  patrón AAA, `pytest.raises`, `@pytest.mark.parametrize` y `@pytest.fixture`.

## CI

`.github/workflows/ci.yml` corre en cada push a `main` y en cada pull request: instala
`proyecto_i/requirements.txt` con Python 3.12 y ejecuta la suite de tests con cobertura
mínima del 60%.
