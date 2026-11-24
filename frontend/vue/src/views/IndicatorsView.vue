<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter, type LocationQuery } from 'vue-router'
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable, { type DataTableRowClickEvent } from 'primevue/datatable'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import SelectButton from 'primevue/selectbutton'
import StatusTag from '../components/common/StatusTag.vue'
import { useFrontendData } from '../composables/useFrontendData'
import type { Indicator } from '../types/contract'
import { downloadCsv } from '../utils/csv'
import { GLOSSARY_BY_KEY } from '../utils/glossary'
import { directionInfo, formatValue, normalizeText, statusInfo } from '../utils/labels'

type EstadoFilter = 'todos' | 'procesado' | 'fuente_identificada'

const VALID_SORT_FIELDS = new Set(['nombre', 'ejeRector', 'estadoHistorico'])
const STATUS_OPTIONS: { label: string; value: EstadoFilter }[] = [
  { label: 'Todos', value: 'todos' },
  { label: 'Con serie histórica', value: 'procesado' },
  { label: 'En integración', value: 'fuente_identificada' },
]

const route = useRoute()
const router = useRouter()
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
const searchInputRef = ref<{ $el?: HTMLElement } | null>(null)
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
  estado.value = rawEstado === 'procesado' || rawEstado === 'fuente_identificada' ? rawEstado : 'todos'
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

function getLatestPoint(indicatorId: string) {
  return data.historicos[indicatorId]?.datos?.at(-1) ?? null
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
  if (target?.closest('a')) return
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
    'Fuente (URL)',
  ]
  const rows = filteredIndicators.value.map((indicator) => {
    const latest = getLatestPoint(indicator.id)
    return [
      indicator.clave,
      indicator.nombre,
      indicator.ejeRector,
      statusInfo(indicator.estadoHistorico).label,
      `${directionInfo(indicator.sentido).label}${indicator.sentido ? ` (${indicator.sentido})` : ''}`,
      indicator.unidadMedida || 'No especificada',
      indicator.lineaBase.anio,
      indicator.lineaBase.valor,
      indicator.meta2030,
      latest?.anio ?? null,
      latest?.valor ?? null,
      indicator.fuente.url,
    ]
  })
  downloadCsv('indicadores-pvd-veracruz.csv', headers, rows)
}

function onWindowKeydown(event: KeyboardEvent) {
  if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey) return
  const target = event.target as HTMLElement | null
  const tag = target?.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || target?.isContentEditable) return
  event.preventDefault()
  const el = searchInputRef.value?.$el
  if (el instanceof HTMLInputElement) {
    el.focus()
  } else {
    el?.querySelector('input')?.focus()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onWindowKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onWindowKeydown)
})
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
          label="Descargar CSV"
          icon="pi pi-download"
          outlined
          size="small"
          :disabled="filteredIndicators.length === 0"
          @click="exportCsv"
        />
      </div>
    </div>

    <div class="catalog-toolbar">
      <div class="catalog-search-group">
        <label class="sr-only" for="catalog-search-input">Buscar indicadores</label>
        <IconField class="catalog-search-field">
          <InputIcon class="pi pi-search" />
          <InputText
            id="catalog-search-input"
            ref="searchInputRef"
            v-model="search"
            type="search"
            placeholder="Buscar por nombre, clave o eje"
          />
        </IconField>
        <span class="shortcut-hint" aria-hidden="true">
          <kbd>/</kbd> para buscar
        </span>
      </div>

      <div class="catalog-controls">
        <div class="filter-group">
          <span class="filter-label">Estado de los datos</span>
          <SelectButton
            v-model="estado"
            :options="STATUS_OPTIONS"
            optionLabel="label"
            optionValue="value"
            :allowEmpty="false"
            aria-label="Filtrar por estado de los datos"
          />
        </div>

        <div class="filter-group">
          <span class="filter-label">
            Eje rector
            <i
              class="pi pi-info-circle info-hint"
              tabindex="0"
              :aria-label="GLOSSARY_BY_KEY.ejeRector.definition"
              v-tooltip.top="GLOSSARY_BY_KEY.ejeRector.definition"
            ></i>
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
          icon="pi pi-filter-slash"
          text
          size="small"
          @click="resetFilters"
        />
      </div>
    </div>

    <DataTable
      :value="filteredIndicators"
      dataKey="id"
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
          <div v-if="getLatestPoint(row.id)" class="latest-cell">
            <strong>{{ formatValue(getLatestPoint(row.id)?.valor, row.unidadMedida) }}</strong>
            <small>{{ getLatestPoint(row.id)?.anio }}</small>
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
          <i class="pi pi-search" aria-hidden="true"></i>
          <p>
            No encontramos indicadores
            <template v-if="search.trim()">para “{{ search.trim() }}”</template>
            con los filtros seleccionados.
          </p>
          <Button
            v-if="hasActiveFilters"
            label="Limpiar filtros"
            icon="pi pi-filter-slash"
            text
            @click="resetFilters"
          />
        </div>
      </template>
    </DataTable>
  </section>
</template>
