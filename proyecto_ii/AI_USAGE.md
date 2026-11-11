# AI_USAGE

## Asistente de desarrollo

- **Herramienta:** Claude (Anthropic), usado como asistente de programación y tutor,
  con acceso a la carpeta del repositorio.
- **Qué generó:** la estructura del paquete `tenis_ml` (`loader`, `validator`, `features`,
  `train`, `predict`, `hf_client`, `pipeline`, `cli`), los tests, el workflow de CI y los
  borradores de `README.md` y de este fichero. También propuso la orientación aleatoria
  jugador_1/jugador_2 para evitar fuga de información y el split temporal.
- **Qué decidí yo:** el dominio (tenis ATP, que ya usé en el Proyecto I), el dataset, el
  objetivo (probabilidad de que gane el jugador_1) y el uso de Hugging Face para explicar la
  predicción, tal y como sugirió el profesor.
- **Cómo lo verifiqué:**
  - Ejecuté en mi equipo (`uv sync`) los 46 tests: pasan, con 98,71 % de cobertura.
  - Ejecuté `python -m tenis_ml.cli train` y obtuve accuracy 0,637, F1 0,641 y línea base 0,632.
  - El CI de GitHub («CI - Proyecto II») pasa en el pull request.
  - Probé la llamada real a Hugging Face (ver más abajo): llega al servicio, pero no devuelve
    explicación por falta de créditos.
- **Qué acepté, qué corregí y qué entiendo:** Acepté el código generado por Claude tras comprobar que los 46 tests pasan en mi equipo, que el entrenamiento reproduce las métricas y que el CI de GitHub sale en verde. No he modificado manualmente el código generado. Las decisiones de dominio, datos y objetivo del modelo fueron mías. Entiendo el flujo: se validan los datos, se construyen variables sin fuga de información, se entrena una regresión logística con split temporal y Hugging Face solo explica la predicción. La llamada real a Hugging Face queda pendiente de probar.

## Modelo de Hugging Face en el producto

- **Proveedor:** Hugging Face Inference API (`huggingface_hub.InferenceClient`).
- **Tarea:** `chat_completion`.
- **Modelo del Hub:** `meta-llama/Llama-3.1-8B-Instruct`, configurable con la variable `HF_MODEL`. Claude propuso
  inicialmente `Qwen/Qwen2.5-7B-Instruct`; el material de la asignatura usa `mistralai/Mistral-7B-Instruct-v0.3`.
  Qwen devolvió `model_not_supported` y Mistral no figuraba en la lista pública de modelos
  servidos el 11 de noviembre de 2026, así que se cambió el valor por defecto.
- **Resultado de la prueba real (11 nov 2026):** con `Qwen/Qwen2.5-7B-Instruct` la API respondió `400
  model_not_supported`; con `meta-llama/Llama-3.1-8B-Instruct` respondió `402 Payment Required` (la cuenta gratuita no
  tiene créditos de Inference Providers). No se ha obtenido una explicación real.
  No he comprado créditos.
- **Para qué se usa:** explicar en lenguaje natural la probabilidad que da el modelo sklearn
  para un partido. No sustituye al modelo sklearn y no aporta datos nuevos: recibe solo
  las probabilidades y diferencias ya calculadas.
- **En CI y tests:** siempre modo `mock`, sin red ni secretos.
- **Secretos:** `HF_TOKEN` va en `.env` (ignorado por Git); `.env.example` solo trae la clave vacía.

## Comandos de evidencia

```bash
uv run pytest -q --cov=tenis_ml --cov-report=term-missing --cov-fail-under=60
uv run python -m tenis_ml.cli train
uv run python -m tenis_ml.cli predict --season 2023 --explain 3 --client mock --output reports/predicciones.csv
# Hugging Face real (requiere HF_TOKEN en .env y créditos en la cuenta):
uv run python -m tenis_ml.cli predict --season 2023 --explain 3 --client hf --output reports/predicciones.csv
```
