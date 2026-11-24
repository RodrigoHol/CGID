"""Orquestador único del pipeline ETL guiado por manifiesto."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.common.validacion import validar_hechos, validar_manifiesto
from etl.extractores import EXTRACTORES, EXTRACTORES_REMOTOS, obtener_extractor

DEFAULT_MANIFEST = ROOT / "config" / "manifiesto_indicadores.json"


def _clean(value: object) -> str:
    return " ".join(str(value or "").split()).strip()


def _es_medio_valido(medio: str) -> bool:
    return bool(medio) and not bool(re.match(r"^(?:N/A|NA|N/D)\b", medio, re.IGNORECASE))


def _nullable_float(value: object) -> float | None:
    try:
        if value is None or value == "" or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_json(value: str) -> dict[str, float]:
    if not _clean(value):
        return {}
    parsed = json.loads(value)
    return {str(year): float(amount) for year, amount in parsed.items()}


def _resolve(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else ROOT / path


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        raise FileNotFoundError(f"No existe el manifiesto: {manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _write_facts_csv(output_path: Path, records: list[dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id_indicador", "anio", "valor_real"])
        writer.writeheader()
        writer.writerows(records)


def _read_facts_csv(csv_path: Path, fuente_id: str) -> list[dict[str, Any]]:
    frame = pd.read_csv(csv_path)
    records = frame.to_dict(orient="records")
    return validar_hechos(records, fuente_id)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_pipeline(
    manifest_path: Path = DEFAULT_MANIFEST,
    only_source: str | None = None,
    skip_extract: bool = False,
    check_only: bool = False,
) -> dict[str, Any]:
    """Ejecuta extracción, validación y generación de salidas para el frontend."""
    manifiesto = _load_manifest(manifest_path)
    entidad = str(manifiesto["entidad"])
    catalogo_maestro = _resolve(manifiesto.get("catalogo_maestro", "data/processed/catalogo/indicadores.csv"))
    catalogo_salida = _resolve(manifiesto.get("catalogo_salida", "data/processed/catalogo/mvp_indicadores.csv"))
    cobertura_salida = _resolve(manifiesto.get("cobertura_salida", "data/manifests/mvp_indicadores.csv"))
    directorio_frontend = _resolve(manifiesto.get("directorio_frontend", "data/processed/frontend"))

    if not catalogo_maestro.exists():
        raise FileNotFoundError(f"No existe el catálogo maestro: {catalogo_maestro}")

    catalog = pd.read_csv(catalogo_maestro, dtype=str, keep_default_na=False)
    validar_manifiesto(manifiesto, catalog, EXTRACTORES.keys(), EXTRACTORES_REMOTOS)

    fuentes: dict[str, dict[str, Any]] = manifiesto["fuentes"]
    indicadores_cfg: list[dict[str, Any]] = manifiesto["indicadores"]

    if only_source is not None:
        if only_source not in fuentes:
            raise ValueError(
                f"La fuente '{only_source}' no existe en el manifiesto. "
                f"Opciones: {sorted(fuentes)}."
            )
        if not fuentes[only_source].get("extractor"):
            raise ValueError(f"La fuente '{only_source}' no tiene extractor configurado.")

    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in indicadores_cfg:
        grouped.setdefault(item["fuente_id"], []).append(item)

    # 1. Validar archivos crudos y extraer fuentes configuradas
    extracted_sources: list[tuple[str, int]] = []
    for fuente_id, source_cfg in fuentes.items():
        extractor_name = source_cfg.get("extractor")
        if not extractor_name:
            continue

        is_remote = str(extractor_name) in EXTRACTORES_REMOTOS
        raw_path = ROOT if is_remote else _resolve(source_cfg["archivo_crudo"])
        out_path = _resolve(source_cfg["archivo_salida"])
        source_indicators = grouped.get(fuente_id, [])

        if not source_indicators:
            continue

        should_extract = (
            not check_only
            and not skip_extract
            and (only_source is None or only_source == fuente_id)
        )

        if not is_remote and (check_only or should_extract):
            if not raw_path.exists():
                raise FileNotFoundError(
                    f"Falta archivo crudo para '{fuente_id}': {raw_path}"
                )

        if should_extract:
            extractor_fn = obtener_extractor(str(extractor_name))
            records = extractor_fn(raw_path, source_cfg, source_indicators)
            validated = validar_hechos(records, fuente_id)
            _write_facts_csv(out_path, validated)
            extracted_sources.append((fuente_id, len(validated)))

    # 2. Leer todos los hechos validados desde los CSV procesados
    facts_by_indicator: dict[str, list[dict[str, Any]]] = {}
    loaded_files: set[Path] = set()
    for fuente_id, source_cfg in fuentes.items():
        salida_str = str(source_cfg.get("archivo_salida", "")).strip()
        if not salida_str:
            continue
        out_path = _resolve(salida_str)
        if out_path in loaded_files:
            continue
        if not out_path.exists():
            if source_cfg.get("extractor") and check_only:
                continue
            raise FileNotFoundError(f"Falta archivo de hechos '{out_path}' para '{fuente_id}'.")

        loaded_files.add(out_path)
        for record in _read_facts_csv(out_path, fuente_id):
            facts_by_indicator.setdefault(record["id_indicador"], []).append(
                {"anio": int(record["anio"]), "valor": float(record["valor_real"])}
            )

    for series in facts_by_indicator.values():
        series.sort(key=lambda item: item["anio"])

    # 3. Ensamblar subconjunto, matriz de cobertura y JSONs del frontend
    catalog_by_id = {row["clave"]: row for _, row in catalog.iterrows()}
    ordered_ids = [item["id"] for item in indicadores_cfg]

    subset_rows = [catalog_by_id[ind_id] for ind_id in ordered_ids]
    subset_df = pd.DataFrame(subset_rows, columns=catalog.columns)

    coverage_rows: list[dict[str, str]] = []
    frontend_indicators: list[dict[str, Any]] = []
    frontend_sources: list[dict[str, Any]] = []
    history_payload: dict[str, dict[str, Any]] = {}

    for item in indicadores_cfg:
        ind_id = item["id"]
        fuente_id = item["fuente_id"]
        source_cfg = fuentes[fuente_id]
        cat_row = catalog_by_id[ind_id]
        records = facts_by_indicator.get(ind_id, [])
        tiene_historico = bool(records)

        url = str(item["url"]) if "url" in item else str(source_cfg.get("url", ""))
        medio = _clean(cat_row["medio_verificacion"])

        if tiene_historico:
            estado = "procesado"
            is_remote = str(source_cfg.get("extractor", "")) in EXTRACTORES_REMOTOS
            archivo_crudo = "" if is_remote else str(source_cfg.get("archivo_crudo", ""))
            archivo_procesado = str(source_cfg.get("archivo_salida", ""))
            default_obs = "Serie histórica validada e integrada."
        elif url or _es_medio_valido(medio):
            estado = "fuente_identificada"
            archivo_crudo = ""
            archivo_procesado = ""
            default_obs = "Fuente identificada; pendiente de descarga y extracción."
        else:
            estado = "pendiente_revision"
            archivo_crudo = ""
            archivo_procesado = ""
            default_obs = "Medio de verificación vacío; requiere revisión documental."

        observaciones = str(item.get("observaciones") or default_obs)
        periodos = [int(point["anio"]) for point in records]
        periodos_str = ",".join(str(y) for y in periodos)

        coverage_rows.append(
            {
                "id_indicador": ind_id,
                "nombre": _clean(cat_row["nombre"]),
                "fuente_verificacion": medio,
                "url_fuente": url,
                "estado_historico": estado,
                "archivo_crudo": archivo_crudo,
                "archivo_procesado": archivo_procesado,
                "periodos_disponibles": periodos_str,
                "entidad": entidad,
                "observaciones": observaciones,
            }
        )

        frontend_indicators.append(
            {
                "id": ind_id,
                "clave": ind_id,
                "nombre": _clean(cat_row["nombre"]),
                "descripcion": _clean(cat_row["descripcion"]),
                "formula": _clean(cat_row["formula"]),
                "unidadMedida": _clean(cat_row["unidad_medida"]),
                "sentido": _clean(cat_row["sentido"]),
                "ejeRector": _clean(cat_row["eje_rector"]),
                "lineaBase": {
                    "anio": int(float(cat_row["linea_base_anio"])) if _clean(cat_row["linea_base_anio"]) else None,
                    "valor": _nullable_float(cat_row["linea_base_valor"]),
                },
                "meta2030": _nullable_float(cat_row["meta_2030_valor"]),
                "metasIntermedias": _parse_json(cat_row["metas_intermedias_json"]),
                "estadoHistorico": estado,
                "periodosDisponibles": periodos,
                "tieneHistorico": tiene_historico,
                "fuente": {
                    "url": url,
                    "medioVerificacion": medio,
                    "archivoCrudo": archivo_crudo,
                    "observaciones": observaciones,
                },
            }
        )

        frontend_sources.append(
            {
                "idIndicador": ind_id,
                "institucion": str(source_cfg["institucion"]),
                "nombre": _clean(cat_row["nombre"]),
                "url": url,
                "archivoCrudo": archivo_crudo,
                "archivoProcesado": archivo_procesado,
                "periodos": periodos,
                "entidad": entidad,
                "estado": estado,
                "observaciones": observaciones,
            }
        )

        if records:
            history_payload[ind_id] = {
                "entidad": entidad,
                "datos": records,
            }

    status_counts: dict[str, int] = {}
    for row in coverage_rows:
        key = row["estado_historico"]
        status_counts[key] = status_counts.get(key, 0) + 1

    summary = {
        "entidad": entidad,
        "totalIndicadores": len(frontend_indicators),
        "indicadoresConHistorico": sum(1 for ind in frontend_indicators if ind["tieneHistorico"]),
        "indicadoresSinHistorico": sum(1 for ind in frontend_indicators if not ind["tieneHistorico"]),
        "indicadoresConMeta2030": sum(1 for ind in frontend_indicators if ind["meta2030"] is not None),
        "porEstadoHistorico": status_counts,
        "periodosHistoricos": sorted(
            {point["anio"] for series in history_payload.values() for point in series["datos"]}
        ),
        "fechaActualizacion": date.today().isoformat(),
    }

    total_records = sum(len(series["datos"]) for series in history_payload.values())

    if not check_only:
        catalogo_salida.parent.mkdir(parents=True, exist_ok=True)
        subset_df.to_csv(catalogo_salida, index=False, encoding="utf-8-sig")

        cobertura_salida.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(coverage_rows).to_csv(cobertura_salida, index=False, encoding="utf-8-sig")

        _write_json(directorio_frontend / "indicadores_mvp.json", frontend_indicators)
        _write_json(directorio_frontend / "historicos_mvp.json", history_payload)
        _write_json(directorio_frontend / "fuentes_mvp.json", frontend_sources)
        _write_json(directorio_frontend / "resumen_mvp.json", summary)

    return {
        "extracted_sources": extracted_sources,
        "total_records": total_records,
        "summary": summary,
        "check_only": check_only,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--only", help="Extrae únicamente el id de fuente indicado.")
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Omite la extracción de fuentes crudas y solo regenera salidas desde hechos existentes.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Valida el manifiesto, archivos crudos y hechos sin escribir archivos de salida.",
    )
    args = parser.parse_args()

    try:
        result = run_pipeline(
            manifest_path=args.manifest,
            only_source=args.only,
            skip_extract=args.skip_extract,
            check_only=args.check,
        )
    except (FileNotFoundError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Error en ETL: {exc}") from exc

    summary = result["summary"]
    mode = "VALIDACIÓN (--check)" if result["check_only"] else "ETL COMPLETADO"
    print(f"[{mode}]")
    if result["extracted_sources"]:
        for fuente_id, count in result["extracted_sources"]:
            print(f"  - Extraído {fuente_id}: {count} registros")
    print(
        f"  - Total indicadores: {summary['totalIndicadores']} "
        f"(con serie histórica: {summary['indicadoresConHistorico']}, "
        f"en integración: {summary['indicadoresSinHistorico']})"
    )
    print(f"  - Registros históricos totales: {result['total_records']}")
    if not result["check_only"]:
        print(f"  - Fecha de actualización: {summary['fechaActualizacion']}")


if __name__ == "__main__":
    main()
