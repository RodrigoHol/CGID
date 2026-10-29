"""Genera el subconjunto oficial y la matriz de cobertura del MVP."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "mvp_indicadores.yml"
CATALOG = ROOT / "data" / "processed" / "catalogo" / "indicadores.csv"
MVP_OUTPUT = ROOT / "data" / "processed" / "catalogo" / "mvp_indicadores.csv"
COVERAGE_OUTPUT = ROOT / "data" / "manifests" / "mvp_indicadores.csv"
HISTORIC_ID = "CGID-PVD25.30-ER1-O01-E00-IE001"
HISTORIC_IDS = {
    "CGID-PVD25.30-ER1-O01-E00-IE001",
    "CGID-PVD25.30-ER1-O01-E00-IE002",
}
HISTORIC_FILE = (
    "data/processed/historicos/hechos/historico_pobreza.csv"
)
RAW_FILE = (
    "data/raw/fuentes/inegi/pobreza_multidimensional/2024/pm_ef_2024.xlsx"
)
PERIODS = "2016,2018,2020,2022,2024"


def load_ids(path: Path) -> list[str]:
    """Lee las claves de la sección indicadores sin requerir PyYAML."""
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*-\s+(\S+)\s*$", line)
        if match:
            ids.append(match.group(1))
    if not ids:
        raise ValueError(f"No se encontraron indicadores en {path}.")
    if len(ids) != len(set(ids)):
        raise ValueError("La configuración del MVP contiene claves duplicadas.")
    return ids


def source_url(value: str) -> str:
    urls = re.findall(r"https?://.*?(?=https?://|$)", value or "")
    cleaned = []
    for url in urls:
        url = url.rstrip(".,;)")
        if url not in cleaned:
            cleaned.append(url)
    return " | ".join(cleaned)


def build_coverage(catalog: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    rows = []
    for indicator_id in ids:
        row = catalog[catalog["clave"] == indicator_id]
        if len(row) != 1:
            raise ValueError(
                f"La clave '{indicator_id}' debe existir exactamente una vez "
                f"en el catálogo maestro; coincidencias: {len(row)}."
            )
        item = row.iloc[0]
        if indicator_id in HISTORIC_IDS:
            status = "procesado"
            raw_file = RAW_FILE
            periods = PERIODS
            processed_file = HISTORIC_FILE
            observations = (
                "Histórico estatal de Veracruz extraído de la hoja Ver.; "
                "IE002 se calculó como 100 menos la carencia por acceso a la "
                "seguridad social."
                if indicator_id.endswith("IE002")
                else "Histórico estatal de Veracruz extraído de la hoja Ver."
            )
        elif item["medio_verificacion"].strip():
            status = "fuente_identificada"
            raw_file = ""
            periods = ""
            processed_file = ""
            observations = "Fuente identificada; pendiente de descarga y extracción."
        else:
            status = "pendiente_revision"
            raw_file = ""
            periods = ""
            processed_file = ""
            observations = "Medio de verificación vacío; requiere revisión documental."
        rows.append(
            {
                "id_indicador": indicator_id,
                "nombre": " ".join(str(item["nombre"]).split()),
                "fuente_verificacion": " ".join(
                    str(item["medio_verificacion"]).split()
                ),
                "url_fuente": source_url(item["medio_verificacion"]),
                "estado_historico": status,
                "archivo_crudo": raw_file,
                "archivo_procesado": processed_file,
                "periodos_disponibles": periods,
                "entidad": "Veracruz",
                "observaciones": observations,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    ids = load_ids(CONFIG)
    catalog = pd.read_csv(CATALOG, dtype=str, keep_default_na=False)
    selected = catalog[catalog["clave"].isin(ids)].copy()
    if len(selected) != len(ids):
        raise ValueError(
            f"El subconjunto contiene {len(selected)} filas; se esperaban {len(ids)}."
        )
    selected["clave"] = pd.Categorical(selected["clave"], categories=ids, ordered=True)
    selected = selected.sort_values("clave").copy()
    selected["clave"] = selected["clave"].astype(str)

    MVP_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(MVP_OUTPUT, index=False, encoding="utf-8-sig")

    coverage = build_coverage(catalog, ids)
    coverage.to_csv(COVERAGE_OUTPUT, index=False, encoding="utf-8-sig")
    print(f"Subconjunto generado: {MVP_OUTPUT} ({len(selected)} indicadores)")
    print(f"Matriz generada: {COVERAGE_OUTPUT} ({len(coverage)} indicadores)")


if __name__ == "__main__":
    main()
