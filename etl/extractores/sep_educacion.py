"""Extractor parametrizado para el libro XLSM de indicadores educativos de la SEP."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


def _normalize_key(value: object) -> str:
    return str(value).strip().zfill(7)


def _read_periods(workbook: Any, last_cycle: int) -> dict[str, int]:
    sheet = workbook["x ciclos"]
    periods: dict[str, int] = {}
    for row in range(1, sheet.max_row + 1):
        period = sheet.cell(row, 1).value
        code = sheet.cell(row, 20).value
        if not isinstance(period, str) or not isinstance(code, (str, int)):
            continue
        if "-" not in period:
            continue
        start_year = period.split("-", 1)[0]
        if start_year.isdigit():
            periods[str(code).zfill(2)] = int(start_year)

    expected = {str(cycle).zfill(2) for cycle in range(1, last_cycle + 1)}
    missing = expected.difference(periods)
    if missing:
        raise ValueError(f"No se encontraron ciclos escolares: {sorted(missing)}")
    return periods


def _read_base_values(
    workbook: Any,
    sheet_name: str,
    indicator_code: str,
    veracruz_code: str,
    last_cycle: int,
) -> dict[str, float]:
    sheet = workbook[sheet_name]
    values: dict[str, float] = {}
    suffix = indicator_code.zfill(3)
    valid_cycles = {str(cycle).zfill(2) for cycle in range(1, last_cycle + 1)}

    for row in sheet.iter_rows(min_row=2, values_only=True):
        key = _normalize_key(row[0])
        if key.startswith(veracruz_code) and key.endswith(suffix) and key[2:4] in valid_cycles:
            value = row[5]
            if value is None or isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                numeric = float(value)
            else:
                text = str(value).strip()
                if not text or text.lower() in {"n.d.", "n/d", "#n/a", "na", "n/a"}:
                    continue
                try:
                    numeric = float(text)
                except ValueError:
                    continue
            if math.isfinite(numeric):
                values[key[2:4]] = numeric

    if not values:
        raise ValueError(
            f"No se encontraron ciclos numéricos para entidad {veracruz_code} e indicador {indicator_code}."
        )
    return values


def extraer(
    input_path: Path,
    source_cfg: dict[str, Any],
    indicators: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extrae series educativas estatales de Veracruz desde tablas base SEP."""
    params = source_cfg.get("params", {})
    veracruz_code = str(params.get("veracruz_code", "30")).zfill(2)
    last_cycle = int(params.get("last_cycle", 36))

    workbook = load_workbook(
        input_path,
        data_only=True,
        keep_vba=True,
        read_only=True,
    )
    try:
        periods = _read_periods(workbook, last_cycle)
        records: list[dict[str, Any]] = []
        for ind in indicators:
            ind_params = ind.get("params", {})
            sheet_name = str(ind_params.get("sheet", "")).strip()
            code = str(ind_params.get("code", "")).strip()
            if not sheet_name or not code:
                raise ValueError(
                    f"El indicador '{ind['id']}' requiere params.sheet y params.code."
                )
            values = _read_base_values(workbook, sheet_name, code, veracruz_code, last_cycle)
            for cycle in sorted(values):
                records.append(
                    {
                        "id_indicador": ind["id"],
                        "anio": periods[cycle],
                        "valor_real": values[cycle],
                    }
                )
        return records
    finally:
        workbook.close()
