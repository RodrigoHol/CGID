"""Extractor parametrizado para tabulados estatales de pobreza multidimensional (INEGI)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


def _normalizar_texto(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    return re.sub(r"\s+", " ", text).strip().casefold()


def _validar_hoja_veracruz(frame: pd.DataFrame, sheet_name: str) -> None:
    contenido = " ".join(
        _normalizar_texto(value)
        for value in frame.iloc[:8].to_numpy().flatten()
        if pd.notna(value)
    )
    if "veracruz" not in contenido and sheet_name.casefold() != "ver.":
        raise ValueError(f"La hoja '{sheet_name}' no parece corresponder a Veracruz.")
    if "eum" in sheet_name.casefold() or "nacional" in contenido:
        raise ValueError("Se detectó un agregado nacional en lugar de Veracruz.")


def _encontrar_columnas_porcentaje(frame: pd.DataFrame, years: list[int]) -> dict[int, int]:
    for index in range(len(frame)):
        values = [_normalizar_texto(value) for value in frame.iloc[index].tolist()]
        if "porcentaje" in values:
            porcentaje_column = values.index("porcentaje")
            year_row = index + 1
            break
    else:
        raise ValueError("No se encontró el bloque de columnas 'Porcentaje'.")

    columnas: dict[int, int] = {}
    expected = set(years)
    for column, value in enumerate(frame.iloc[year_row, porcentaje_column:], porcentaje_column):
        if pd.notna(value):
            try:
                year = int(float(value))
            except (TypeError, ValueError):
                continue
            if year in expected and year not in columnas:
                columnas[year] = column

    if set(columnas) != expected:
        raise ValueError(
            f"No se encontraron todos los años esperados en porcentaje: {sorted(columnas)}."
        )
    return columnas


def _encontrar_fila_indicador(frame: pd.DataFrame, label: str) -> int:
    objetivo = _normalizar_texto(label)
    coincidencias = [
        index
        for index, row in frame.iterrows()
        if any(_normalizar_texto(value) == objetivo for value in row.iloc[:4])
    ]
    if len(coincidencias) != 1:
        raise ValueError(
            f"Se esperaba 1 fila para '{label}' y se encontraron {len(coincidencias)}."
        )
    return int(coincidencias[0])


def extraer(
    input_path: Path,
    source_cfg: dict[str, Any],
    indicators: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extrae series estatales desde el libro de pobreza multidimensional configurado."""
    params = source_cfg.get("params", {})
    sheet_name = str(params.get("sheet", "Ver."))
    years = [int(y) for y in params.get("years", [2016, 2018, 2020, 2022, 2024])]

    frame = pd.read_excel(input_path, sheet_name=sheet_name, header=None)
    _validar_hoja_veracruz(frame, sheet_name)
    percentage_columns = _encontrar_columnas_porcentaje(frame, years)

    records: list[dict[str, Any]] = []
    for ind in indicators:
        ind_params = ind.get("params", {})
        label = str(ind_params.get("label", "")).strip()
        if not label:
            raise ValueError(f"El indicador '{ind['id']}' requiere params.label.")
        complement = bool(ind_params.get("complement", False))
        row_index = _encontrar_fila_indicador(frame, label)

        for year in years:
            raw_value = frame.iloc[row_index, percentage_columns[year]]
            value = pd.to_numeric(raw_value, errors="coerce")
            if pd.isna(value):
                raise ValueError(
                    f"Valor no numérico para '{ind['id']}', año {year}: {raw_value!r}"
                )
            numeric = float(value)
            if complement:
                numeric = 100.0 - numeric
            records.append(
                {
                    "id_indicador": ind["id"],
                    "anio": year,
                    "valor_real": numeric,
                }
            )
    return records
