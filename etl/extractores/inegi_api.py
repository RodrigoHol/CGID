"""Extractor para la API v2.0 del Banco de Indicadores del INEGI (BISE / BIE)."""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _cargar_token(root: Path) -> str:
    env_token = os.environ.get("INEGI_API_TOKEN", "").strip()
    if env_token:
        return env_token

    for base in (root, Path(__file__).resolve().parents[2]):
        env_path = base / ".env"
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "INEGI_API_TOKEN":
                token = value.strip().strip('"').strip("'")
                if token:
                    return token

    raise RuntimeError("Falta la variable INEGI_API_TOKEN en el entorno o en .env.")


def _enmascarar_token(texto: str, token: str) -> str:
    return texto.replace(token, "***") if token else texto


def _consultar_serie(
    serie_id: str,
    area_geo: str,
    banco: str,
    idioma: str,
    token: str,
    timeout: float,
) -> dict[str, Any]:
    url = (
        "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/"
        f"INDICATOR/{serie_id}/{idioma}/{area_geo}/false/{banco}/2.0/{token}?type=json"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "CGID-Veracruz-ETL/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        msg = _enmascarar_token(f"HTTP {exc.code} al consultar serie {serie_id}: {exc.reason}", token)
        raise RuntimeError(msg) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        msg = _enmascarar_token(f"Error de red al consultar serie {serie_id}: {exc}", token)
        raise RuntimeError(msg) from None

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Respuesta JSON inválida de INEGI para serie {serie_id}: {exc}") from None


def extraer(
    input_path: Path,
    source_cfg: dict[str, Any],
    indicators: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Descarga series históricas desde la API v2.0 del INEGI según el manifiesto."""
    token = _cargar_token(input_path)
    source_params = source_cfg.get("params", {})
    default_area = str(source_params.get("area_geo", "30"))
    default_banco = str(source_params.get("banco", "BISE"))
    idioma = str(source_params.get("idioma", "es"))
    timeout = float(source_params.get("timeout", 20))
    delay_s = float(source_params.get("delay_s", 0.2))

    records: list[dict[str, Any]] = []
    for idx, ind in enumerate(indicators):
        ind_params = ind.get("params", {})
        serie_id = str(ind_params.get("serie_id", "")).strip()
        if not serie_id:
            raise ValueError(f"El indicador '{ind['id']}' requiere params.serie_id.")

        area_geo = str(ind_params.get("area_geo", default_area))
        banco = str(ind_params.get("banco", default_banco))
        agregacion = str(ind_params.get("agregacion", "ultimo")).strip().lower()
        complement = bool(ind_params.get("complement", False))
        escala = ind_params.get("escala")
        min_year = ind_params.get("min_year")

        payload = _consultar_serie(serie_id, area_geo, banco, idioma, token, timeout)
        series_list = payload.get("Series") or []
        if not series_list:
            raise ValueError(
                f"La API del INEGI no devolvió series para '{ind['id']}' (serie {serie_id}, área {area_geo})."
            )

        observations = series_list[0].get("OBSERVATIONS") or []
        por_anio: dict[int, list[tuple[str, float]]] = {}
        for obs in observations:
            raw_val = obs.get("OBS_VALUE")
            if raw_val is None:
                continue
            val_str = str(raw_val).strip()
            if not val_str or val_str.lower() in {"nan", "null", "n/a", "nd"}:
                continue
            try:
                numeric = float(val_str)
            except ValueError:
                continue

            period = str(obs.get("TIME_PERIOD", "")).strip()
            match = re.match(r"^(\d{4})", period)
            if not match:
                continue
            year = int(match.group(1))
            if min_year is not None and year < int(min_year):
                continue
            por_anio.setdefault(year, []).append((period, numeric))

        if not por_anio:
            raise ValueError(
                f"La serie {serie_id} ({ind['id']}) no contiene observaciones numéricas válidas."
            )

        for year in sorted(por_anio):
            items = sorted(por_anio[year], key=lambda item: item[0])
            if agregacion == "promedio":
                valor = sum(v for _, v in items) / len(items)
            else:
                valor = items[-1][1]

            if escala is not None:
                valor *= float(escala)
            if complement:
                valor = 100.0 - valor

            records.append(
                {
                    "id_indicador": ind["id"],
                    "anio": year,
                    "valor_real": float(valor),
                }
            )

        if delay_s > 0 and idx < len(indicators) - 1:
            time.sleep(delay_s)

    return records
