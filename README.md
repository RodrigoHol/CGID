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

## Extraer el primer histórico

El histórico del indicador `CGID-PVD25.30-ER1-O01-E00-IE001` se extrae de la
hoja `Ver.` de `pm_ef_2024.xlsx`:

```powershell
.\venv\Scripts\python.exe etl\historicos\extraer_historico_pobreza.py
```

La salida queda en:

```text
data/processed/historicos/hechos/historico_pobreza.csv
```

El archivo usa formato largo y contiene únicamente:
`id_indicador`, `anio` y `valor_real`. El valor corresponde al porcentaje de
población en situación de pobreza de Veracruz para los años publicados por
INEGI (2016, 2018, 2020, 2022 y 2024).
