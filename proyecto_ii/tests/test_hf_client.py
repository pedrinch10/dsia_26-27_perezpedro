"""Tests del cliente de borde (mock y real con huggingface_hub simulado)."""

import sys
import types

import pytest

from tenis_ml.hf_client import (
    HFConfigError,
    HFExplanationClient,
    HFRequestError,
    MockExplanationClient,
    build_prompt,
    get_client,
)


@pytest.fixture
def context() -> dict:
    return {
        "player_1": "Jugador 5",
        "player_2": "Jugador 40",
        "surface": "Clay",
        "round": "QF",
        "prob_player_1_wins": 0.8,
        "rank_diff": -35.0,
        "points_diff": 1500.0,
    }


def test_mock_es_determinista_y_nombra_al_favorito(context):
    client = MockExplanationClient()
    assert client.explain(context) == client.explain(context)
    assert "Jugador 5" in client.explain(context)


def test_mock_elige_al_jugador_2_si_la_probabilidad_es_baja(context):
    context["prob_player_1_wins"] = 0.2
    assert "favorece a Jugador 40" in MockExplanationClient().explain(context)


def test_build_prompt_incluye_los_datos_del_partido(context):
    prompt = build_prompt(context)
    assert "Jugador 5" in prompt and "Clay" in prompt and "80%" in prompt


def test_get_client_mock():
    assert isinstance(get_client("mock"), MockExplanationClient)


def test_get_client_modo_desconocido_lanza_valueerror():
    with pytest.raises(ValueError):
        get_client("otro")


def test_cliente_real_sin_token_lanza_hfconfigerror(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(HFConfigError):
        HFExplanationClient()


def test_get_client_hf_con_token_devuelve_cliente_real(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "hf_falso")
    assert isinstance(get_client("hf"), HFExplanationClient)


def _fake_hub(monkeypatch, behavior):
    module = types.ModuleType("huggingface_hub")
    module.InferenceClient = behavior
    monkeypatch.setitem(sys.modules, "huggingface_hub", module)


def test_cliente_real_devuelve_el_texto_de_la_respuesta(monkeypatch, context):
    class FakeClient:
        def __init__(self, model, token):
            self.model, self.token = model, token

        def chat_completion(self, messages, max_tokens):
            message = types.SimpleNamespace(content="  Explicación simulada  ")
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=message)])

    _fake_hub(monkeypatch, FakeClient)
    client = HFExplanationClient(token="hf_falso", model="owner/modelo")
    assert client.explain(context) == "Explicación simulada"


def test_cliente_real_traduce_fallos_a_hfrequesterror(monkeypatch, context):
    class BrokenClient:
        def __init__(self, model, token):
            raise RuntimeError("sin red")

    _fake_hub(monkeypatch, BrokenClient)
    client = HFExplanationClient(token="hf_falso")
    with pytest.raises(HFRequestError):
        client.explain(context)
