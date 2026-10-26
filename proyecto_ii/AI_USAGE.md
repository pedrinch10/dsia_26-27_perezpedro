# AI_USAGE

## Asistente de desarrollo

- **Herramienta:** Claude (Anthropic), usado como asistente de programación.
- **Qué generó:** la estructura del paquete `tenis_ml`, el código de `loader`, `validator`,
  `features`, `train`, `predict`, `hf_client`, `pipeline` y `cli`, los tests y los borradores
  de README y workflow de CI.
- **Verificación:** la lógica de datos (validación y construcción de features) se comprobó
  con el CSV real; el entrenamiento y los tests con scikit-learn se ejecutan en el entorno
  local del autor y en el CI.

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
