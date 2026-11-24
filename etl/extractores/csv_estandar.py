"""Extractor genérico para fuentes CSV con filtros configurables."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def extraer(
    input_path: Path,
    source_cfg: dict[str, Any],
    indicators: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extrae series históricas desde un CSV tabular o en formato largo."""
    source_params = source_cfg.get("params", {})
    frame = pd.read_csv(input_path)

    default_year_col = str(source_params.get("year_column", "anio"))
    default_value_col = str(source_params.get("value_column", "valor_real"))
    default_id_col = source_params.get("id_column")
    if default_id_col is None and "id_indicador" in frame.columns:
        default_id_col = "id_indicador"

    default_min = source_params.get("min_value")
    default_max = source_params.get("max_value")

    records: list[dict[str, Any]] = []
    for ind in indicators:
        ind_params = ind.get("params", {})
        year_col = str(ind_params.get("year_column", default_year_col))
        value_col = str(ind_params.get("value_column", default_value_col))
        id_col = ind_params.get("id_column", default_id_col)
        min_value = ind_params.get("min_value", default_min)
        max_value = ind_params.get("max_value", default_max)
        filters = ind_params.get("filters", {})

        required = {year_col, value_col, *filters.keys()}
        if id_col:
            required.add(str(id_col))
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(
                f"Faltan columnas requeridas en '{input_path.name}': {sorted(missing)}."
            )

        subset = frame.copy()
        if id_col:
            subset = subset[subset[str(id_col)].astype(str).str.strip() == ind["id"]]
        for col, expected in filters.items():
            subset = subset[subset[col].astype(str).str.strip() == str(expected).strip()]

        if subset.empty:
            raise ValueError(
                f"No se encontraron registros en '{input_path.name}' para '{ind['id']}'."
            )

        years = pd.to_numeric(subset[year_col], errors="coerce")
        values = pd.to_numeric(subset[value_col], errors="coerce")
        if years.isna().any() or values.isna().any():
            raise ValueError(
                f"La serie de '{ind['id']}' en '{input_path.name}' contiene años o valores no numéricos."
            )
        if min_value is not None and (values < float(min_value)).any():
            raise ValueError(
                f"Valores por debajo de {min_value} para '{ind['id']}' en '{input_path.name}'."
            )
        if max_value is not None and (values > float(max_value)).any():
            raise ValueError(
                f"Valores por encima de {max_value} para '{ind['id']}' en '{input_path.name}'."
            )

        for anio, valor in zip(years.astype(int).tolist(), values.astype(float).tolist()):
            records.append(
                {
                    "id_indicador": ind["id"],
                    "anio": anio,
                    "valor_real": valor,
                }
            )
    return records
