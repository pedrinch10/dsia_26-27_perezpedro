"""Cliente de borde para explicar predicciones con un modelo del Hub de Hugging Face.

Mismo contrato para el modo real y el mock: el resto del pipeline solo conoce
`ExplanationClient`. En tests y CI se usa siempre `mock`.
"""

import os
from typing import Protocol

DEFAULT_HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"


class HFConfigError(Exception):
    """Falta configuración del cliente real (p. ej. HF_TOKEN)."""


class HFRequestError(Exception):
    """La llamada a la Inference API ha fallado."""


class ExplanationClient(Protocol):
    def explain(self, context: dict) -> str: ...


def build_prompt(context: dict) -> str:
    favorite = context["player_1"] if context["prob_player_1_wins"] >= 0.5 else context["player_2"]
    return (
        "Eres un analista de tenis. Explica en 2 frases, en español y sin inventar datos, "
        "por qué un modelo estadístico da estas probabilidades.\n"
        f"Partido: {context['player_1']} vs {context['player_2']} "
        f"(superficie: {context['surface']}, ronda: {context['round']}).\n"
        f"Probabilidad de victoria de {context['player_1']}: "
        f"{context['prob_player_1_wins']:.0%}. Favorito del modelo: {favorite}.\n"
        f"Diferencia de ranking (jugador_1 - jugador_2): {context['rank_diff']:.0f}. "
        f"Diferencia de puntos ATP: {context['points_diff']:.0f}."
    )


class MockExplanationClient:
    """Respuesta determinista, sin red. Obligatorio en tests y CI."""

    def explain(self, context: dict) -> str:
        favorite = (
            context["player_1"] if context["prob_player_1_wins"] >= 0.5 else context["player_2"]
        )
        return (
            f"[mock] El modelo favorece a {favorite} en {context['surface']} "
            f"({context['prob_player_1_wins']:.0%} para {context['player_1']})."
        )


class HFExplanationClient:
    """Cliente real: tarea chat_completion de la Inference API de Hugging Face."""

    def __init__(self, token: str | None = None, model: str | None = None) -> None:
        self._token = token or os.getenv("HF_TOKEN")
        if not self._token:
            raise HFConfigError("Falta HF_TOKEN. Defínelo en .env (ver .env.example).")
        self._model = model or os.getenv("HF_MODEL") or DEFAULT_HF_MODEL

    def explain(self, context: dict) -> str:
        from huggingface_hub import InferenceClient  # import tardío: el mock no lo necesita

        try:
            client = InferenceClient(model=self._model, token=self._token)
            response = client.chat_completion(
                messages=[{"role": "user", "content": build_prompt(context)}],
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        except Exception as error:  # el borde traduce cualquier fallo a un error propio
            raise HFRequestError(f"Fallo al llamar a Hugging Face: {error}") from error


def get_client(mode: str) -> ExplanationClient:
    if mode == "mock":
        return MockExplanationClient()
    if mode == "hf":
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass
        return HFExplanationClient()
    raise ValueError(f"Modo de cliente desconocido: {mode!r} (usa 'mock' o 'hf')")
