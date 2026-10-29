"""Extrae el histórico estatal del indicador de pobreza multidimensional.

La fuente pm_ef_2024.xlsx contiene una hoja por entidad y tres bloques de
variables: población, porcentaje y carencias promedio. Este ETL extrae el
porcentaje de pobreza de IE001 y calcula IE002 como el complemento de la
carencia por acceso a la seguridad social.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    ROOT
    / "data"
    / "raw"
    / "fuentes"
    / "inegi"
    / "pobreza_multidimensional"
    / "2024"
    / "pm_ef_2024.xlsx"
)
DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "processed"
    / "historicos"
    / "hechos"
    / "historico_pobreza.csv"
)
INDICATOR_ID_IE001 = "CGID-PVD25.30-ER1-O01-E00-IE001"
INDICATOR_ID_IE002 = "CGID-PVD25.30-ER1-O01-E00-IE002"
INDICATOR_LABEL_IE001 = "Población en situación de pobreza"
INDICATOR_LABEL_IE002 = "Carencia por acceso a la seguridad social"
YEARS = (2016, 2018, 2020, 2022, 2024)


def normalizar_texto(value: object) -> str:
    """Normaliza texto de Excel para comparar sin depender de acentos o espacios."""
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"\s+", " ", text).strip().casefold()
    return text


def encontrar_fila_indicador(frame: pd.DataFrame, label: str) -> int:
    """Encuentra la fila exacta del indicador, evitando subindicadores."""
    objetivo = normalizar_texto(label)
    coincidencias = []
    for index, value in frame.iloc[:, 0].items():
        if normalizar_texto(value) == objetivo:
            coincidencias.append(index)
    if len(coincidencias) != 1:
        raise ValueError(
            f"Se esperaban 1 fila para '{label}' y se encontraron "
            f"{len(coincidencias)}."
        )
    return coincidencias[0]


def encontrar_columnas_porcentaje(frame: pd.DataFrame) -> dict[int, int]:
    """Obtiene las columnas del bloque Porcentaje a partir de la fila de años."""
    porcentaje_column = None
    for index in range(len(frame)):
        values = [normalizar_texto(value) for value in frame.iloc[index].tolist()]
        if "porcentaje" in values:
            porcentaje_column = values.index("porcentaje")
            year_row = index + 1
            break
    else:
        raise ValueError("No se encontró el bloque de columnas 'Porcentaje'.")

    columnas = {}
    for column, value in enumerate(frame.iloc[year_row, porcentaje_column:], porcentaje_column):
        if pd.notna(value):
            try:
                year = int(float(value))
            except (TypeError, ValueError):
                continue
            if year in YEARS and year not in columnas:
                columnas[year] = column

    if set(columnas) != set(YEARS):
        raise ValueError(
            f"No se encontraron todos los años esperados en porcentaje: "
            f"{sorted(columnas)}."
        )
    return columnas


def validar_hoja_veracruz(frame: pd.DataFrame, sheet_name: str) -> None:
    """Valida que la hoja corresponde a Veracruz y no a un agregado nacional."""
    contenido = " ".join(
        normalizar_texto(value)
        for value in frame.iloc[:8].to_numpy().flatten()
        if pd.notna(value)
    )
    if "veracruz" not in contenido and sheet_name.casefold() != "ver.":
        raise ValueError(
            f"La hoja '{sheet_name}' no parece corresponder a Veracruz."
        )
    if "eum" in sheet_name.casefold() or "nacional" in contenido:
        raise ValueError("Se detectó un agregado nacional en lugar de Veracruz.")


def extraer_historico(
    input_path: Path = DEFAULT_INPUT,
    sheet_name: str = "Ver.",
) -> pd.DataFrame:
    """Lee la fuente cruda y devuelve IE001 e IE002 en formato largo."""
    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo fuente: {input_path}")

    try:
        frame = pd.read_excel(input_path, sheet_name=sheet_name, header=None)
    except (ValueError, OSError) as exc:
        raise RuntimeError(
            f"No se pudo leer la hoja '{sheet_name}' de {input_path}: {exc}"
        ) from exc

    validar_hoja_veracruz(frame, sheet_name)
    percentage_columns = encontrar_columnas_porcentaje(frame)

    records = []
    definitions = (
        (INDICATOR_ID_IE001, INDICATOR_LABEL_IE001, False),
        (INDICATOR_ID_IE002, INDICATOR_LABEL_IE002, True),
    )
    for indicator_id, label, complement in definitions:
        row_index = encontrar_fila_indicador(frame, label)
        for year in YEARS:
            raw_value = frame.iloc[row_index, percentage_columns[year]]
            value = pd.to_numeric(raw_value, errors="coerce")
            if pd.isna(value):
                raise ValueError(f"El valor de {year} no es numérico: {raw_value!r}")
            if complement:
                value = 100 - value
            records.append(
                {"id_indicador": indicator_id, "anio": year, "valor_real": float(value)}
            )

    return pd.DataFrame(records, columns=["id_indicador", "anio", "valor_real"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sheet", default="Ver.")
    args = parser.parse_args()

    try:
        result = extraer_historico(args.input, args.sheet)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(args.output, index=False, encoding="utf-8-sig")
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"Error al extraer histórico: {exc}") from exc

    print(f"Se exportaron {len(result)} registros a '{args.output}'.")


if __name__ == "__main__":
    main()
