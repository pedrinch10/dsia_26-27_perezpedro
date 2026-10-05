"""Tests de SalesValidator (Proyecto I - Parte A)."""

import pandas as pd
import pytest

from ventas_app.validator import SalesRecord, SalesValidator


@pytest.fixture
def ventas_mini() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fecha": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "region": ["Norte", "Sur", "Norte"],
            "producto": ["A", "B", "A"],
            "unidades": [2, None, 5],
            "precio_unitario": [10.0, 20.0, -1.0],
            "cliente_id": ["C1", "C2", "C1"],
        }
    )


@pytest.fixture
def validator() -> SalesValidator:
    return SalesValidator()


def test_split_cuenta_validos_e_invalidos(validator, ventas_mini):
    # Arrange: ventas_mini tiene 1 fila válida, 2 inválidas (unidades nula y precio negativo)
    # Act
    validos, errores = validator.split(ventas_mini)
    # Assert
    assert len(validos) == 1
    assert len(errores) == 2


def test_split_calcula_amount_correctamente(validator, ventas_mini):
    validos, _ = validator.split(ventas_mini)
    assert validos[0].amount == 20.0  # 2 unidades * 10.0


def test_split_no_muta_el_dataframe_original(validator, ventas_mini):
    original = ventas_mini.copy()
    validator.split(ventas_mini)
    pd.testing.assert_frame_equal(ventas_mini, original)


def test_sales_record_es_inmutable(validator, ventas_mini):
    validos, _ = validator.split(ventas_mini)
    record = validos[0]
    with pytest.raises(AttributeError):
        record.units = 999  # frozen=True debe impedir la mutación


@pytest.mark.parametrize("precio", [0, -1, -100])
def test_precio_no_positivo_no_es_valido(validator, precio):
    df = pd.DataFrame(
        {
            "region": ["Norte"],
            "producto": ["A"],
            "unidades": [1],
            "precio_unitario": [precio],
        }
    )
    validos, errores = validator.split(df)
    assert len(validos) == 0
    assert len(errores) == 1


@pytest.mark.parametrize("unidades", [0, -5, None])
def test_unidades_no_positivas_o_nulas_no_son_validas(validator, unidades):
    df = pd.DataFrame(
        {
            "region": ["Norte"],
            "producto": ["A"],
            "unidades": [unidades],
            "precio_unitario": [10.0],
        }
    )
    validos, errores = validator.split(df)
    assert len(validos) == 0
    assert len(errores) == 1


def test_split_devuelve_sales_record(validator, ventas_mini):
    validos, _ = validator.split(ventas_mini)
    assert isinstance(validos[0], SalesRecord)


@pytest.mark.integration
def test_split_con_csv_real_checkpoint():
    """Checkpoint del curso con el ventas.csv real: 140 válidas / 10 inválidas."""
    from pathlib import Path

    from ventas_app.loader import CsvSalesRepository

    path = Path(__file__).resolve().parents[2] / "data" / "ventas.csv"
    repo = CsvSalesRepository(path)
    frame = repo.load()

    validator = SalesValidator()
    validos, errores = validator.split(frame)

    assert len(validos) == 140
    assert len(errores) == 10
