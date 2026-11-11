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
  (tras validar). Es la referencia con la que se compara el modelo.

## Resultados

Generados por `python -m tenis_ml.cli train` y guardados en `reports/metrics.json`
(ejecución del 11 de noviembre de 2026 con scikit-learn 1.9.1 y pandas 3.0.5; pueden variar
ligeramente con otras versiones):

| Métrica (test: temporada 2023, 2.904 partidos) | Valor |
| --- | --- |
| Accuracy del modelo | 0,637 |
| F1 del modelo | 0,641 |
| Accuracy de la línea base (gana el mejor ranking) | 0,632 |

Entrenamiento con 8.358 partidos (2019, 2021 y 2022).

**Lectura honesta:** el modelo mejora la línea base en solo 0,5 puntos, con un único split.
No es una mejora demostrable: casi toda la señal está ya en el ranking. El valor de esta
entrega es el pipeline reproducible (validación, features sin fuga, split temporal, modelo
persistido e inferencia integrada); mejorar el modelo queda para el Proyecto III.

<!-- PARA PEDRO: reejecuta `train` en tu entorno (uv) y confirma o actualiza estas cifras.
     Decide si quieres añadir alguna mejora del modelo y justifícala con tus palabras. -->

**Artefactos:** se versiona el informe `reports/metrics.json`. El modelo
`models/tenis_model.joblib` se regenera con `train` (un `.joblib` depende de la versión de
scikit-learn con la que se guardó, así que conviene reentrenar en cada entorno).

<!-- PARA PEDRO: el enunciado admite "modelo entrenado y/o instrucciones claras para
     reentrenar". Si prefieres subir también el .joblib, entrénalo con tu uv.lock y cambia este párrafo. -->

## Reglas de validación

Partido válido si tiene superficie reconocida (`Hard`, `Clay`, `Grass`, `Carpet`), marcador,
`best_of` de 3 o 5, nombres de ambos jugadores, y ranking y puntos ATP de los dos.
Edad y altura pueden faltar (se imputan). Con el CSV real: 11.262 válidos y 180 descartados.

## Hugging Face

- **Tarea:** `chat_completion` (Inference API).
- **Modelo:** `Qwen/Qwen2.5-7B-Instruct` por defecto, configurable con `HF_MODEL`.
- **Estado:** el modo `mock` está probado. La llamada real al Hub está implementada pero
  **pendiente de probar** con un `HF_TOKEN`.

<!-- PARA PEDRO: crea tu .env con HF_TOKEN, ejecuta el comando 3 de "Cómo usarlo" y sustituye la
     línea "Estado" por el resultado real. Si el modelo no responde, cambia HF_MODEL (guía B6.5;
     el demo de aula usa mistralai/Mistral-7B-Instruct-v0.3) y actualiza README, AI_USAGE y .env.example. -->
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

## Robustez: errores, logs y configuración

- **Errores propios por capa:** `DataLoadError` (datos), `TrainingError` (split vacío),
  `ModelNotFoundError` (falta entrenar), `HFConfigError` (falta `HF_TOKEN`) y
  `HFRequestError` (fallo de la Inference API).
- **CLI:** ante un error esperable escribe una línea `ERROR` en el log y termina con
  código de salida 1, sin traceback.
- **Degradación controlada:** si Hugging Face falla al explicar un partido, se registra un
  `WARNING`, la explicación queda vacía y las predicciones de sklearn se exportan igualmente.
- **Logs:** cada paso informa de filas cargadas, válidas y descartadas, métricas y ficheros
  generados. El nivel se cambia con la variable `LOG_LEVEL` (por defecto `INFO`).
- **Configuración:** rutas, semilla y temporada de test en `tenis_ml/config.py`; secretos
  solo por variables de entorno.

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
- Interfaz web o dashboard de monitorización que consuma esa API (obligatorio en el III).
- Despliegue y monitorización (logs, métricas de uso y de deriva de datos).
- Mejores modelos y más temporadas de datos.
