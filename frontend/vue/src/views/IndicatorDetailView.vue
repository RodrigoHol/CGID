<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Breadcrumb from 'primevue/breadcrumb'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import StatusState from '../components/common/StatusState.vue'
import StatusTag from '../components/common/StatusTag.vue'
import HistoricalChart from '../components/indicators/HistoricalChart.vue'
import { useFrontendData } from '../composables/useFrontendData'
import { SITE_NAME } from '../config/site'
import { downloadCsv } from '../utils/csv'
import { GLOSSARY_BY_KEY } from '../utils/glossary'
import {
  assessVariation,
  directionInfo,
  formatValue,
  formatVariation,
} from '../utils/labels'

const route = useRoute()
const router = useRouter()
const data = useFrontendData()

const indicator = computed(() => data.indicadores.find((item) => item.id === route.params.id))
const series = computed(() => (indicator.value ? data.historicos[indicator.value.id]?.datos ?? [] : []))
const source = computed(() =>
  indicator.value ? data.fuentes.find((item) => item.idIndicador === indicator.value?.id) : undefined,
)
const latest = computed(() => series.value.at(-1))
const first = computed(() => series.value[0])
const variation = computed(() =>
  latest.value && first.value ? latest.value.valor - first.value.valor : null,
)
const variationLabel = computed(() =>
  variation.value !== null
    ? formatVariation(variation.value, indicator.value?.unidadMedida)
    : 'Sin serie histórica',
)
const variationAssessment = computed(() =>
  indicator.value ? assessVariation(variation.value, indicator.value.sentido) : null,
)
const direction = computed(() => directionInfo(indicator.value?.sentido ?? ''))
const sourceUrl = computed(() => source.value?.url || indicator.value?.fuente.url || '')

const observationsExpanded = ref(false)
const recentSeries = computed(() => [...series.value].reverse())
const visibleObservations = computed(() =>
  observationsExpanded.value ? recentSeries.value : recentSeries.value.slice(0, 3),
)

const backToCatalogPath = computed(() => {
  const back = window.history.state?.back
  if (typeof back === 'string' && (back === '/indicadores' || back.startsWith('/indicadores?'))) {
    return back
  }
  return '/indicadores'
})

const breadcrumbHome = { icon: 'pi pi-home', route: '/', label: 'Inicio' }
const breadcrumbItems = computed(() => {
  const rawName = indicator.value?.nombre ?? 'Indicador'
  const truncated = rawName.length > 60 ? `${rawName.slice(0, 57)}…` : rawName
  return [
    { label: 'Indicadores', route: backToCatalogPath.value },
    { label: truncated },
  ]
})

watchEffect(() => {
  document.title = indicator.value
    ? `${indicator.value.nombre} | ${SITE_NAME} · IAP Veracruz`
    : `Indicador no encontrado | ${SITE_NAME} · IAP Veracruz`
})

function goBack() {
  const back = window.history.state?.back
  if (typeof back === 'string' && (back === '/indicadores' || back.startsWith('/indicadores?'))) {
    router.back()
    return
  }
  router.push('/indicadores')
}

function exportSeriesCsv() {
  if (!indicator.value || !series.value.length) return
  const headers = ['Año', 'Valor']
  const rows = series.value.map((point) => [point.anio, point.valor])
  downloadCsv(`${indicator.value.clave}-serie.csv`, headers, rows)
}
</script>

<template>
  <section v-if="indicator" class="detail-page">
    <div class="detail-topbar">
      <Breadcrumb :home="breadcrumbHome" :model="breadcrumbItems" class="detail-breadcrumb">
        <template #item="{ item }">
          <RouterLink v-if="item.route" :to="item.route" class="p-breadcrumb-item-link">
            <i v-if="item.icon" :class="item.icon" aria-hidden="true"></i>
            <span>{{ item.label }}</span>
          </RouterLink>
          <span v-else class="p-breadcrumb-item-link p-breadcrumb-item-link--current" aria-current="page">
            {{ item.label }}
          </span>
        </template>
      </Breadcrumb>

      <Button
        label="Volver al catálogo"
        icon="pi pi-arrow-left"
        text
        size="small"
        class="back-button"
        @click="goBack"
      />
    </div>

    <section class="surface-card detail-hero">
      <div class="detail-hero__body">
        <span class="section-kicker">{{ indicator.clave }}</span>
        <h1>{{ indicator.nombre }}</h1>
        <p>{{ indicator.descripcion }}</p>
      </div>
      <div class="detail-hero__badges">
        <StatusTag :estado="indicator.estadoHistorico" />
        <Tag
          v-if="indicator.unidadMedida"
          :value="indicator.unidadMedida"
          icon="pi pi-tag"
          class="unit-tag"
        />
      </div>
    </section>

    <section class="detail-metrics" aria-label="Cifras clave del indicador">
      <article class="surface-card detail-metric-card">
        <span class="detail-metric-card__label">
          Línea base
          <i
            class="pi pi-info-circle info-hint"
            tabindex="0"
            :aria-label="GLOSSARY_BY_KEY.lineaBase.definition"
            v-tooltip.top="GLOSSARY_BY_KEY.lineaBase.definition"
          ></i>
        </span>
        <strong>{{ formatValue(indicator.lineaBase.valor, indicator.unidadMedida) }}</strong>
        <small>{{ indicator.lineaBase.anio || 'No disponible' }}</small>
      </article>

      <article class="surface-card detail-metric-card">
        <span class="detail-metric-card__label">
          Meta 2030
          <i
            class="pi pi-info-circle info-hint"
            tabindex="0"
            :aria-label="GLOSSARY_BY_KEY.meta2030.definition"
            v-tooltip.top="GLOSSARY_BY_KEY.meta2030.definition"
          ></i>
        </span>
        <strong>{{ formatValue(indicator.meta2030, indicator.unidadMedida) }}</strong>
        <small>Objetivo del PVD</small>
      </article>

      <article class="surface-card detail-metric-card">
        <span class="detail-metric-card__label">
          Último valor
          <i
            class="pi pi-info-circle info-hint"
            tabindex="0"
            :aria-label="GLOSSARY_BY_KEY.ultimoValor.definition"
            v-tooltip.top="GLOSSARY_BY_KEY.ultimoValor.definition"
          ></i>
        </span>
        <strong>{{ latest ? formatValue(latest.valor, indicator.unidadMedida) : '—' }}</strong>
        <small>{{ latest?.anio || 'Sin periodo' }}</small>
      </article>

      <article class="surface-card detail-metric-card">
        <span class="detail-metric-card__label">
          Variación observada
          <i
            class="pi pi-info-circle info-hint"
            tabindex="0"
            :aria-label="GLOSSARY_BY_KEY.variacionObservada.definition"
            v-tooltip.top="GLOSSARY_BY_KEY.variacionObservada.definition"
          ></i>
        </span>
        <strong>{{ variationLabel }}</strong>
        <div class="detail-metric-card__foot">
          <Tag
            v-if="variationAssessment"
            :value="variationAssessment.label"
            :icon="variationAssessment.icon"
            :class="['trend-tag', variationAssessment.cls]"
          />
          <small>{{ first?.anio || '—' }} a {{ latest?.anio || '—' }}</small>
        </div>
      </article>
    </section>

    <section class="surface-card detail-card detail-chart-card">
      <div class="detail-card__header">
        <div>
          <span class="section-kicker">EVOLUCIÓN HISTÓRICA</span>
          <h2>Serie disponible para {{ data.resumen.entidad }}</h2>
        </div>
        <span class="unit-label">{{ indicator.unidadMedida || 'Valor del indicador' }}</span>
      </div>
      <HistoricalChart
        :points="series"
        :baseline="indicator.lineaBase"
        :target="indicator.meta2030"
        :direction="indicator.sentido"
        :unit="indicator.unidadMedida"
      />
    </section>

    <div class="detail-columns">
      <section class="surface-card detail-card">
        <div class="detail-card__header">
          <div>
            <span class="section-kicker">OBSERVACIONES</span>
            <h2>Datos publicados</h2>
          </div>
          <div class="observation-actions">
            <span class="observation-count">{{ series.length }} periodos</span>
            <Button
              v-if="series.length"
              label="Descargar serie (CSV)"
              icon="pi pi-download"
              outlined
              size="small"
              @click="exportSeriesCsv"
            />
          </div>
        </div>

        <table v-if="series.length" class="observation-table">
          <caption class="sr-only">
            Observaciones históricas publicadas para {{ indicator.nombre }}
          </caption>
          <thead>
            <tr>
              <th scope="col">Periodo</th>
              <th scope="col">Valor</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="point in visibleObservations" :key="point.anio">
              <th scope="row">{{ point.anio }}</th>
              <td>{{ formatValue(point.valor, indicator.unidadMedida) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="observation-empty">Aún no hay observaciones históricas publicadas.</p>

        <Button
          v-if="series.length > 3"
          class="observation-toggle"
          :label="observationsExpanded ? 'Mostrar solo los 3 más recientes' : `Mostrar los ${series.length} periodos`"
          :icon="observationsExpanded ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
          iconPos="right"
          text
          size="small"
          :aria-expanded="observationsExpanded"
          @click="observationsExpanded = !observationsExpanded"
        />
      </section>

      <section class="surface-card detail-card detail-facts">
        <div class="detail-card__header">
          <div>
            <span class="section-kicker">FICHA TÉCNICA</span>
            <h2>Interpretación</h2>
          </div>
        </div>
        <dl>
          <div>
            <dt>
              Sentido
              <i
                class="pi pi-info-circle info-hint"
                tabindex="0"
                :aria-label="GLOSSARY_BY_KEY.sentido.definition"
                v-tooltip.top="GLOSSARY_BY_KEY.sentido.definition"
              ></i>
            </dt>
            <dd class="direction-value">
              <i :class="direction.icon" aria-hidden="true"></i>
              <span>
                {{ direction.label }}
                <template v-if="indicator.sentido">({{ indicator.sentido.toLowerCase() }})</template>
              </span>
            </dd>
          </div>
          <div>
            <dt>Eje rector</dt>
            <dd>{{ indicator.ejeRector || 'No especificado' }}</dd>
          </div>
          <div>
            <dt>Entidad</dt>
            <dd>{{ data.resumen.entidad }}</dd>
          </div>
          <div>
            <dt>Fórmula</dt>
            <dd>{{ indicator.formula || 'No especificada' }}</dd>
          </div>
          <div>
            <dt>Unidad</dt>
            <dd>{{ indicator.unidadMedida || 'No especificada' }}</dd>
          </div>
        </dl>
      </section>
    </div>

    <section class="surface-card detail-card detail-source">
      <div class="detail-card__header">
        <div>
          <span class="section-kicker">PROCEDENCIA</span>
          <h2>Fuente de información</h2>
        </div>
      </div>
      <div class="source-detail">
        <div>
          <strong>{{ source?.institucion || 'Fuente identificada' }}</strong>
          <p>{{ source?.nombre || indicator.fuente.medioVerificacion }}</p>
          <small>{{ source?.observaciones || indicator.fuente.observaciones }}</small>
        </div>
        <a
          v-if="sourceUrl"
          class="p-button p-component p-button-outlined source-link"
          :href="sourceUrl"
          target="_blank"
          rel="noreferrer"
          :aria-label="`Consultar fuente en ${source?.institucion || 'sitio oficial'} (abre en una pestaña nueva)`"
        >
          <span>Consultar fuente</span>
          <i class="pi pi-external-link" aria-hidden="true"></i>
        </a>
        <span v-else class="source-unavailable">Enlace no disponible</span>
      </div>
    </section>
  </section>

  <section v-else class="not-found-page">
    <div class="surface-card">
      <StatusState
        type="empty"
        title="Indicador no encontrado"
        :message="`La clave “${String(route.params.id)}” no existe o fue actualizada.`"
      >
        <template #actions>
          <Button label="Ir al catálogo" icon="pi pi-list" @click="router.push('/indicadores')" />
          <Button label="Ir al inicio" icon="pi pi-home" severity="secondary" outlined @click="router.push('/')" />
        </template>
      </StatusState>
    </div>
  </section>
</template>
