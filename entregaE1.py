"""E1 — Procesamiento de datos con pandas."""

import json

import pandas as pd

RUTA_CSV = "datos/ventas.csv"
RUTA_CSV_LIMPIO = "datos/ventas_limpias.csv"
RUTA_JSON_CALIDAD = "datos/calidad_datos.json"


def diagnosticar(frame: pd.DataFrame) -> None:
    print("Shape:", frame.shape)
    print("\nTipos de dato:\n", frame.dtypes)
    print("\nNulos por columna:\n", frame.isna().sum())


def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = frame.copy()
    work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
    work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")

    ok = (
        work["unidades"].notna() & (work["unidades"] > 0)
        & work["precio_unitario"].notna() & (work["precio_unitario"] > 0)
    )

    validos = work.loc[ok].copy()
    errores = work.loc[~ok].copy()
    validos["importe"] = validos["unidades"] * validos["precio_unitario"]
    return validos, errores


def agregar(validos: pd.DataFrame) -> None:
    print("\nImporte total por región:")
    print(validos.groupby("region")["importe"].sum().sort_values(ascending=False))

    print("\nTop 3 productos por importe:")
    print(validos.groupby("producto")["importe"].sum().sort_values(ascending=False).head(3))

    print("\nClientes con más de una compra:")
    conteo = validos["cliente_id"].value_counts()
    print(conteo[conteo > 1])


def exportar(validos: pd.DataFrame, errores: pd.DataFrame, frame_original: pd.DataFrame) -> None:
    validos.to_csv(RUTA_CSV_LIMPIO, index=False)

    calidad = {
        "filas_totales": len(frame_original),
        "filas_validas": len(validos),
        "filas_invalidas": len(errores),
        "importe_total": float(validos["importe"].sum()),
    }
    with open(RUTA_JSON_CALIDAD, "w", encoding="utf-8") as f:
        json.dump(calidad, f, indent=2, ensure_ascii=False)

    print("\nExportado:", RUTA_CSV_LIMPIO, "y", RUTA_JSON_CALIDAD)
    print(calidad)


def main() -> None:
    frame = pd.read_csv(RUTA_CSV)
    diagnosticar(frame)

    validos, errores = validar_ventas(frame)
    print(f"\nVálidas: {len(validos)} | Inválidas: {len(errores)}")  # debe ser 8 / 2

    agregar(validos)
    exportar(validos, errores, frame)


if __name__ == "__main__":
    main()