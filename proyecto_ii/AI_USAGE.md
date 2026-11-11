# AI_USAGE

## Asistente de desarrollo

- **Herramienta:** Claude (Anthropic), usado como asistente de programación.
- **Qué generó:** la estructura del paquete `tenis_ml`, el código de `loader`, `validator`,
  `features`, `train`, `predict`, `hf_client`, `pipeline` y `cli`, los tests y los borradores
  de README y workflow de CI.
- **Verificación:** el asistente ejecutó los tests (46 en verde), el entrenamiento y la
  predicción en modo `mock` con el CSV real el 11 de noviembre de 2026 (scikit-learn 1.9.1,
  pandas 3.0.5). No se ha probado la llamada real a Hugging Face.

## Qué acepté y qué revisé

<!-- PARA PEDRO: esta sección la pide el enunciado ("qué aceptaste") y debe ser tuya.
     Sustituye el borrador por lo que hayas hecho de verdad. Guion orientativo:
     - Ejecuté los tests y el entrenamiento en mi entorno (fecha, resultado).
     - Revisé línea a línea: features.py, train.py, hf_client.py (lo que entendí o cambié).
     - Decisiones mías: dominio y dataset de tenis, uso de HF para explicar la predicción.
     - Probé el cliente real con el modelo X (o: pendiente por falta de token). -->

- _Pendiente de redactar por el autor._

## Modelo de Hugging Face en el producto

- **Proveedor:** Hugging Face Inference API (`huggingface_hub.InferenceClient`).
- **Tarea:** `chat_completion`.
- **Modelo del Hub:** valor por defecto `Qwen/Qwen2.5-7B-Instruct`, configurable con la
  variable `HF_MODEL`. Hay que confirmar que está disponible con el token del autor.
- **Para qué se usa:** explicar en lenguaje natural la probabilidad que da el modelo sklearn
  para un partido. No sustituye al modelo sklearn y no aporta datos nuevos: recibe solo
  las probabilidades y diferencias ya calculadas.
- **En CI y tests:** siempre modo `mock`, sin red ni secretos.
- **Secretos:** `HF_TOKEN` va en `.env` (ignorado por Git); `.env.example` solo trae la clave vacía.
