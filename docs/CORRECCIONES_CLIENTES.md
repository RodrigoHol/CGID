# Plan de Correcciones y Evolución — Observaciones de Clientes (CGID)

Documento de trabajo que traduce las notas levantadas en sesión con los clientes en un **backlog puntual, priorizado y clasificado por complejidad técnica y dependencia de datos**.

> **Objetivo central de negocio:** que personas del área de **economía, finanzas y planeación** comprendan en segundos el estado real de cada indicador del Plan Veracruzano de Desarrollo (PVD) 2025–2030: dónde partió el sexenio, dónde está hoy, cuánto falta para la meta, quién es responsable y cómo se compara Veracruz frente al país.

---

## 1. Diagnóstico de partida (estado real del proyecto)

Con base en la auditoría directa de `data/processed/frontend/indicadores_mvp.json`, `etl/catalogo/extractor_catalogo.py` y `config/manifiesto_indicadores.json`:

| Métrica del catálogo actual | Valor observado | Implicación directa para las correcciones |
| :--- | :---: | :--- |
| Indicadores totales en el catálogo PVD | **148** | Base completa para resumen, filtros y asignación institucional. |
| Indicadores con serie histórica integrada (`tieneHistorico`) | **46** | Los 102 restantes requieren extracción/documentación o vista clara de estado pendiente. |
| Indicadores con dato observado en **2024** | **32** | Para los otros indicadores habrá que mostrar línea base cercana a 2024/2025 o señalar el rezago de publicación. |
| Indicadores sin fórmula (`formula: ""`) | **30** | Requiere explicación legible automática en UI + recuperación documental en catálogo. |
| Indicadores sin unidad de medida (`unidadMedida: ""`) | **123** | Limita la lectura financiera si no se rescata o infiere desde el PDF/ficha. |
| Hallazgo en `etl/catalogo/extractor_catalogo.py` | `Fecha de publicación` y `metas_intermedias_json` | El extractor ya corta en `Fecha de publicación`, pero aún no extrae periodicidad/fechas ni responsables; además, `metas_intermedias_json` presenta artefactos de parseo (ej. `"2024": 2027.0`) que deben limpiarse antes de calcular rezagos contra metas intermedias. |
| Potencial de comparativos en `data/raw/` | INEGI Pobreza, SEP, API BISE | Las fuentes crudas (`pm_ef_2024.xlsx`, `reporte_indicadores_educativos_sep_2026.xlsm` y API BISE) contienen datos nacionales y por entidad federativa para habilitar el piloto estatal vs. nacional y el ranking. |

---

## 2. Matriz Maestra Priorizada (Orden de ejecución)

Criterio de priorización:
- **P1 — Impacto inmediato / Baja complejidad:** Cambios principalmente de interfaz y cálculos directos en frontend sobre datos ya existentes.
- **P2 — Seguimiento sexenal y Resumen Ejecutivo / Complejidad Media:** Requiere depuración de datos (`metas_intermedias_json`), nuevas métricas derivadas de avance/rezago y rediseño del Dashboard principal y vistas agrupadas.
- **P3 — Metadatos institucionales y calendario / Complejidad Media-Alta:** Exige extender el esquema JSON/CSV, mejorar `extractor_catalogo.py` y recabar insumos oficiales de secretarías/encargados.
- **P4 — Analítica predictiva y comparativos nacionales/municipales / Complejidad Alta:** Requiere modelos de proyección transparentes, ingesta de series nacionales (32 entidades) y series municipales/regionales (212 municipios).

| ID | Corrección solicitada (nota del cliente) | Prioridad | Complejidad | Capas impactadas | Dependencias |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **C01** | Bajar la gráfica en la vista de cada indicador; mostrar primero el contexto | **P1** | Baja | Frontend | Ninguna |
| **C02** | Describir cada concepto con el ícono de `?` | **P1** | Baja | Frontend | Ninguna |
| **C03** | Explicar Línea Base y explicar Fórmula cuando no exista | **P1** | Baja | Frontend / Catálogo | Ninguna (UI) / Revisión PDF |
| **C04** | En Variación observada, permitir seleccionar el año base de comparación | **P1** | Baja | Frontend | Ninguna |
| **C05** | Mostrar porcentaje de avance hacia la meta y tiempo restante | **P1** | Baja–Media | Frontend | Regla de cálculo unificada |
| **C06** | Incluir interpretación ejecutiva de cada gráfica | **P1** | Baja–Media | Frontend | Ninguna |
| **C07** | Mostrar en todos los indicadores cómo inició el sexenio (2024), cómo va hoy y la meta | **P2** | Media | Frontend / ETL | Depuración línea base / 2024 |
| **C08** | Identificar indicadores prioritarios según el atraso/rezago | **P2** | Media | ETL / Frontend | Limpiar `metas_intermedias_json` y definir criterio de atraso |
| **C09** | Hoja de Resumen en el Dashboard principal (cuántos, cómo van, más atrasados y su secretaría) | **P2** | Media | Frontend | C08 y C12 (al menos Secretaría) |
| **C10** | Presentar indicadores por Ejes, por Secretaría y General + apartado claro de filtros | **P2** | Media | Frontend / Datos | C12 (campo Secretaría) |
| **C11** | Periodicidad en Último Valor + Mes de última publicación y fecha de siguiente publicación | **P3** | Media–Alta | ETL / Esquema / Frontend | Re-extracción PDF + calendario oficial |
| **C12** | Secretaría, Subsecretaría, Departamento/Área y Nombre del encargado responsable | **P3** | Media–Alta | Esquema / ETL / Gestión Cliente / Frontend | Matriz oficial de responsables del cliente |
| **C13** | Lista de indicadores que requieren investigación por Secretaría (brechas de datos/ficha) | **P3** | Media | ETL / Gestión Cliente / Frontend | C12 y auditoría automática |
| **C14** | Proyección de tendencia actual, peor de los casos y mejor de los casos al 2030 | **P4** | Alta | Frontend / Metodología | Validación metodológica del modelo de escenarios |
| **C15** | Cruce con gráfica nacional (al menos 3 indicadores estatal vs. nacional) | **P4** | Alta | ETL / Esquema / Frontend | Selección de 3+ indicadores piloto |
| **C16** | Ranking nacional (arriba o abajo de la media nacional) | **P4** | Alta | ETL / Esquema / Frontend | C15 (datos de las 32 entidades y media) |
| **C17** | Inclusión por municipio o región de Veracruz en el comparativo | **P4** | Alta | ETL / Esquema / Frontend | Disponibilidad municipal/regional en fuentes oficiales |

---

## 3. Detalle puntual de cada corrección

### Prioridad P1 — Quick Wins de comprensión y experiencia (Frontend inmediato)

#### C01 · Bajar la gráfica en la vista de indicador y priorizar el contexto
- **Nota original:** *"En la vista de cada indicador Bajar la gráfica, primero tener el contexto"*
- **Qué debe cambiar:** Reordenar `IndicatorDetailView.vue` para que el usuario financiero lea en este orden natural:
  1. **Contexto del indicador:** nombre, descripción clara, eje rector, secretaría responsable y qué mide exactamente.
  2. **Resumen ejecutivo / trayectoria sexenal:** 2024 → Actual → Meta 2030, % de avance, semáforo y tiempo restante.
  3. **Ficha técnica e interpretación** (sentido, fórmula/explicación, unidad, línea base).
  4. **Gráfica histórica + interpretación textual** (debajo del contexto).
  5. **Tabla de observaciones por año y fuente oficial.**
- **Archivos:** `frontend/vue/src/views/IndicatorDetailView.vue`, `frontend/vue/src/styles/main.css`.

#### C02 · Cambiar íconos de ayuda a `?` y describir cada concepto
- **Nota original:** *"Describir cada concepto con el icono de ?"*
- **Qué debe cambiar:**
  - Sustituir el ícono `info` (`i`) en botones/pistas de glosario por `help` (`?` dentro de círculo) para que sea visualmente obvio dónde consultar una definición.
  - Ampliar `src/utils/glossary.ts` para cubrir **todos** los conceptos presentes en pantalla: *Línea base*, *Meta 2030*, *Último valor*, *Periodicidad*, *Última y próxima publicación*, *Variación observada*, *Porcentaje de avance*, *Sentido (Ascendente/Descendente/Regular)*, *Eje rector*, *Brecha/Atraso*, *Media nacional* y *Semáforo*.
  - Hacer que los `?` funcionen tanto con hover como con **clic/tap** (Popover o Dialog ligero en móvil, no solo tooltip).
- **Archivos:** `frontend/vue/src/utils/glossary.ts`, `frontend/vue/src/views/IndicatorDetailView.vue`, `frontend/vue/src/views/DashboardView.vue`, `frontend/vue/src/views/IndicatorsView.vue`.

#### C03 · Explicar Línea Base y explicar Fórmula cuando falte
- **Nota original:** *"Fórmula sino tiene explicada"*, *"Explicar línea base"*
- **Qué debe cambiar:**
  - **Fórmula:** Actualmente **30 de 148 indicadores** tienen `formula: ""`. Cuando esté vacía, mostrar una explicación amigable en lenguaje natural (ej. *"Cálculo directo reportado por la fuente oficial (ver descripción y método de verificación)"* o derivar una lectura en lenguaje llano de qué numerador/denominador compara), nunca un frío `"No especificada"`. Complementariamente, revisar en el PDF si esos 30 casos tienen método de cálculo en la sección `IV. Datos de las variables`.
  - **Línea base:** Añadir debajo o dentro de la tarjeta de Línea Base una explicación breve y contextual (ej. *"Punto de partida oficial del PVD en {año}: {valor}"*), explicando si se mide previo o al inicio del sexenio.
- **Archivos:** `frontend/vue/src/views/IndicatorDetailView.vue`, `frontend/vue/src/utils/glossary.ts`, `etl/catalogo/extractor_catalogo.py`.

#### C04 · Selector de año base en Variación observada
- **Nota original:** *"Variación observada seleccionar base"*
- **Qué debe cambiar:** En la tarjeta/bloque de *Variación observada* dentro de `IndicatorDetailView.vue`, incluir un selector desplegable (`Select` de PrimeVue) que permita elegir **contra qué periodo comparar el último valor** (por defecto: *Línea base PVD* o *Inicio de sexenio 2024*, con opción de elegir cualquier año disponible en la serie histórica, p. ej. `2016`, `2018`, `2020`, `2022`, `2024`). Recalcular en tiempo real la diferencia absoluta/en pp y el semáforo *Favorable / Desfavorable*.
- **Archivos:** `frontend/vue/src/views/IndicatorDetailView.vue`.

#### C05 · Porcentaje de avance en cada indicador y tiempo restante para la meta
- **Nota original:** *"Porcentaje de avance que se tiene en casa [cada] indicador y cuánto tiempo queda para llegar a la meta"*
- **Qué debe cambiar:**
  - Calcular e indicar claramente:
    - **% de avance hacia la Meta 2030:** `(Valor actual - Línea base) / (Meta 2030 - Línea base) * 100` (acotado visualmente y respetando el sentido ascendente/descendente; si retrocedió respecto a la línea base, mostrar `0 % de avance · retroceso de X` en rojo).
    - **Tiempo restante:** años/meses faltantes hasta el cierre de la meta sexenal (`2030`), e indicar si el indicador aún no tiene datos posteriores a la línea base para calcular avance.
- **Archivos:** Nueva utilidad `frontend/vue/src/utils/calculations.ts`, `frontend/vue/src/views/IndicatorDetailView.vue`, `frontend/vue/src/views/IndicatorsView.vue`.

#### C06 · Interpretación automática de cada gráfica
- **Nota original:** *"Meter interpretación de cada gráfica de los indicadores"*
- **Qué debe cambiar:** Debajo del título o pie de cada gráfica en `HistoricalChart.vue` y en las gráficas del `DashboardView.vue`, generar un bloque corto en lenguaje ejecutivo (máximo 2–3 líneas) que resuma:
  - Dirección reciente (*mejoró / empeoró / se mantuvo estable* entre el primer y último año),
  - Distancia actual respecto a la Meta 2030 (ej. *"Para alcanzar la meta de 41.5 % en 2030, Veracruz necesita reducir 3.0 puntos porcentuales adicionales en los próximos 4 años"*).
- **Archivos:** `frontend/vue/src/components/indicators/HistoricalChart.vue`, `frontend/vue/src/utils/calculations.ts`.

---

### Prioridad P2 — Trayectoria Sexenal, Rezago y Resumen Ejecutivo (ETL + Frontend)

#### C07 · Trayectoria del sexenio en todos los indicadores (2024 → Actual → Meta)
- **Nota original:** *"En todos los indicadores hay que resolver como se puede ver cómo lo agarro el sexenio apartir de 2024 y como va ahorita y la meta"*
- **Qué debe cambiar:**
  - Mostrar una **línea de tiempo / comparativa de 3 hitos** en cada indicador (y en columna/tarjeta del catálogo):
    1. **Inicio de sexenio (2024):** valor observado en 2024 (disponible hoy en 32 indicadores) o, si la fuente publica con rezago/otro ciclo, mostrar explícitamente la **Línea base PVD** indicando el año exacto de referencia (p. ej. `2023` o `2025`) para no inventar ni ocultar el dato.
    2. **Situación actual:** último dato disponible y su año/mes.
    3. **Meta sexenal 2030:** objetivo oficial del PVD.
  - En los 102 indicadores sin serie histórica aún, mostrar explícitamente Línea base y Meta 2030 con el estado del semáforo (*En integración* / *En revisión*) para que los 148 indicadores cumplan la vista comparativa.
- **Archivos:** `frontend/vue/src/views/IndicatorDetailView.vue`, `frontend/vue/src/views/IndicatorsView.vue`.

#### C08 · Identificar indicadores prioritarios según el atraso (y depurar metas intermedias)
- **Nota original:** *"Cuáles son los indicadores prioritarios según el atraso que se tiene"*
- **Qué debe cambiar:**
  1. **Limpieza en ETL:** Corregir el parseo de `metas_intermedias_json` en `etl/catalogo/extractor_catalogo.py` (actualmente captura años de calendario como `"2024": 2027.0` en lugar de valores numéricos de meta por año).
  2. **Regla de cálculo de atraso / prioridad:** Definir una fórmula transparente y validada con el cliente (por ejemplo: comparar `% de avance real` vs. `% de tiempo transcurrido del sexenio` + sentido desfavorable), clasificando cada indicador en:
     - **Prioridad Alta / Con atraso** (rojo: retroceso respecto a 2024/línea base o rezago significativo respecto a la trayectoria esperada a 2030),
     - **En seguimiento / Moderado** (ámbar),
     - **En meta / Favorable** (verde),
     - **Sin serie para evaluar** (pendiente de datos).
- **Archivos:** `etl/catalogo/extractor_catalogo.py`, `etl/frontend/generar_datos_frontend.py`, `frontend/vue/src/utils/calculations.ts`.

#### C09 · Hoja de Resumen Ejecutivo en el Dashboard principal
- **Nota original:** *"Hacer una hoja de resumen. Cuántos indicadores, cómo van, cuáles son los indicadores más atrasados y de que secretaria pertenecen. Eso deberia ir en el dashboard principal"*
- **Qué debe cambiar:** Reestructurar la parte superior/central de `DashboardView.vue` para que funcione como una verdadera **Hoja de Resumen Ejecutivo**:
  - **Cuántos indicadores son:** total (`148`), con serie histórica (`46`), sin serie (`102`), y con meta 2030 (`144`).
  - **Cómo van (desempeño):** conteo por desempeño (*En meta / favorable*, *Con atraso / prioritarios*, *Sin serie aún*).
  - **Top de indicadores más atrasados (prioritarios):** tabla/lista accionable con nombre, % de avance/atraso, último valor vs. meta y **Secretaría responsable**, con clic directo a su ficha.
  - **Resumen por Secretaría:** gráfica o tabla compacta de avance y rezagos por dependencia.
- **Archivos:** `frontend/vue/src/views/DashboardView.vue`.

#### C10 · Presentar indicadores por Ejes, por Secretaría y General + Apartado de filtros
- **Nota original:** *"Presentar los indicadores por ejes, por secretaria y general"*, *"Apartado para aplicar filtros"*
- **Qué debe cambiar:**
  - En `IndicatorsView.vue`, incorporar un **selector de vista / agrupación** en la parte superior:
    - **Vista General** (tabla completa actual con paginación).
    - **Por Eje Rector** (acordeón o secciones agrupadas por los 6 ejes con mini-resumen de avance por eje).
    - **Por Secretaría** (agrupación por dependencia responsable con conteo de indicadores y atrasos).
  - Separar visualmente un **panel dedicado de filtros** (búsqueda, Eje rector, Secretaría, Semáforo de disponibilidad, Nivel de atraso/prioridad, Periodicidad) con chips removibles y resumen de resultados.
- **Archivos:** `frontend/vue/src/views/IndicatorsView.vue`, `frontend/vue/src/styles/main.css`.

---

### Prioridad P3 — Metadatos Institucionales, Periodicidad y Lista de Investigación (ETL + Insumos + Frontend)

#### C11 · Periodicidad, mes de última publicación y próxima publicación
- **Nota original:** *"Último valor -- poner la periodisidad"*, *"Última publicación poner también el mes y cuando se publica el siguente"*
- **Qué debe cambiar:**
  - Extender el contrato de datos (`schemas/catalogo.sql`, `frontend/vue/src/types/contract.ts` y `etl/frontend/generar_datos_frontend.py`) con:
    - `periodicidad` (Anual, Bienal, Trimestral, Mensual, Sexenal).
    - `ultimaPublicacion` (`anio`, `mes`, etiqueta legible ej. *"Agosto 2025"*).
    - `proximaPublicacion` (`anio`, `mes`, o ventana estimada ej. *"Julio–Agosto 2026"*).
  - Revisar si el bloque `Fecha de publicación` del PDF (`Indicadores_PVD_Catalogo.pdf`) ya contiene periodicidad/fechas para extraerlo en `etl/catalogo/extractor_catalogo.py` y complementarlo con reglas por fuente (INEGI ENIGH/Pobreza bienal, SEP ciclo escolar anual, ENCIG bienal, etc.).
  - Mostrar la **periodicidad** directamente en la tarjeta de *Último valor* y un bloque claro de **Calendario de actualización** en el detalle.
- **Archivos:** `etl/catalogo/extractor_catalogo.py`, `config/manifiesto_indicadores.json`, `etl/frontend/generar_datos_frontend.py`, `frontend/vue/src/types/contract.ts`, `frontend/vue/src/views/IndicatorDetailView.vue`.

#### C12 · Secretaría, Subsecretaría, Departamento/Área y Nombre del Encargado
- **Nota original:** *"Agregar de que secretaria y de que área es responsable cada indicador,Nombre del encargado"*, *"De que secretaria, sub secretaria y que departamento"*
- **Qué debe cambiar:**
  - Agregar al modelo de datos de cada indicador un objeto `responsable`:
    ```json
    "responsable": {
      "secretaria": "",
      "subsecretaria": "",
      "departamento": "",
      "area": "",
      "encargado": ""
    }
    ```
  - Verificar primero si las fichas del PDF PVD incluyen dependencia/unidad administrativa responsable y extraerlo automáticamente en `extractor_catalogo.py`; cruzar con un archivo maestro editable (ej. `config/responsables_indicadores.csv`) para capturar **Subsecretaría, Departamento y Nombre del encargado** que no vengan en el PDF.
  - Mostrar esta ficha de responsabilidad tanto en `IndicatorDetailView.vue` como en los filtros y tarjetas de `IndicatorsView.vue` y `DashboardView.vue`.
- **Archivos:** `schemas/catalogo.sql`, `etl/catalogo/extractor_catalogo.py`, `config/responsables_indicadores.csv` (nuevo), `etl/frontend/generar_datos_frontend.py`, `frontend/vue/src/types/contract.ts`.

#### C13 · Lista de indicadores que requieren investigación por Secretaría
- **Nota original:** *"Hacer una lista de cuales necesitamos secretaria de investigación"*
- **Qué debe cambiar:**
  - Generar automáticamente desde el ETL un reporte/pantalla de **Brechas e Investigación Pendiente** agrupado por Secretaría, listando exactamente qué le falta a cada indicador:
    - Sin serie histórica (**102** actualmente) o sin dato 2024,
    - Sin fórmula (**30** actualmente),
    - Sin unidad de medida (**123** actualmente),
    - Sin periodicidad / fecha de próxima publicación,
    - Sin subsecretaría / departamento / encargado asignado.
  - Exponerlo en una pestaña o sección exportable a Excel (CSV) dentro de `SourcesView.vue` (o subvista `/fuentes` / `/investigacion`) para que el equipo gestione directamente los oficios o solicitudes con cada Secretaría.
- **Archivos:** `etl/frontend/generar_datos_frontend.py`, `frontend/vue/src/views/SourcesView.vue`, `data/processed/exports/` (exportable CSV/Excel).

---

### Prioridad P4 — Proyecciones y Comparativos Nacionales / Municipales (Alta complejidad)

#### C14 · Proyección de tendencia actual, peor de los casos y mejor de los casos
- **Nota original:** *"Hacer prediccion de la tendencia actual, el peor de los casos y el mejor de los casos"*
- **Qué debe cambiar:**
  - Implementar un módulo estadístico transparente (con mínimo `3` observaciones históricas para evitar extrapolaciones engañosas) que calcule hacia **2030**:
    - **Tendencia actual (escenario base):** regresión lineal o tasa media anual observada proyectada a 2030.
    - **Mejor de los casos:** banda optimista (ej. percentil superior / intervalo de confianza o ritmo de mejora histórica máxima).
    - **Peor de los casos:** banda pesimista / estancamiento o ritmo de deterioro histórico.
  - Graficar en `HistoricalChart.vue` con líneas punteadas diferenciadas de los datos reales observados y un **aviso metodológico visible** aclarando que son proyecciones estadísticas ilustrativas (respetando la regla del proyecto de no mezclar estimaciones con datos oficiales publicados).
- **Archivos:** `frontend/vue/src/utils/projections.ts` (nuevo) o cálculo en `etl/`, `frontend/vue/src/components/indicators/HistoricalChart.vue`.

#### C15 · Cruce con gráfica nacional (al menos 3 indicadores estatal vs. nacional)
- **Nota original:** *"Hacer el cruce con la gráfica nacional. Al menos 3 indicadores que se puedan comparar indicadores estatales vs nacional e inclusión por munición [municipio] o región"*
- **Qué debe cambiar:**
  - Extender el esquema de `historicos` (`schemas/historicos.sql`, `etl/extractores/`, `historicos_mvp.json`) para almacenar múltiples ámbitos geográficos (`Veracruz`, `Nacional`, `Entidades`, `Municipios`/`Regiones`) en lugar de asumir una sola serie plana por indicador.
  - Seleccionar e integrar **al menos 3 indicadores piloto** con datos oficiales estatales y nacionales ya disponibles en `data/raw/` (candidatos inmediatos: `IE001` Pobreza multidimensional INEGI, `IE014` Pobreza extrema INEGI, e indicadores educativos de `reporte_indicadores_educativos_sep_2026.xlsm` o API BISE INEGI).
  - En `HistoricalChart.vue`, añadir selector/toggle para superponer la curva **Nacional** frente a **Veracruz**.
- **Archivos:** `schemas/historicos.sql`, `etl/extractores/*`, `etl/frontend/generar_datos_frontend.py`, `frontend/vue/src/types/contract.ts`, `frontend/vue/src/components/indicators/HistoricalChart.vue`.

#### C16 · Ranking a nivel nacional (arriba o abajo de la media nacional)
- **Nota original:** *"Ranking a nivel nacional. Por arriba o por abajo de la media nocional [nacional]"*
- **Qué debe cambiar:**
  - Para los indicadores con cobertura de las **32 entidades federativas**, calcular y guardar en el payload del frontend:
    - Posición de Veracruz en el **ranking nacional (`1` a `32`)** considerando el `sentido` del indicador (*1° = mejor desempeño* o aclarando explícitamente el orden),
    - Valor de la **media nacional**,
    - Diferencia respecto a la media y etiqueta semafórica clara: **“Por arriba de la media nacional (Favorable / Desfavorable)”** o **“Por abajo de la media nacional”**.
  - Mostrar en el detalle del indicador una tarjeta de posicionamiento nacional y gráfica comparativa de barras por entidad o top/bottom + media.
- **Archivos:** `etl/extractores/*`, `etl/frontend/generar_datos_frontend.py`, `frontend/vue/src/views/IndicatorDetailView.vue`.

#### C17 · Desglose por municipio o región de Veracruz
- **Nota original:** *"...e inclusión por munición [municipio] o región"*
- **Qué debe cambiar:**
  - Identificar en qué indicadores existen datos oficiales desagregados a nivel municipal (212 municipios de Veracruz, ej. pobreza municipal CONEVAL/INEGI o estadística educativa SEP por municipio) o por las **10 regiones de Veracruz** (Huasteca Alta, Huasteca Baja, Totonaca, Nautla, Capital, Sotavento, Las Montañas, Papaloapan, Los Tuxtlas, Olmeca).
  - Añadir un bloque/pestaña en `IndicatorDetailView.vue` (para los indicadores que cuenten con desagregación) con buscador de municipio/región, tabla ordenable y comparativa contra el promedio estatal.
- **Archivos:** `etl/historicos/` (nuevos extractores municipales/regionales), `etl/frontend/generar_datos_frontend.py`, `frontend/vue/src/views/IndicatorDetailView.vue`.

---

## 4. Insumos que se necesitan del cliente para destrabar P2–P4

Antes de ejecutar las fases P3 y P4 conviene solicitar o validar con el cliente los siguientes puntos:

1. **Matriz oficial de responsables (para C12 y C13):** Confirmar por cada uno de los 148 indicadores la *Secretaría, Subsecretaría, Departamento/Área* y *Nombre del enlace o encargado* (o validar si se parte de un catálogo base para que ellos lo completen).
2. **Criterio oficial de atraso/prioridad (para C08 y C09):** Confirmar cómo desean medir el atraso en indicadores sin metas intermedias limpias (ej. avance lineal esperado `2024 → 2030` vs. cualquier retroceso respecto a la línea base).
3. **Definición de los 3+ indicadores piloto (para C15, C16 y C17):** Elegir los 3 indicadores prioritarios donde les interesa ver de inmediato el cruce **Veracruz vs. Nacional**, el **ranking de 32 estados** y la vista **municipal o regional** (por disponibilidad actual, los más rápidos son Pobreza multidimensional INEGI, Educación SEP y un indicador de la API BISE de INEGI).
4. **Regla metodológica para proyecciones (para C14):** Confirmar si los escenarios *mejor / peor* deben calcularse estadísticamente sobre la serie histórica (regresión + desviación/intervalo) o con bandas fijas respecto a la meta.

---

## 5. Hoja de ruta sugerida (4 Sprints)

1. **Sprint 1 (P1 — Inmediato):** `C01` + `C02` + `C03` + `C04` + `C05` + `C06`. Mejora drástica de legibilidad y comprensión financiera sin esperar insumos externos.
2. **Sprint 2 (P2 — Resumen y Seguimiento Sexenal):** Depuración de `metas_intermedias_json` + `C07` + `C08` + `C09` + `C10`. Dashboard convertido en hoja de resumen ejecutivo con atrasos y filtros avanzados.
3. **Sprint 3 (P3 — Responsables y Calendario):** `C11` + `C12` + `C13`. Extracción de periodicidades/fechas, carga de secretarías/encargados y tablero de investigación pendiente por secretaría.
4. **Sprint 4 (P4 — Proyecciones y Comparativos):** `C14` + `C15` + `C16` + `C17`. Escenarios 2030, cruce Veracruz vs. Nacional, ranking de 32 entidades y desglose por región/municipio.
