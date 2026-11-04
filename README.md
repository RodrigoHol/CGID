# CGID

Catálogo y plataforma de consulta de indicadores del Plan Veracruzano de Desarrollo 2025-2030.

## Estructura

- `data/raw`: archivos originales sin modificar.
- `data/staging`: archivos intermedios que pueden regenerarse.
- `data/processed`: datos normalizados para consumo web, ETL o base de datos.
- `etl`: extracción, normalización y validación.
- `schemas`: esquema relacional previsto para la migración a una base de datos.
- `frontend/vue`: vista web actual y futura aplicación Vue.
- `frontend/looker`: espacio reservado para modelos y vistas de Looker.
- `config`: rutas y configuración de fuentes.
- `data/manifests`: procedencia y control de archivos descargados.

## Regenerar el catálogo

Desde la raíz del proyecto:

```powershell
.\venv\Scripts\python.exe etl\catalogo\extractor_catalogo.py
```

La salida se genera en:

```text
data/processed/catalogo/indicadores.csv
```

## Alcance del MVP

El alcance oficial de la entrega del 9 de noviembre está definido en
`config/mvp_indicadores.yml`. Para regenerar el subconjunto y la matriz de
cobertura:

```powershell
.\venv\Scripts\python.exe etl\catalogo\generar_mvp.py
```

Los resultados son:

- `data/processed/catalogo/mvp_indicadores.csv`: metadatos de los 15 indicadores.
- `data/manifests/mvp_indicadores.csv`: fuente, estado histórico y periodos.

Los estados de cobertura son `procesado`, `fuente_identificada` y
`pendiente_revision`. No se deben completar años faltantes con ceros o
estimaciones no documentadas.

## Ejecutar la vista web

Desde la raíz del proyecto:

```powershell
.\venv\Scripts\python.exe tools\servidor.py
```

Abrir:

<http://127.0.0.1:8000/frontend/vue/index.html>

Los históricos deberán almacenarse en formato largo en
`data/processed/historicos/hechos/valores_indicadores.csv`, conservando la
fuente, el periodo, la entidad, la URL y la procedencia del archivo original.

## Extraer históricos de pobreza

Los históricos de `IE001`, `IE002`, `IE014` e `IE015` se extraen de la hoja `Ver.` de
`pm_ef_2024.xlsx`:

```powershell
.\venv\Scripts\python.exe etl\historicos\extraer_historico_pobreza.py
```

La salida queda en:

```text
data/processed/historicos/hechos/historico_pobreza.csv
```

El archivo usa formato largo y contiene únicamente:
`id_indicador`, `anio` y `valor_real`, con cinco años por indicador. IE002 se
calcula como el complemento de la carencia por acceso a la seguridad social;
IE001, IE014 e IE015 se extraen directamente del bloque de porcentajes.

IE016 se procesa por separado desde el tabulador interactivo ENCIG, filtrando
exclusivamente `Veracruz de Ignacio de la Llave` y el servicio `Centros de
salud y hospitales del gobierno de su estado`. Su salida es
`data/processed/historicos/hechos/historico_ie016_encig.csv` y contiene los
periodos 2015, 2017, 2019, 2021, 2023 y 2025. El Excel `_est.xlsx` valida el
periodo 2023 y el archivo `_int.xlsx` se conserva como referencia de precisión;
ninguno sustituye la serie capturada del tabulador interactivo.

## Contrato de datos para Vue

Para generar los artefactos de consumo del frontend:

```powershell
.\venv\Scripts\python.exe etl\frontend\generar_datos_frontend.py
```

La salida queda en `data/processed/frontend/`:

- `indicadores_mvp.json`: las 15 fichas técnicas y su estado de cobertura.
- `historicos_mvp.json`: series disponibles, sin rellenar periodos faltantes.
- `fuentes_mvp.json`: procedencia y enlaces por indicador.
- `resumen_mvp.json`: métricas agregadas para el dashboard.

El contrato distingue `lineaBase` y `meta2030` de `historicos_mvp`; la línea
base del PVD no se trata como una observación histórica. Los indicadores sin
serie permanecen en `indicadores_mvp.json` con `tieneHistorico: false`.
