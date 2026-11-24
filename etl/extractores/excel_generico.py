"""Extractor genérico para tabulados Excel con años en columnas y etiquetas en filas."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


def _normalizar_texto(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    return re.sub(r"\s+", " ", text).strip().casefold()


def _detectar_columnas_anio(
    frame: pd.DataFrame,
    header_row: int | None,
    expected_years: list[int] | None,
) -> dict[int, int]:
    candidate_rows = [header_row] if header_row is not None else list(range(min(len(frame), 30)))
    best_cols: dict[int, int] = {}

    for row_idx in candidate_rows:
        cols: dict[int, int] = {}
        for col_idx, val in enumerate(frame.iloc[row_idx].tolist()):
            if pd.isna(val):
                continue
            try:
                year = int(float(str(val).strip()))
            except (TypeError, ValueError):
                continue
            if 1950 <= year <= 2050 and (expected_years is None or year in expected_years):
                cols.setdefault(year, col_idx)
        if expected_years and set(expected_years).issubset(cols):
            return {year: cols[year] for year in expected_years}
        if len(cols) > len(best_cols):
            best_cols = cols

    if not best_cols:
        raise ValueError("No se encontraron columnas de años válidas en la hoja Excel.")
    if expected_years and not set(expected_years).issubset(best_cols):
        raise ValueError(
            f"Faltan años esperados {expected_years}; detectados: {sorted(best_cols)}."
        )
    return dict(sorted(best_cols.items()))


def _buscar_fila(
    frame: pd.DataFrame,
    label: str,
    label_columns: int,
    match_mode: str,
) -> int:
    objetivo = _normalizar_texto(label)
    coincidencias: list[int] = []
    for index, row in frame.iterrows():
        cells = [_normalizar_texto(value) for value in row.iloc[:label_columns]]
        if match_mode == "contains":
            matched = any(objetivo in cell for cell in cells if cell)
        else:
            matched = any(cell == objetivo for cell in cells)
        if matched:
            coincidencias.append(int(index))
    if len(coincidencias) != 1:
        raise ValueError(
            f"Se esperaba 1 fila para '{label}' y se encontraron {len(coincidencias)}."
        )
    return coincidencias[0]


def extraer(
    input_path: Path,
    source_cfg: dict[str, Any],
    indicators: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extrae series desde una hoja Excel tabulada usando configuración del manifiesto."""
    params = source_cfg.get("params", {})
    default_sheet = params.get("sheet", 0)
    header_row = params.get("header_row")
    expected_years = [int(y) for y in params["years"]] if params.get("years") else None
    label_columns = int(params.get("label_columns", 4))

    records: list[dict[str, Any]] = []
    cache: dict[str | int, tuple[pd.DataFrame, dict[int, int]]] = {}

    for ind in indicators:
        ind_params = ind.get("params", {})
        sheet = ind_params.get("sheet", default_sheet)
        if sheet not in cache:
            frame = pd.read_excel(input_path, sheet_name=sheet, header=None)
            year_cols = _detectar_columnas_anio(frame, header_row, expected_years)
            cache[sheet] = (frame, year_cols)
        frame, year_cols = cache[sheet]

        label = str(ind_params.get("label", "")).strip()
        if not label:
            raise ValueError(f"El indicador '{ind['id']}' requiere params.label.")
        match_mode = str(ind_params.get("match_mode", "exact"))
        complement = bool(ind_params.get("complement", False))
        row_idx = _buscar_fila(frame, label, label_columns, match_mode)

        for year, col_idx in year_cols.items():
            raw_val = frame.iloc[row_idx, col_idx]
            val = pd.to_numeric(raw_val, errors="coerce")
            if pd.isna(val):
                continue
            numeric = float(val)
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
