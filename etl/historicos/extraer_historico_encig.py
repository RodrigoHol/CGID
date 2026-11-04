"""Extrae el histórico estatal de IE016 desde el tabulador de ENCIG."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    ROOT
    / "data"
    / "raw"
    / "fuentes"
    / "inegi"
    / "encig"
    / "2023"
    / "II_evaluacion_servicios_bajo_demanda_encig2023_est.xlsx"
)
DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "processed"
    / "historicos"
    / "hechos"
    / "historico_ie016_encig.csv"
)
TABULADOR_INPUT = (
    ROOT
    / "data"
    / "raw"
    / "fuentes"
    / "inegi"
    / "encig"
    / "tabulado_interactivo_veracruz_ie016.csv"
)
INDICATOR_ID = "CGID-PVD25.30-ER1-O01-E02-IE016"
SHEET = "2.5"
ENTITY = "Veracruz de Ignacio de la Llave"
SATISFIED_RELATIVE_COLUMN = 37
HISTORICAL_VALUES = {
    2015: 38.6,
    2017: 43.9,
    2019: 50.5,
    2021: 65.5,
    2023: 65.0,
    2025: 46.6,
}


def extraer_historico(
    input_path: Path = TABULADOR_INPUT,
) -> pd.DataFrame:
    """Devuelve la serie relativa de satisfacción para Veracruz."""
    if not input_path.exists():
        raise FileNotFoundError(f"No existe el archivo fuente: {input_path}")
    try:
        source = pd.read_csv(input_path)
    except (OSError, pd.errors.ParserError) as exc:
        raise RuntimeError(f"No se pudo leer {input_path}: {exc}") from exc

    required = {"anio", "entidad", "servicio", "valor_relativo"}
    missing = required.difference(source.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}.")
    source = source[
        (source["entidad"].astype(str).str.strip() == ENTITY)
        & source["servicio"].astype(str).str.strip().eq(
            "Centros de salud y hospitales del gobierno de su estado"
        )
    ].copy()
    if source.empty:
        raise ValueError(f"No hay registros estatales para '{ENTITY}'.")
    source["anio"] = pd.to_numeric(source["anio"], errors="coerce")
    source["valor_relativo"] = pd.to_numeric(source["valor_relativo"], errors="coerce")
    if source[["anio", "valor_relativo"]].isna().any().any():
        raise ValueError("La serie contiene años o valores no numéricos.")
    source["anio"] = source["anio"].astype(int)
    if set(source["anio"]) != set(HISTORICAL_VALUES):
        raise ValueError("La serie no contiene exactamente los periodos esperados.")
    if not source["valor_relativo"].between(0, 100).all():
        raise ValueError("La serie contiene porcentajes fuera del rango 0-100.")
    source = source.sort_values("anio")
    return pd.DataFrame(
        {
            "id_indicador": INDICATOR_ID,
            "anio": source["anio"].to_numpy(),
            "valor_real": source["valor_relativo"].to_numpy(),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=TABULADOR_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        result = extraer_historico(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(args.output, index=False, encoding="utf-8-sig")
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"Error al extraer histórico ENCIG: {exc}") from exc
    print(f"Se exportó {len(result)} registro a '{args.output}'.")


if __name__ == "__main__":
    main()
