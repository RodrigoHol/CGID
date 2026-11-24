"""Registro central de extractores reutilizables."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from etl.extractores.csv_estandar import extraer as extraer_csv_estandar
from etl.extractores.excel_generico import extraer as extraer_excel_generico
from etl.extractores.inegi_api import extraer as extraer_inegi_api
from etl.extractores.inegi_pobreza import extraer as extraer_inegi_pobreza
from etl.extractores.sep_educacion import extraer as extraer_sep_educacion

ExtractorFn = Callable[[Path, dict[str, Any], list[dict[str, Any]]], list[dict[str, Any]]]

EXTRACTORES: dict[str, ExtractorFn] = {
    "inegi_pobreza_excel": extraer_inegi_pobreza,
    "sep_educacion_xlsm": extraer_sep_educacion,
    "csv_estandar": extraer_csv_estandar,
    "excel_generico": extraer_excel_generico,
    "inegi_api": extraer_inegi_api,
}

EXTRACTORES_REMOTOS: set[str] = {"inegi_api"}


def obtener_extractor(nombre: str) -> ExtractorFn:
    """Devuelve la función extractora asociada al identificador configurado."""
    if nombre not in EXTRACTORES:
        raise ValueError(
            f"Extractor desconocido '{nombre}'. Disponibles: {sorted(EXTRACTORES)}."
        )
    return EXTRACTORES[nombre]
