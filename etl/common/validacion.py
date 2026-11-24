"""Validaciones del manifiesto unificado y de las series de hechos."""

from __future__ import annotations

import math
from typing import Any, Iterable

import pandas as pd


def validar_manifiesto(
    manifiesto: dict[str, Any],
    catalog_df: pd.DataFrame,
    extractores_disponibles: Iterable[str],
    extractores_remotos: Iterable[str] = (),
) -> None:
    """Verifica la estructura del manifiesto y su correspondencia con el catálogo maestro."""
    requeridas = {"version", "entidad", "fuentes", "indicadores"}
    faltantes = requeridas.difference(manifiesto)
    if faltantes:
        raise ValueError(f"Al manifiesto le faltan claves requeridas: {sorted(faltantes)}.")

    fuentes = manifiesto["fuentes"]
    indicadores = manifiesto["indicadores"]
    if not isinstance(fuentes, dict) or not fuentes:
        raise ValueError("La sección 'fuentes' del manifiesto debe ser un objeto no vacío.")
    if not isinstance(indicadores, list) or not indicadores:
        raise ValueError("La sección 'indicadores' del manifiesto debe ser una lista no vacía.")

    disponibles = set(extractores_disponibles)
    remotos = set(extractores_remotos)
    for fuente_id, cfg in fuentes.items():
        if not isinstance(cfg, dict):
            raise ValueError(f"La fuente '{fuente_id}' debe ser un objeto JSON.")
        if not str(cfg.get("institucion", "")).strip():
            raise ValueError(f"La fuente '{fuente_id}' debe definir 'institucion'.")
        extractor = cfg.get("extractor")
        if extractor is not None:
            if extractor not in disponibles:
                raise ValueError(
                    f"La fuente '{fuente_id}' referencia un extractor desconocido: '{extractor}'."
                )
            if extractor not in remotos and not str(cfg.get("archivo_crudo", "")).strip():
                raise ValueError(f"La fuente '{fuente_id}' requiere 'archivo_crudo'.")
            if not str(cfg.get("archivo_salida", "")).strip():
                raise ValueError(f"La fuente '{fuente_id}' requiere 'archivo_salida'.")

    if catalog_df["clave"].duplicated().any():
        raise ValueError("El catálogo maestro contiene claves duplicadas.")
    catalogo_ids = set(catalog_df["clave"].astype(str))

    vistos: set[str] = set()
    for item in indicadores:
        ind_id = str(item.get("id", "")).strip()
        fuente_id = str(item.get("fuente_id", "")).strip()
        if not ind_id:
            raise ValueError("Cada indicador en el manifiesto debe incluir 'id'.")
        if ind_id in vistos:
            raise ValueError(f"El indicador '{ind_id}' está duplicado en el manifiesto.")
        vistos.add(ind_id)
        if ind_id not in catalogo_ids:
            raise ValueError(
                f"El indicador '{ind_id}' no existe en el catálogo maestro."
            )
        if fuente_id not in fuentes:
            raise ValueError(
                f"El indicador '{ind_id}' referencia una fuente inexistente: '{fuente_id}'."
            )


def validar_hechos(records: list[dict[str, Any]], fuente_id: str) -> list[dict[str, Any]]:
    """Valida el contrato (id_indicador, anio, valor_real) y ordena la serie."""
    if not records:
        raise ValueError(f"La fuente '{fuente_id}' no generó ningún registro.")

    limpios: list[dict[str, Any]] = []
    claves_vistas: set[tuple[str, int]] = set()
    for record in records:
        if not {"id_indicador", "anio", "valor_real"}.issubset(record):
            raise ValueError(
                f"Registro incompleto en '{fuente_id}': se requieren id_indicador, anio y valor_real."
            )
        ind_id = str(record["id_indicador"]).strip()
        if not ind_id:
            raise ValueError(f"Registro con id_indicador vacío en '{fuente_id}'.")

        try:
            anio = int(record["anio"])
            valor = float(record["valor_real"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Año o valor inválido en '{fuente_id}' para '{ind_id}': {record!r}"
            ) from exc

        if not math.isfinite(valor):
            raise ValueError(
                f"Valor no finito en '{fuente_id}' para '{ind_id}', año {anio}: {valor!r}"
            )

        llave = (ind_id, anio)
        if llave in claves_vistas:
            raise ValueError(
                f"Registro duplicado en '{fuente_id}' para indicador '{ind_id}', año {anio}."
            )
        claves_vistas.add(llave)
        limpios.append({"id_indicador": ind_id, "anio": anio, "valor_real": valor})

    limpios.sort(key=lambda item: (item["id_indicador"], item["anio"]))
    return limpios
