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

## Ejecutar la aplicación web

La aplicación Vue 3 + TypeScript + Vite vive en `frontend/vue`. Para
instalar dependencias y abrir el entorno de desarrollo:

```powershell
Set-Location frontend/vue
npm install
npm run dev
```

Abrir la URL que muestre Vite (habitualmente
<http://127.0.0.1:5173/>). Para validar una compilación de producción:

## Publicar en GitHub Pages

El workflow `.github/workflows/deploy-pages.yml` publica automáticamente la
aplicación en GitHub Pages cada vez que se actualiza `main`. En la configuración
del repositorio, selecciona **Settings > Pages > Source: GitHub Actions**.

La aplicación usa `/CGID/` como base de producción y hash history para que las
rutas de indicadores funcionen al recargar la página. Las imágenes se importan
desde `frontend/vue/src/assets`, por lo que Vite ajusta sus URLs al publicar
bajo el subdirectorio del repositorio. Para validar una compilación de producción:

```powershell
npm run build
```

La aplicación consume los cuatro archivos del contrato en
`data/processed/frontend/` a través de `src/services/data.service.ts`. Esta
capa mantiene desacoplada la UI de la fuente de datos y podrá sustituirse por
una API sin reescribir los componentes.

El catálogo enlaza cada indicador con su detalle en
`/indicadores/:id`. El detalle presenta la serie histórica disponible, línea
base, meta 2030, último valor, variación observada, tabla de periodos y fuente
de procedencia. Los años que no están publicados por la fuente no se
interpolan.

## Servidor estático legado

Desde la raíz del proyecto:

```powershell
.\venv\Scripts\python.exe tools\servidor.py
```

Abrir la vista anterior en:

<http://127.0.0.1:8000/frontend/vue/index.html>

Este servidor se conserva para compatibilidad con el flujo anterior; el
desarrollo de la aplicación nueva debe hacerse con Vite.

Los históricos deberán almacenarse en formato largo en
`data/processed/historicos/hechos/valores_indicadores.csv`, conservando la
fuente, el periodo, la entidad, la URL y la procedencia del archivo original.

## Extraer históricos de pobreza

Los históricos de `IE001`, `IE002`, `IE014`, `IE015` e `IE025` se extraen de la hoja `Ver.` de
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
IE001, IE014, IE015 e IE025 se extraen directamente del bloque de porcentajes.
IE025 corresponde a la fila `Población con al menos tres carencias sociales`.

IE016 se procesa por separado desde el tabulador interactivo ENCIG, filtrando
exclusivamente `Veracruz de Ignacio de la Llave` y el servicio `Centros de
salud y hospitales del gobierno de su estado`. Su salida es
`data/processed/historicos/hechos/historico_ie016_encig.csv` y contiene los
periodos 2015, 2017, 2019, 2021, 2023 y 2025. El Excel `_est.xlsx` valida el
periodo 2023 y el archivo `_int.xlsx` se conserva como referencia de precisión;
ninguno sustituye la serie capturada del tabulador interactivo.

## Extraer históricos educativos SEP

`IE017`, `IE018` e `IE019` se extraen del libro XLSM de indicadores educativos
de la SEP:

```powershell
.\venv\Scripts\python.exe etl\historicos\extraer_historico_educacion_sep.py
```

El extractor lee las tablas base de las hojas `1` y `2`, sin depender de la
ejecución de macros. Filtra la entidad Veracruz (clave `33`) y conserva los
ciclos escolares 1990-1991 a 2025-2026; en el contrato histórico se representa
cada ciclo por su año inicial. IE017 usa la clave SEP `129` (cobertura básica),
IE018 la `133` (cobertura media superior) e IE019 la `224` (cobertura superior
sin posgrado). La salida es
`data/processed/historicos/hechos/historico_educacion_sep.csv`.

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
