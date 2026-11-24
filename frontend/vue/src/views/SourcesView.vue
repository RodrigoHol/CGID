<script setup lang="ts">
import Button from 'primevue/button'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import Tag from 'primevue/tag'
import StatusTag from '../components/common/StatusTag.vue'
import { useFrontendData } from '../composables/useFrontendData'
import type { DataSource } from '../types/contract'
import { downloadCsv } from '../utils/csv'
import { statusInfo } from '../utils/labels'

const data = useFrontendData()

function formatCoverage(source: DataSource): string {
  if (!source.periodos.length) return `${source.entidad} · Sin periodos`
  const minYear = Math.min(...source.periodos)
  const maxYear = Math.max(...source.periodos)
  const range = minYear === maxYear ? String(minYear) : `${minYear}–${maxYear}`
  return `${source.entidad} · ${range} · ${source.periodos.length} periodos`
}

function exportSourcesCsv() {
  const headers = ['Institución', 'Indicador', 'Entidad', 'Periodos', 'Estado', 'URL']
  const rows = data.fuentes.map((source) => [
    source.institucion,
    source.nombre,
    source.entidad,
    source.periodos.join(', '),
    statusInfo(source.estado).label,
    source.url,
  ])
  downloadCsv('fuentes-pvd-veracruz.csv', headers, rows)
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
        <span class="table-caption">{{ data.fuentes.length }} fuentes registradas</span>
        <Button
          label="Descargar CSV"
          icon="pi pi-download"
          outlined
          size="small"
          @click="exportSourcesCsv"
        />
      </div>
    </div>

    <DataTable :value="data.fuentes" dataKey="idIndicador" responsiveLayout="scroll">
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
            <i class="pi pi-external-link" aria-hidden="true"></i>
          </a>
          <span v-else class="source-unavailable">No disponible</span>
        </template>
      </Column>
    </DataTable>
  </section>
</template>
