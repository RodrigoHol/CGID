"""Puebla el manifiesto unificado con los 148 indicadores del catálogo PVD sin sobrescribir configuraciones previas."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_MANIFEST = ROOT / "config" / "manifiesto_indicadores.json"

DOMAIN_MAP: list[tuple[tuple[str, ...], tuple[str, str, str, str]]] = [
    (("ceieg.veracruz.gob.mx",), ("ceieg_veracruz", "CEIEG Veracruz", "Comité Estatal de Información Estadística y Geográfica (CEIEG)", "http://ceieg.veracruz.gob.mx/")),
    (("inegi.org.mx",), ("inegi_pendientes", "INEGI", "Tabulados e indicadores INEGI (por clasificar)", "https://www.inegi.org.mx/")),
    (("sev.gob.mx",), ("sev_prontuario", "SEV", "Prontuario Estadístico SEV", "https://www.sev.gob.mx/v1/servicios/anuario-estadistico/")),
    (("planeacion.sep.gob.mx",), ("sep_pendientes", "SEP", "Estadísticas educativas SEP (por integrar)", "https://www.planeacion.sep.gob.mx/estadisticaeducativas.aspx")),
    (("transparenciapresupuestaria.gob.mx",), ("shcp_transparencia", "SHCP", "Transparencia Presupuestaria SHCP", "https://www.transparenciapresupuestaria.gob.mx/")),
    (("disciplinafinanciera.hacienda.gob.mx",), ("shcp_disciplina", "SHCP", "Disciplina Financiera y Sistema de Alertas SHCP", "https://www.disciplinafinanciera.hacienda.gob.mx/")),
    (("centromexico.digital",), ("centro_mexico_digital", "Centro México Digital", "Centro México Digital", "https://centromexico.digital/")),
    (("seinet.veracruz.mx", "veracruz.gob.mx"), ("gob_veracruz", "Gobierno del Estado de Veracruz", "Portales del Gobierno del Estado de Veracruz", "https://www.veracruz.gob.mx/")),
    (("nube.agricultura.gob.mx",), ("sader_agricultura", "SADER", "Secretaría de Agricultura y Desarrollo Rural (SADER)", "https://nube.agricultura.gob.mx/")),
    (("worldjusticeproject.mx", "index.worldjusticeproject.mx"), ("wjp_mexico", "World Justice Project", "Índice de Estado de Derecho en México (WJP)", "https://worldjusticeproject.mx/")),
    (("dgis.salud.gob.mx", "calidad.salud.gob.mx", "epidemiologia.salud.gob.mx", "sinaiscap.salud.gob.mx"), ("salud_federal", "Secretaría de Salud", "Sistema de Información en Salud (Secretaría de Salud)", "https://www.gob.mx/salud")),
    (("idd-mex.org",), ("idd_mex", "IDD-Mex", "Índice de Desarrollo Democrático de México", "https://idd-mex.org/")),
    (("culturaveracruz.gob.mx",), ("secver_cultural", "SECVER", "Registros e informes culturales SECVER", "https://culturaveracruz.gob.mx/")),
    (("sic.cultura.gob.mx",), ("cultura_sic", "Secretaría de Cultura", "Sistema de Información Cultural (SIC)", "https://sic.cultura.gob.mx/")),
    (("imco.org.mx",), ("imco", "IMCO", "Instituto Mexicano para la Competitividad (IMCO)", "https://imco.org.mx/")),
    (("datatur.sectur.gob.mx",), ("sectur_datatur", "SECTUR", "DataTur (Secretaría de Turismo)", "https://datatur.sectur.gob.mx/")),
    (("siesco.conavi.gob.mx",), ("conavi_siesco", "CONAVI", "Sistema de Información Estadística CONAVI", "https://siesco.conavi.gob.mx/")),
    (("indicedepazmexico.org",), ("ie_paz_mexico", "IEP", "Índice de Paz México", "https://www.indicedepazmexico.org/")),
    (("agenda2030.mx",), ("agenda2030_mx", "Agenda 2030 México", "Plataforma Agenda 2030 México", "https://agenda2030.mx/")),
    (("gob.mx",), ("gob_mx_federal", "Gobierno de México", "Portales del Gobierno de México (gob.mx)", "https://www.gob.mx/")),
]


def _extraer_primera_url(medio: str) -> str:
    match = re.search(r"https?://[^\s;|]+?(?=https?://|[\s;|]|$)", medio or "")
    if not match:
        return ""
    return match.group(0).rstrip(".,;)")


def _clasificar_fuente(medio: str, url: str) -> tuple[str, str, str, str]:
    texto = " ".join((medio or "").split())
    texto_low = texto.casefold()

    if url:
        host = urlparse(url).hostname or ""
        host = host.lower().removeprefix("www.")
        for dominios, info in DOMAIN_MAP:
            if host in dominios:
                return info
        if host.endswith(".salud.gob.mx"):
            return ("salud_federal", "Secretaría de Salud", "Sistema de Información en Salud (Secretaría de Salud)", "https://www.gob.mx/salud")
        if host.endswith(".veracruz.gob.mx"):
            return ("gob_veracruz", "Gobierno del Estado de Veracruz", "Portales del Gobierno del Estado de Veracruz", "https://www.veracruz.gob.mx/")

    if "sistema_de_alertas" in texto_low or "plina_financiera" in texto_low:
        return ("shcp_disciplina", "SHCP", "Disciplina Financiera y Sistema de Alertas SHCP", "https://www.disciplinafinanciera.hacienda.gob.mx/")
    if "siafev" in texto_low or "sefiplan" in texto_low:
        return ("sefiplan_siafev", "SEFIPLAN", "SIAFEV / SEFIPLAN Veracruz", "")
    if "sedema" in texto_low or "evaluación y regulación ambiental" in texto_low:
        return ("sedema_veracruz", "SEDEMA", "Secretaría de Medio Ambiente (SEDEMA)", "")
    if "siop" in texto_low or "construcción de obra" in texto_low:
        return ("siop_veracruz", "SIOP", "Secretaría de Infraestructura y Obras Públicas (SIOP)", "")
    if "stps" in texto_low:
        return ("stps_federal", "STPS", "Secretaría del Trabajo y Previsión Social (STPS)", "")
    if not texto or re.match(r"^(?:N/A|NA|N/D)\b", texto, re.IGNORECASE):
        return ("sin_fuente_definida", "Por definir", "Indicadores sin fuente o medio de verificación definido", "")
    return ("otra_fuente_veracruz", "Gobierno del Estado de Veracruz", "Fuentes estatales pendientes de enlace o registro", "")


def poblar_manifiesto(manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    """Agrega los indicadores faltantes de indicadores.csv al manifiesto respetando los existentes."""
    manifiesto = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalogo_rel = manifiesto.get("catalogo_maestro", "data/processed/catalogo/indicadores.csv")
    catalogo_path = Path(catalogo_rel) if Path(catalogo_rel).is_absolute() else ROOT / catalogo_rel
    catalog = pd.read_csv(catalogo_path, dtype=str, keep_default_na=False)

    fuentes: dict[str, dict[str, Any]] = manifiesto["fuentes"]
    indicadores: list[dict[str, Any]] = manifiesto["indicadores"]
    existentes = {item["id"] for item in indicadores}

    agregados = 0
    nuevas_fuentes = 0
    conteo_por_fuente: Counter[str] = Counter()

    for _, row in catalog.iterrows():
        clave = str(row["clave"]).strip()
        if clave in existentes:
            continue

        medio = str(row["medio_verificacion"]).strip()
        url = _extraer_primera_url(medio)
        fuente_id, institucion, nombre_fuente, default_url = _clasificar_fuente(medio, url)

        if fuente_id not in fuentes:
            fuentes[fuente_id] = {
                "institucion": institucion,
                "nombre": nombre_fuente,
                "url": default_url,
                "extractor": None,
                "archivo_crudo": "",
                "archivo_salida": "",
                "params": {},
            }
            nuevas_fuentes += 1

        if fuente_id == "sin_fuente_definida":
            obs = "Medio de verificación vacío o N/A; requiere revisión documental."
        elif url:
            obs = "Fuente identificada; pendiente de descarga y extracción."
        else:
            obs = "Fuente institucional sin URL directa; pendiente de gestión y extracción."

        indicadores.append(
            {
                "id": clave,
                "fuente_id": fuente_id,
                "url": url,
                "params": {},
                "observaciones": obs,
            }
        )
        existentes.add(clave)
        agregados += 1
        conteo_por_fuente[fuente_id] += 1

    manifest_path.write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "total_indicadores": len(indicadores),
        "agregados": agregados,
        "total_fuentes": len(fuentes),
        "nuevas_fuentes": nuevas_fuentes,
        "conteo_por_fuente": dict(conteo_por_fuente),
    }


def main() -> None:
    res = poblar_manifiesto()
    print(
        f"Manifiesto actualizado: {res['total_indicadores']} indicadores totales "
        f"(+{res['agregados']} nuevos), {res['total_fuentes']} fuentes "
        f"(+{res['nuevas_fuentes']} nuevas)."
    )
    if res["conteo_por_fuente"]:
        print("Nuevos indicadores agrupados por fuente:")
        for fuente_id, count in sorted(res["conteo_por_fuente"].items(), key=lambda x: -x[1]):
            print(f"  - {fuente_id}: {count}")


if __name__ == "__main__":
    main()
