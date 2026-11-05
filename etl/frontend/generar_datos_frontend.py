"""Genera los artefactos JSON que consume la aplicación Vue del MVP."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data" / "processed" / "catalogo" / "mvp_indicadores.csv"
COVERAGE = ROOT / "data" / "manifests" / "mvp_indicadores.csv"
OUTPUT = ROOT / "data" / "processed" / "frontend"


def clean(value: object) -> str:
    return " ".join(str(value or "").split()).strip()


def nullable_float(value: object) -> float | None:
    try:
        if value is None or value == "" or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_periods(value: str) -> list[int]:
    return [int(item) for item in clean(value).split(",") if item]


def parse_json(value: str) -> dict[str, float]:
    if not clean(value):
        return {}
    parsed = json.loads(value)
    return {str(year): float(amount) for year, amount in parsed.items()}


def load_history(paths: set[str]) -> dict[str, list[dict[str, float | int]]]:
    history: dict[str, list[dict[str, float | int]]] = {}
    for relative_path in paths:
        if not relative_path:
            continue
        source = ROOT / relative_path
        if not source.exists():
            raise FileNotFoundError(f"No existe el histórico procesado: {source}")
        frame = pd.read_csv(source)
        required = {"id_indicador", "anio", "valor_real"}
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{source} no contiene columnas: {sorted(missing)}")
        for row in frame.itertuples(index=False):
            value = nullable_float(row.valor_real)
            if value is None:
                raise ValueError(
                    f"Valor histórico inválido para {row.id_indicador}, año {row.anio}."
                )
            history.setdefault(str(row.id_indicador), []).append(
                {"anio": int(row.anio), "valor": value}
            )
    for records in history.values():
        records.sort(key=lambda item: item["anio"])
    return history


def build_sources(coverage: pd.DataFrame) -> list[dict[str, object]]:
    sources = []
    for row in coverage.itertuples(index=False):
        institution = (
            "SEP"
            if "sep" in clean(row.archivo_crudo).casefold()
            else "INEGI"
        )
        sources.append(
            {
                "idIndicador": row.id_indicador,
                "institucion": institution,
                "nombre": clean(row.nombre),
                "url": clean(row.url_fuente),
                "archivoCrudo": clean(row.archivo_crudo),
                "archivoProcesado": clean(row.archivo_procesado),
                "periodos": parse_periods(row.periodos_disponibles),
                "entidad": clean(row.entidad),
                "estado": clean(row.estado_historico),
                "observaciones": clean(row.observaciones),
            }
        )
    return sources


def main() -> None:
    catalog = pd.read_csv(CATALOG, dtype=str, keep_default_na=False)
    coverage = pd.read_csv(COVERAGE, dtype=str, keep_default_na=False)
    if catalog["clave"].duplicated().any():
        raise ValueError("El catálogo MVP contiene claves duplicadas.")
    if set(catalog["clave"]) != set(coverage["id_indicador"]):
        raise ValueError("Catálogo y matriz de cobertura no contienen el mismo alcance.")

    history = load_history(set(coverage["archivo_procesado"]))
    indicators = []
    for row in catalog.itertuples(index=False):
        coverage_row = coverage[coverage["id_indicador"] == row.clave].iloc[0]
        records = history.get(row.clave, [])
        indicators.append(
            {
                "id": row.clave,
                "clave": row.clave,
                "nombre": clean(row.nombre),
                "descripcion": clean(row.descripcion),
                "formula": clean(row.formula),
                "unidadMedida": clean(row.unidad_medida),
                "sentido": clean(row.sentido),
                "ejeRector": clean(row.eje_rector),
                "lineaBase": {
                    "anio": int(row.linea_base_anio)
                    if clean(row.linea_base_anio)
                    else None,
                    "valor": nullable_float(row.linea_base_valor),
                },
                "meta2030": nullable_float(row.meta_2030_valor),
                "metasIntermedias": parse_json(row.metas_intermedias_json),
                "estadoHistorico": clean(coverage_row.estado_historico),
                "periodosDisponibles": parse_periods(
                    coverage_row.periodos_disponibles
                ),
                "tieneHistorico": bool(records),
                "fuente": {
                    "url": clean(coverage_row.url_fuente),
                    "medioVerificacion": clean(row.medio_verificacion),
                    "archivoCrudo": clean(coverage_row.archivo_crudo),
                    "observaciones": clean(coverage_row.observaciones),
                },
            }
        )

    history_payload = {
        indicator_id: {
            "entidad": clean(
                coverage.loc[
                    coverage["id_indicador"] == indicator_id, "entidad"
                ].iloc[0]
            ),
            "datos": records,
        }
        for indicator_id, records in history.items()
    }
    status_counts = coverage["estado_historico"].value_counts().to_dict()
    summary = {
        "entidad": "Veracruz",
        "totalIndicadores": len(indicators),
        "indicadoresConHistorico": sum(
            indicator["tieneHistorico"] for indicator in indicators
        ),
        "indicadoresSinHistorico": sum(
            not indicator["tieneHistorico"] for indicator in indicators
        ),
        "indicadoresConMeta2030": sum(
            indicator["meta2030"] is not None for indicator in indicators
        ),
        "porEstadoHistorico": {
            str(key): int(value) for key, value in status_counts.items()
        },
        "periodosHistoricos": sorted(
            {record["anio"] for records in history.values() for record in records}
        ),
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = {
        "indicadores_mvp.json": indicators,
        "historicos_mvp.json": history_payload,
        "fuentes_mvp.json": build_sources(coverage),
        "resumen_mvp.json": summary,
    }
    for filename, payload in files.items():
        (OUTPUT / filename).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"Se generaron {len(files)} archivos en '{OUTPUT}'.")


if __name__ == "__main__":
    main()
