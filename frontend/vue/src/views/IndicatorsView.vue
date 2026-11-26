<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter, type LocationQuery } from 'vue-router'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import Column from 'primevue/column'
import DataTable, { type DataTableRowClickEvent } from 'primevue/datatable'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import SelectButton from 'primevue/selectbutton'
import { useToast } from 'primevue/usetoast'
import AppIcon from '../components/common/AppIcon.vue'
import HelpHint from '../components/common/HelpHint.vue'
import StatusTag from '../components/common/StatusTag.vue'
import { useFrontendData } from '../composables/useFrontendData'
import type { HistoricalPoint, Indicator } from '../types/contract'
import { calculateGoalProgress, type GoalProgress } from '../utils/calculations'
import { downloadCsv } from '../utils/csv'
import { directionInfo, formatValue, normalizeText, statusInfo } from '../utils/labels'

type EstadoFilter = 'todos' | 'procesado' | 'fuente_identificada' | 'pendiente_revision'

const VALID_SORT_FIELDS = new Set(['nombre', 'ejeRector', 'estadoHistorico'])
const STATUS_OPTIONS: { label: string; value: EstadoFilter }[] = [
  { label: 'Todos', value: 'todos' },
  { label: 'Disponibles', value: 'procesado' },
  { label: 'En integración', value: 'fuente_identificada' },
  { label: 'En revisión', value: 'pendiente_revision' },
]

const route = useRoute()
const router = useRouter()
const toast = useToast()
const data = useFrontendData()

const axisOptions = computed(() =>
  Array.from(new Set(data.indicadores.map((item) => item.ejeRector).filter(Boolean))).sort((a, b) =>
    a.localeCompare(b, 'es'),
  ),
)

const search = ref('')
const estado = ref<EstadoFilter>('todos')
const eje = ref<string | null>(null)
const sortField = ref<string | undefined>(undefined)
const sortOrder = ref<number | undefined>(undefined)
let syncingFromRoute = false

function readQueryValue(value: LocationQuery[string]): string {
  if (Array.isArray(value)) return typeof value[0] === 'string' ? value[0] : ''
  return typeof value === 'string' ? value : ''
}

function syncFromRoute(query: LocationQuery) {
  syncingFromRoute = true
  const q = readQueryValue(query.q)
  const rawEstado = readQueryValue(query.estado)
  const rawEje = readQueryValue(query.eje)
  const rawOrden = readQueryValue(query.orden)
  const rawDir = readQueryValue(query.dir)

  search.value = q
  estado.value =
    rawEstado === 'procesado' || rawEstado === 'fuente_identificada' || rawEstado === 'pendiente_revision'
      ? rawEstado
      : 'todos'
  eje.value = rawEje && axisOptions.value.includes(rawEje) ? rawEje : null
  sortField.value = VALID_SORT_FIELDS.has(rawOrden) ? rawOrden : undefined
  sortOrder.value = rawDir === '1' ? 1 : rawDir === '-1' ? -1 : undefined
  syncingFromRoute = false
}

syncFromRoute(route.query)

watch(
  () => route.query,
  (nextQuery) => {
    if (route.name !== 'indicadores') return
    syncFromRoute(nextQuery)
  },
)

function buildQueryFromState(): Record<string, string> {
  const next: Record<string, string> = {}
  const trimmed = search.value.trim()
  if (trimmed) next.q = trimmed
  if (estado.value !== 'todos') next.estado = estado.value
  if (eje.value) next.eje = eje.value
  if (sortField.value) next.orden = sortField.value
  if (sortOrder.value === 1 || sortOrder.value === -1) next.dir = String(sortOrder.value)
  return next
}

function sameQuery(a: Record<string, string>, b: LocationQuery): boolean {
  const bNormalized: Record<string, string> = {}
  for (const key of ['q', 'estado', 'eje', 'orden', 'dir']) {
    const val = readQueryValue(b[key])
    if (val) bNormalized[key] = val
  }
  const keysA = Object.keys(a)
  const keysB = Object.keys(bNormalized)
  if (keysA.length !== keysB.length) return false
  return keysA.every((key) => a[key] === bNormalized[key])
}

watch([search, estado, eje, sortField, sortOrder], () => {
  if (syncingFromRoute || route.name !== 'indicadores') return
  const next = buildQueryFromState()
  if (!sameQuery(next, route.query)) {
    router.replace({ query: next })
  }
})

const filteredIndicators = computed(() => {
  const query = normalizeText(search.value.trim())
  return data.indicadores.filter((indicator) => {
    if (estado.value !== 'todos' && indicator.estadoHistorico !== estado.value) return false
    if (eje.value && indicator.ejeRector !== eje.value) return false
    if (!query) return true
    const searchable = normalizeText([indicator.clave, indicator.nombre, indicator.ejeRector].join(' '))
    return searchable.includes(query)
  })
})

const hasActiveFilters = computed(
  () => Boolean(search.value.trim()) || estado.value !== 'todos' || Boolean(eje.value),
)

const activeFilterChips = computed(() => {
  const chips: { key: 'search' | 'estado' | 'eje'; label: string }[] = []
  if (search.value.trim()) {
    chips.push({ key: 'search', label: `Búsqueda: “${search.value.trim()}”` })
  }
  if (estado.value !== 'todos') {
    chips.push({ key: 'estado', label: `Semáforo: ${statusInfo(estado.value).label}` })
  }
  if (eje.value) {
    chips.push({ key: 'eje', label: `Eje: ${eje.value}` })
  }
  return chips
})

function removeChip(key: 'search' | 'estado' | 'eje') {
  if (key === 'search') search.value = ''
  if (key === 'estado') estado.value = 'todos'
  if (key === 'eje') eje.value = null
}

interface CatalogRowMetrics {
  latest: HistoricalPoint | null
  progress: GoalProgress
}

const indicatorMetricsMap = computed(() => {
  const map = new Map<string, CatalogRowMetrics>()
  for (const indicator of data.indicadores) {
    const series = data.historicos[indicator.id]?.datos ?? []
    map.set(indicator.id, {
      latest: series.at(-1) ?? null,
      progress: calculateGoalProgress(indicator, series),
    })
  }
  return map
})

function getRowMetrics(indicatorId: string): CatalogRowMetrics {
  return indicatorMetricsMap.value.get(indicatorId) ?? {
    latest: null,
    progress: {
      status: 'no_series',
      percent: null,
      rawPercent: null,
      barPercent: 0,
      tone: 'neutral',
      shortLabel: 'Sin serie',
      badgeLabel: 'Sin serie histórica',
      detail: '',
    },
  }
}

function resetFilters() {
  search.value = ''
  estado.value = 'todos'
  eje.value = null
}

function onSortFieldChange(value: string | ((item: Indicator) => string) | undefined | null) {
  sortField.value = typeof value === 'string' && VALID_SORT_FIELDS.has(value) ? value : undefined
}

function onSortOrderChange(value: number | undefined | null) {
  sortOrder.value = value === 1 || value === -1 ? value : undefined
}

function onRowClick(event: DataTableRowClickEvent<Indicator>) {
  const target = event.originalEvent.target as HTMLElement | null
  if (target?.closest('a') || target?.closest('button')) return
  router.push(`/indicadores/${event.data.id}`)
}

function exportCsv() {
  const headers = [
    'Clave',
    'Indicador',
    'Eje rector',
    'Estado',
    'Sentido',
    'Unidad',
    'Año línea base',
    'Línea base',
    'Meta 2030',
    'Último año',
    'Último valor',
    'Avance 2030',
    'Fuente (URL)',
  ]
  const rows = filteredIndicators.value.map((indicator) => {
    const { latest, progress } = getRowMetrics(indicator.id)
    return [
      indicator.clave,
      indicator.nombre,
      indicator.ejeRector,
      statusInfo(indicator.estadoHistorico).label,
      `${directionInfo(indicator.sentido).label}${indicator.sentido ? ` (${indicator.sentido})` : ''}`,
      indicator.unidadMedida || 'Según fuente oficial',
      indicator.lineaBase.anio,
      indicator.lineaBase.valor,
      indicator.meta2030,
      latest?.anio ?? null,
      latest?.valor ?? null,
      progress.shortLabel,
      indicator.fuente.url,
    ]
  })
  downloadCsv('indicadores-pvd-veracruz.csv', headers, rows)
  toast.add({
    severity: 'success',
    summary: 'Archivo listo',
    detail: `Se exportaron ${rows.length} indicadores para Excel.`,
    life: 3200,
  })
}
</script>

<template>
  <section class="surface-card content-panel">
    <div class="content-panel__header">
      <div>
        <span class="section-kicker">CATÁLOGO PVD 2025–2030</span>
        <h2>Indicadores del Plan Veracruzano de Desarrollo</h2>
      </div>
      <div class="catalog-header-actions">
        <span class="table-caption" aria-live="polite">
          {{ filteredIndicators.length }} de {{ data.indicadores.length }} indicadores
        </span>
        <Button
          label="Exportar a Excel (CSV)"
          outlined
          :disabled="filteredIndicators.length === 0"
          @click="exportCsv"
        >
          <template #icon>
            <AppIcon name="download" size="sm" />
          </template>
        </Button>
      </div>
    </div>

    <div class="catalog-toolbar">
      <div class="catalog-search-group">
        <label class="sr-only" for="catalog-search-input">Buscar indicadores</label>
        <IconField class="catalog-search-field">
          <InputIcon>
            <AppIcon name="search" size="sm" />
          </InputIcon>
          <InputText
            id="catalog-search-input"
            v-model="search"
            type="search"
            placeholder="Escribe el nombre, clave o tema del indicador"
          />
        </IconField>
      </div>

      <div class="catalog-controls">
        <div class="filter-group">
          <span class="filter-label">
            Semáforo de disponibilidad
            <HelpHint term-key="semaforo" />
          </span>
          <SelectButton
            v-model="estado"
            :options="STATUS_OPTIONS"
            optionLabel="label"
            optionValue="value"
            :allowEmpty="false"
            aria-label="Filtrar por disponibilidad de datos"
          />
        </div>

        <div class="filter-group">
          <span class="filter-label">
            Eje rector
            <HelpHint term-key="ejeRector" />
          </span>
          <Select
            v-model="eje"
            :options="axisOptions"
            showClear
            placeholder="Todos los ejes"
            aria-label="Filtrar por eje rector"
            class="axis-select"
          />
        </div>

        <Button
          v-if="hasActiveFilters"
          label="Limpiar filtros"
          text
          @click="resetFilters"
        >
          <template #icon>
            <AppIcon name="filter_alt_off" size="sm" />
          </template>
        </Button>
      </div>

      <div class="semaphore-inline-legend" aria-hidden="true">
        <span class="semaphore-item semaphore-item--green">
          <span class="sem-dot"></span> Verde: con serie lista
        </span>
        <span class="semaphore-item semaphore-item--amber">
          <span class="sem-dot"></span> Ámbar: en integración
        </span>
        <span class="semaphore-item semaphore-item--red">
          <span class="sem-dot"></span> Rojo: en revisión
        </span>
      </div>

      <div v-if="activeFilterChips.length" class="active-chips" aria-label="Filtros activos">
        <Chip
          v-for="chip in activeFilterChips"
          :key="chip.key"
          :label="chip.label"
          removable
          class="filter-chip"
          @remove="removeChip(chip.key)"
        >
          <template #removeicon="{ removeCallback, keydownCallback }">
            <button
              type="button"
              class="filter-chip__remove"
              :aria-label="`Quitar filtro ${chip.label}`"
              @click="removeCallback"
              @keydown="keydownCallback"
            >
              <AppIcon name="close" size="xs" />
            </button>
          </template>
        </Chip>
      </div>
    </div>

    <DataTable
      :value="filteredIndicators"
      dataKey="id"
      paginator
      :rows="20"
      :rowsPerPageOptions="[10, 20, 50, 148]"
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      currentPageReportTemplate="{first}–{last} de {totalRecords}"
      :sortField="sortField"
      :sortOrder="sortOrder"
      removableSort
      responsiveLayout="scroll"
      :rowClass="() => 'indicator-table__row'"
      @update:sort-field="onSortFieldChange"
      @update:sort-order="onSortOrderChange"
      @row-click="onRowClick"
    >
      <Column field="nombre" header="Indicador" sortable>
        <template #body="{ data: row }">
          <div class="indicator-cell">
            <RouterLink class="indicator-link" :to="`/indicadores/${row.id}`">
              {{ row.nombre }}
            </RouterLink>
            <span class="indicator-code">{{ row.clave }}</span>
          </div>
        </template>
      </Column>

      <Column field="ejeRector" header="Eje rector" sortable class="col-axis">
        <template #body="{ data: row }">
          <span class="indicator-axis">{{ row.ejeRector }}</span>
        </template>
      </Column>

      <Column header="Último dato">
        <template #body="{ data: row }">
          <div v-if="getRowMetrics(row.id).latest" class="latest-cell">
            <strong>{{ formatValue(getRowMetrics(row.id).latest?.valor, row.unidadMedida) }}</strong>
            <small>{{ getRowMetrics(row.id).latest?.anio }}</small>
          </div>
          <span v-else class="latest-empty">—</span>
        </template>
      </Column>

      <Column>
        <template #header>
          <span class="table-header-with-help">
            Avance 2030
            <HelpHint term-key="porcentajeAvance" size="xs" />
          </span>
        </template>
        <template #body="{ data: row }">
          <div v-if="getRowMetrics(row.id).latest" class="catalog-progress-cell">
            <div class="catalog-progress-label" :class="`catalog-progress-label--${getRowMetrics(row.id).progress.tone}`">
              <span class="sem-dot" aria-hidden="true"></span>
              <span>{{ getRowMetrics(row.id).progress.shortLabel }}</span>
            </div>
            <div
              v-if="getRowMetrics(row.id).progress.percent !== null"
              class="mini-progress-bar"
              aria-hidden="true"
            >
              <div
                class="mini-progress-fill"
                :class="`progress-fill--${getRowMetrics(row.id).progress.tone}`"
                :style="{ width: `${getRowMetrics(row.id).progress.barPercent}%` }"
              ></div>
            </div>
          </div>
          <span v-else class="latest-empty">—</span>
        </template>
      </Column>

      <Column field="estadoHistorico" header="Estado" sortable>
        <template #body="{ data: row }">
          <StatusTag :estado="row.estadoHistorico" />
        </template>
      </Column>

      <template #empty>
        <div class="table-empty">
          <AppIcon name="search_off" size="xl" />
          <p>
            No encontramos indicadores
            <template v-if="search.trim()">para “{{ search.trim() }}”</template>
            con los filtros seleccionados.
          </p>
          <Button
            v-if="hasActiveFilters"
            label="Limpiar filtros"
            text
            @click="resetFilters"
          >
            <template #icon>
              <AppIcon name="filter_alt_off" size="sm" />
            </template>
          </Button>
        </div>
      </template>
    </DataTable>
  </section>
</template>
