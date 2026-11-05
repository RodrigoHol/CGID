"""Extrae las tasas de cobertura educativa de Veracruz publicadas por la SEP.

El libro XLSM contiene tablas base en las hojas ``1`` y ``2``. Las macros
construyen las vistas, pero no son necesarias para el ETL: cada registro se
identifica por entidad, ciclo escolar e indicador en la columna ``INDICE``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    ROOT
    / "data"
    / "raw"
    / "fuentes"
    / "sep"
    / "educacion"
    / "2026"
    / "reporte_indicadores_educativos_sep_2026.xlsm"
)
DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "processed"
    / "historicos"
    / "hechos"
    / "historico_educacion_sep.csv"
)

VERACRUZ_CODE = "33"
LAST_HISTORICAL_CYCLE = 36  # 2025-2026; los ciclos siguientes son pronósticos.
INDICATORS = (
    ("CGID-PVD25.30-ER1-O01-E03-IE017", "1", "129"),
    ("CGID-PVD25.30-ER1-O01-E03-IE018", "1", "133"),
    ("CGID-PVD25.30-ER1-O01-E03-IE019", "2", "224"),
)


def normalize_key(value: object) -> str:
    """Devuelve una clave de siete posiciones conservando ceros iniciales."""
    return str(value).strip().zfill(7)


def read_periods(workbook) -> dict[str, int]:
    """Obtiene el año inicial de cada ciclo desde la tabla de ciclos del libro."""
    sheet = workbook["x ciclos"]
    periods = {}
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
    expected = {str(cycle).zfill(2) for cycle in range(1, LAST_HISTORICAL_CYCLE + 1)}
    missing = expected.difference(periods)
    if missing:
        raise ValueError(f"No se encontraron ciclos escolares: {sorted(missing)}")
    return periods


def read_base_values(workbook, sheet_name: str, indicator_code: str) -> dict[str, float]:
    """Lee los porcentajes de Veracruz para un indicador de una tabla base."""
    sheet = workbook[sheet_name]
    values = {}
    suffix = indicator_code.zfill(3)
    for row in sheet.iter_rows(min_row=2, values_only=True):
        key = normalize_key(row[0])
        if (
            key.startswith(VERACRUZ_CODE)
            and key.endswith(suffix)
            and key[2:4] in {str(cycle).zfill(2) for cycle in range(1, LAST_HISTORICAL_CYCLE + 1)}
        ):
            value = row[5]
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"Valor no numérico para Veracruz, ciclo {key[2:4]}, "
                    f"indicador {indicator_code}: {value!r}"
                )
            values[key[2:4]] = float(value)

    expected = {str(cycle).zfill(2) for cycle in range(1, LAST_HISTORICAL_CYCLE + 1)}
    missing = expected.difference(values)
    if missing:
        raise ValueError(
            f"Faltan ciclos para Veracruz e indicador {indicator_code}: "
            f"{sorted(missing)}"
        )
    return values


def extract(input_path: Path = DEFAULT_INPUT):
    """Extrae IE017-IE019 y devuelve registros en el contrato histórico."""
    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo fuente: {input_path}")

    workbook = load_workbook(
        input_path,
        data_only=True,
        keep_vba=True,
        read_only=True,
    )
    periods = read_periods(workbook)
    records = []
    for indicator_id, sheet_name, indicator_code in INDICATORS:
        values = read_base_values(workbook, sheet_name, indicator_code)
        for cycle in sorted(values):
            records.append(
                {
                    "id_indicador": indicator_id,
                    "anio": periods[cycle],
                    "valor_real": values[cycle],
                }
            )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        records = extract(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        import csv

        with args.output.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=["id_indicador", "anio", "valor_real"],
            )
            writer.writeheader()
            writer.writerows(records)
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise SystemExit(f"Error al extraer histórico educativo: {exc}") from exc

    print(f"Se exportaron {len(records)} registros a '{args.output}'.")


if __name__ == "__main__":
    main()
