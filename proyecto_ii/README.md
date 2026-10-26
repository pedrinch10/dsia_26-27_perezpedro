# Proyecto II — Predicción de partidos ATP (sklearn + Hugging Face)

Base del Trabajo Final (Proyecto III). Pipeline reproducible que:

```text
CSV ATP → validación → features → modelo sklearn → probabilidad → explicación (Hugging Face)
```

## Dominio y datos

- **Dominio:** tenis profesional masculino (ATP).
- **Motivación:** el dataset es real, público y tiene señal predictiva clara (ranking, puntos,
  superficie). Permite un problema de clasificación con una línea base fácil de entender.
- **Datos:** 11.442 partidos de las temporadas 2019, 2021, 2022 y 2023, en formato de
  Jeff Sackmann (`data/tenis_matches_2019_2023.csv`).
- **Origen:** mirror `github.com/farhadGithub/tennis-atp-data` de los datos de Jeff Sackmann
  (el repositorio original dejó de estar disponible). Descarga: 5 de octubre de 2026.
- **Licencia:** CC BY-NC-SA 4.0 (atribución, uso no comercial, compartir igual). Uso académico.

## Problema y modelo

- **Objetivo:** estimar la probabilidad de que gane el `jugador_1` en un partido.
- **Sin fuga de información:** el CSV trae ganador y perdedor en columnas fijas. `features.py`
  asigna cada jugador a `jugador_1` o `jugador_2` al azar (semilla fija) para que el modelo no
  vea siempre al ganador en el mismo lado.
- **Features:** diferencia de ranking, log del cociente de rankings, diferencia de puntos ATP,
  de edad y de altura, formato (`best_of`), superficie y ronda.
- **Modelo:** regresión logística de scikit-learn con preprocesado (imputación de la mediana,
  escalado y one-hot) dentro de un único `Pipeline`, guardado con `joblib`.
- **Evaluación:** split temporal. Entrena con las temporadas anteriores a 2023 y evalúa en 2023.
- **Línea base:** "gana el mejor clasificado" acierta el 63,2 % de los partidos de 2023
  (tras validar). El modelo debe mejorarla.
- **Resultados:** `reports/metrics.json` (accuracy, F1 y línea base), generado por `train`.

## Reglas de validación

Partido válido si tiene superficie reconocida (`Hard`, `Clay`, `Grass`, `Carpet`), marcador,
`best_of` de 3 o 5, nombres de ambos jugadores, y ranking y puntos ATP de los dos.
Edad y altura pueden faltar (se imputan). Con el CSV real: 11.262 válidos y 180 descartados.

## Hugging Face

- **Tarea:** `chat_completion` (Inference API).
- **Modelo:** `Qwen/Qwen2.5-7B-Instruct` por defecto, configurable con `HF_MODEL`.
- **Uso en el flujo:** explica en dos frases la probabilidad que da sklearn. No sustituye
  al modelo ni aporta datos nuevos.
- **Cliente:** `ExplanationClient` (Protocol) con `MockExplanationClient` y
  `HFExplanationClient`. **En tests y CI corre siempre el mock.**
- Detalle en [`AI_USAGE.md`](AI_USAGE.md).

## Estructura

```text
proyecto_ii/
  tenis_ml/   config, loader, validator, features, train, predict, hf_client, pipeline, cli
  tests/      un fichero por módulo + tests de pipeline/CLI
  data/       CSV de partidos
  models/     modelo entrenado (tenis_model.joblib)
  reports/    métricas (metrics.json)
  .env.example  requirements.txt  AI_USAGE.md
```

## Cómo usarlo

Desde `proyecto_ii/` (con las dependencias instaladas):

```bash
# 1. Entrenar y guardar modelo + métricas
python -m tenis_ml.cli train

# 2. Predecir sobre la temporada 2023 y explicar 5 partidos (mock)
python -m tenis_ml.cli predict --season 2023 --explain 5 --client mock --output reports/predicciones.csv

# 3. Igual con Hugging Face real (requiere HF_TOKEN en .env)
python -m tenis_ml.cli predict --season 2023 --explain 5 --client hf --output reports/predicciones.csv
```

Configuración: copia `.env.example` a `.env` y rellena `HF_TOKEN`. `.env` está en `.gitignore`.

## Tests

```bash
pytest -q --cov=tenis_ml --cov-report=term-missing --cov-fail-under=60
pytest -q -m "not integration"   # solo unitarios
```

Los tests de integración usan el CSV real. El CI (`.github/workflows/ci_proyecto_ii.yml`,
en la raíz del repositorio) ejecuta todo con cobertura mínima del 60 %.

## Qué se ampliará en el Proyecto III

- API (p. ej. FastAPI) con endpoint de predicción y de explicación (`/analyze` o equivalente),
  reutilizando `predict.py` y `hf_client.py` sin tocarlos.
- Despliegue y monitorización (logs, métricas de uso y de deriva de datos).
- Mejores modelos y más temporadas de datos.
