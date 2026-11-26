<script setup lang="ts">
import { computed, ref } from 'vue'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import SelectButton from 'primevue/selectbutton'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import AppIcon from '../components/common/AppIcon.vue'
import HelpHint from '../components/common/HelpHint.vue'
import StatusTag from '../components/common/StatusTag.vue'
import { useFrontendData } from '../composables/useFrontendData'
import type { DataSource } from '../types/contract'
import { downloadCsv } from '../utils/csv'
import { normalizeText, statusInfo } from '../utils/labels'

type SourceEstado = 'todos' | 'procesado' | 'fuente_identificada' | 'pendiente_revision'

const STATUS_OPTIONS: { label: string; value: SourceEstado }[] = [
  { label: 'Todos', value: 'todos' },
  { label: 'Disponibles', value: 'procesado' },
  { label: 'En integración', value: 'fuente_identificada' },
  { label: 'En revisión', value: 'pendiente_revision' },
]

const toast = useToast()
const data = useFrontendData()

const search = ref('')
const institution = ref<string | null>(null)
const estado = ref<SourceEstado>('todos')

const institutionOptions = computed(() =>
  Array.from(new Set(data.fuentes.map((item) => item.institucion).filter(Boolean))).sort((a, b) =>
    a.localeCompare(b, 'es'),
  ),
)

const filteredSources = computed(() => {
  const q = normalizeText(search.value.trim())
  return data.fuentes.filter((source) => {
    if (institution.value && source.institucion !== institution.value) return false
    if (estado.value !== 'todos' && source.estado !== estado.value) return false
    if (!q) return true
    const text = normalizeText([source.institucion, source.nombre, source.idIndicador].join(' '))
    return text.includes(q)
  })
})

const hasActiveFilters = computed(
  () => Boolean(search.value.trim()) || Boolean(institution.value) || estado.value !== 'todos',
)

const activeFilterChips = computed(() => {
  const chips: { key: 'search' | 'institution' | 'estado'; label: string }[] = []
  if (search.value.trim()) chips.push({ key: 'search', label: `Búsqueda: “${search.value.trim()}”` })
  if (institution.value) chips.push({ key: 'institution', label: `Institución: ${institution.value}` })
  if (estado.value !== 'todos') chips.push({ key: 'estado', label: `Semáforo: ${statusInfo(estado.value).label}` })
  return chips
})

function removeChip(key: 'search' | 'institution' | 'estado') {
  if (key === 'search') search.value = ''
  if (key === 'institution') institution.value = null
  if (key === 'estado') estado.value = 'todos'
}

function resetFilters() {
  search.value = ''
  institution.value = null
  estado.value = 'todos'
}

function formatCoverage(source: DataSource): string {
  if (!source.periodos.length) return `${source.entidad} · Sin periodos`
  const minYear = Math.min(...source.periodos)
  const maxYear = Math.max(...source.periodos)
  const range = minYear === maxYear ? String(minYear) : `${minYear}–${maxYear}`
  return `${source.entidad} · ${range} · ${source.periodos.length} periodos`
}

function exportSourcesCsv() {
  const headers = ['Institución', 'Indicador', 'Entidad', 'Periodos', 'Estado', 'URL']
  const rows = filteredSources.value.map((source) => [
    source.institucion,
    source.nombre,
    source.entidad,
    source.periodos.join(', '),
    statusInfo(source.estado).label,
    source.url,
  ])
  downloadCsv('fuentes-pvd-veracruz.csv', headers, rows)
  toast.add({
    severity: 'success',
    summary: 'Archivo listo',
    detail: `Se exportaron ${rows.length} fuentes para Excel.`,
    life: 3200,
  })
}
</script>

<template>
  <section class="surface-card content-panel">
    <div class="content-panel__header">
      <div>
        <span class="section-kicker">TRAZABILIDAD</span>
        <h2>Fuentes oficiales de información</h2>
      </div>
      <div class="catalog-header-actions">
        <span class="table-caption" aria-live="polite">
          {{ filteredSources.length }} de {{ data.fuentes.length }} fuentes
        </span>
        <Button
          label="Exportar a Excel (CSV)"
          outlined
          :disabled="filteredSources.length === 0"
          @click="exportSourcesCsv"
        >
          <template #icon>
            <AppIcon name="download" size="sm" />
          </template>
        </Button>
      </div>
    </div>

    <div class="catalog-toolbar">
      <div class="catalog-search-group">
        <label class="sr-only" for="sources-search-input">Buscar fuentes u organismos</label>
        <IconField class="catalog-search-field">
          <InputIcon>
            <AppIcon name="search" size="sm" />
          </InputIcon>
          <InputText
            id="sources-search-input"
            v-model="search"
            type="search"
            placeholder="Buscar por institución o nombre del indicador"
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
            aria-label="Filtrar fuentes por disponibilidad"
          />
        </div>

        <div class="filter-group">
          <span class="filter-label">Institución</span>
          <Select
            v-model="institution"
            :options="institutionOptions"
            showClear
            filter
            placeholder="Todas las instituciones"
            aria-label="Filtrar por institución"
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
      :value="filteredSources"
      dataKey="idIndicador"
      paginator
      :rows="20"
      :rowsPerPageOptions="[10, 20, 50, 148]"
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      currentPageReportTemplate="{first}–{last} de {totalRecords}"
      responsiveLayout="scroll"
    >
      <Column field="institucion" header="Institución" sortable>
        <template #body="{ data: row }">
          <Tag :value="row.institucion" class="inst-tag" />
        </template>
      </Column>

      <Column field="nombre" header="Fuente / Indicador" sortable>
        <template #body="{ data: row }">
          <RouterLink class="indicator-link" :to="`/indicadores/${row.idIndicador}`">
            {{ row.nombre }}
          </RouterLink>
        </template>
      </Column>

      <Column header="Cobertura">
        <template #body="{ data: row }">
          <span class="source-coverage">{{ formatCoverage(row) }}</span>
        </template>
      </Column>

      <Column field="estado" header="Estado" sortable>
        <template #body="{ data: row }">
          <StatusTag :estado="row.estado" />
        </template>
      </Column>

      <Column header="Acción">
        <template #body="{ data: row }">
          <a
            v-if="row.url"
            class="source-link"
            :href="row.url"
            target="_blank"
            rel="noreferrer"
            :aria-label="`Consultar fuente de ${row.nombre} (abre en una pestaña nueva)`"
          >
            <span>Consultar fuente</span>
            <AppIcon name="open_in_new" size="xs" />
          </a>
          <span v-else class="source-unavailable">No disponible</span>
        </template>
      </Column>

      <template #empty>
        <div class="table-empty">
          <AppIcon name="search_off" size="xl" />
          <p>No encontramos fuentes con los criterios seleccionados.</p>
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
