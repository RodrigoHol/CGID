<script setup lang="ts">
import { computed, ref, watch, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import AppIcon from '../components/common/AppIcon.vue'
import HelpHint from '../components/common/HelpHint.vue'
import StatusState from '../components/common/StatusState.vue'
import StatusTag from '../components/common/StatusTag.vue'
import HistoricalChart from '../components/indicators/HistoricalChart.vue'
import { useFrontendData } from '../composables/useFrontendData'
import { SITE_NAME } from '../config/site'
import {
  buildVariationBaseOptions,
  calculateGoalProgress,
  calculateTimeRemaining,
  explainBaseline,
  explainFormula,
  explainUnit,
  getDefaultVariationBaseKey,
} from '../utils/calculations'
import { downloadCsv } from '../utils/csv'
import {
  assessVariation,
  directionInfo,
  formatNumber,
  formatValue,
  formatVariation,
} from '../utils/labels'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const data = useFrontendData()

const indicator = computed(() => data.indicadores.find((item) => item.id === route.params.id))
const series = computed(() => (indicator.value ? data.historicos[indicator.value.id]?.datos ?? [] : []))
const source = computed(() =>
  indicator.value ? data.fuentes.find((item) => item.idIndicador === indicator.value?.id) : undefined,
)
const latest = computed(() => series.value.at(-1))

const variationBaseOptions = computed(() =>
  indicator.value ? buildVariationBaseOptions(indicator.value, series.value) : [],
)
const selectedBaseKey = ref<string | null>(null)
const observationsExpanded = ref(false)

watch(
  () => indicator.value?.id,
  () => {
    observationsExpanded.value = false
    selectedBaseKey.value = indicator.value
      ? getDefaultVariationBaseKey(variationBaseOptions.value, indicator.value, series.value)
      : null
  },
  { immediate: true },
)

const selectedBaseOption = computed(() => {
  if (!variationBaseOptions.value.length) return null
  return (
    variationBaseOptions.value.find((opt) => opt.key === selectedBaseKey.value)
    ?? variationBaseOptions.value[0]
    ?? null
  )
})

const variation = computed(() => {
  if (!latest.value || !selectedBaseOption.value) return null
  return latest.value.valor - selectedBaseOption.value.value
})

const variationLabel = computed(() =>
  variation.value !== null
    ? formatVariation(variation.value, indicator.value?.unidadMedida)
    : 'Sin serie histórica',
)

const variationAssessment = computed(() =>
  indicator.value ? assessVariation(variation.value, indicator.value.sentido) : null,
)

const variationCardClass = computed(() => {
  if (!variationAssessment.value) return ''
  if (variationAssessment.value.cls === 'trend--good') return 'detail-metric-card--good'
  if (variationAssessment.value.cls === 'trend--bad') return 'detail-metric-card--bad'
  return 'detail-metric-card--neutral'
})

const variationPeriodText = computed(() => {
  if (!latest.value || !selectedBaseOption.value) return 'Sin datos para comparar'
  return `De ${selectedBaseOption.value.shortLabel} (${formatValue(selectedBaseOption.value.value, indicator.value?.unidadMedida)}) a ${latest.value.anio}`
})

const direction = computed(() => directionInfo(indicator.value?.sentido ?? ''))
const sourceUrl = computed(() => source.value?.url || indicator.value?.fuente.url || '')

const goalProgress = computed(() =>
  indicator.value ? calculateGoalProgress(indicator.value, series.value) : null,
)
const timeRemaining = computed(() =>
  calculateTimeRemaining(2030, data.resumen.fechaActualizacion),
)
const baselineExplanation = computed(() =>
  indicator.value ? explainBaseline(indicator.value) : '',
)
const formulaInfo = computed(() =>
  indicator.value ? explainFormula(indicator.value) : { text: '', isFallback: false },
)
const unitInfo = computed(() =>
  explainUnit(indicator.value?.unidadMedida ?? ''),
)

const progressTagClass = computed(() => {
  if (!goalProgress.value) return 'trend--neutral'
  if (goalProgress.value.tone === 'good') return 'trend--good'
  if (goalProgress.value.tone === 'bad') return 'trend--bad'
  return 'trend--neutral'
})

const progressTagIcon = computed(() => {
  if (!goalProgress.value) return 'schedule'
  if (goalProgress.value.tone === 'good') return 'check_circle'
  if (goalProgress.value.tone === 'bad') return 'warning'
  return 'schedule'
})

const recentSeries = computed(() => [...series.value].reverse())
const visibleObservations = computed(() =>
  observationsExpanded.value ? recentSeries.value : recentSeries.value.slice(0, 3),
)

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
  toast.add({
    severity: 'success',
    summary: 'Archivo listo',
    detail: `Se exportó ${indicator.value.clave}-serie.csv (${rows.length} años).`,
    life: 3200,
  })
}
</script>

<template>
  <section v-if="indicator" class="detail-page">
    <div class="detail-topbar">
      <Button
        label="Volver al catálogo"
        text
        class="back-button"
        @click="goBack"
      >
        <template #icon>
          <AppIcon name="arrow_back" size="sm" />
        </template>
      </Button>
    </div>

    <!-- 1. Contexto del indicador -->
    <section class="surface-card detail-hero">
      <div class="detail-hero__body">
        <span class="section-kicker">{{ indicator.ejeRector || 'Indicador del PVD 2025–2030' }}</span>
        <h1>{{ indicator.nombre }}</h1>
        <p>{{ indicator.descripcion || 'Indicador estratégico de seguimiento del Plan Veracruzano de Desarrollo 2025–2030.' }}</p>
        <div class="detail-hero__meta">
          <span class="detail-hero__code">Clave PVD: {{ indicator.clave }}</span>
          <span v-if="source?.institucion" class="detail-hero__institution">
            <AppIcon name="account_balance" size="xs" />
            Fuente: {{ source.institucion }}
          </span>
        </div>
      </div>

      <div class="detail-hero__badges">
        <div class="detail-hero__status-row">
          <StatusTag :estado="indicator.estadoHistorico" />
          <HelpHint term-key="semaforo" />
        </div>
        <Tag :value="direction.label" class="unit-tag">
          <template #icon>
            <AppIcon :name="direction.icon" size="xs" />
          </template>
        </Tag>
        <Tag
          v-if="indicator.unidadMedida"
          :value="indicator.unidadMedida"
          class="unit-tag"
        >
          <template #icon>
            <AppIcon name="sell" size="xs" />
          </template>
        </Tag>
      </div>
    </section>

    <!-- 2. Resumen ejecutivo: Avance hacia la Meta 2030 y Tiempo restante -->
    <section
      v-if="goalProgress"
      class="surface-card detail-progress-card"
      aria-label="Avance hacia la Meta 2030 y tiempo restante"
    >
      <div class="progress-header">
        <div class="progress-header__main">
          <span class="detail-metric-card__label">
            Avance hacia la Meta 2030
            <HelpHint term-key="porcentajeAvance" />
          </span>
          <div class="progress-headline">
            <strong class="progress-percent">
              {{ goalProgress.percent !== null ? `${formatNumber(goalProgress.percent)} %` : goalProgress.shortLabel }}
            </strong>
            <Tag :value="goalProgress.badgeLabel" :class="['trend-tag', progressTagClass]">
              <template #icon>
                <span class="sem-dot" aria-hidden="true"></span>
                <AppIcon :name="progressTagIcon" size="xs" />
              </template>
            </Tag>
          </div>
        </div>

        <div class="progress-time-box">
          <span class="detail-metric-card__label">
            Tiempo restante
            <HelpHint term-key="tiempoRestante" />
          </span>
          <strong>{{ timeRemaining.label }}</strong>
          <small>Horizonte al cierre de 2030</small>
        </div>
      </div>

      <div
        class="progress-track"
        role="progressbar"
        :aria-valuenow="goalProgress.percent ?? 0"
        aria-valuemin="0"
        aria-valuemax="100"
        :aria-label="`Avance hacia la Meta 2030: ${goalProgress.shortLabel}`"
      >
        <div
          class="progress-fill"
          :class="`progress-fill--${goalProgress.tone}`"
          :style="{ width: `${goalProgress.barPercent}%` }"
        ></div>
      </div>

      <p class="progress-detail">{{ goalProgress.detail }}</p>

      <div class="trajectory-strip" aria-label="Trayectoria de tres hitos del indicador">
        <div class="trajectory-milestone trajectory-milestone--baseline">
          <span class="trajectory-milestone__label">
            Línea base ({{ indicator.lineaBase.anio ?? 's/a' }})
          </span>
          <strong>{{ formatValue(indicator.lineaBase.valor, indicator.unidadMedida) }}</strong>
        </div>

        <div class="trajectory-connector trajectory-connector--to-latest" aria-hidden="true">
          <span class="trajectory-connector__line"></span>
          <span class="trajectory-connector__head"></span>
        </div>

        <div class="trajectory-milestone trajectory-milestone--latest">
          <span class="trajectory-milestone__label">
            Último dato ({{ latest?.anio ?? 'sin serie' }})
          </span>
          <strong>{{ latest ? formatValue(latest.valor, indicator.unidadMedida) : '—' }}</strong>
        </div>

        <div class="trajectory-connector trajectory-connector--to-target" aria-hidden="true">
          <span class="trajectory-connector__line"></span>
          <span class="trajectory-connector__head"></span>
        </div>

        <div class="trajectory-milestone trajectory-milestone--target">
          <span class="trajectory-milestone__label">Meta 2030</span>
          <strong>{{ formatValue(indicator.meta2030, indicator.unidadMedida) }}</strong>
        </div>
      </div>
    </section>

    <!-- 3. Cifras clave + Selector de año base en Variación observada -->
    <section class="detail-metrics" aria-label="Cifras clave del indicador">
      <article class="surface-card detail-metric-card detail-metric-card--baseline">
        <span class="detail-metric-card__label">
          Línea base
          <HelpHint term-key="lineaBase" />
        </span>
        <strong>{{ formatValue(indicator.lineaBase.valor, indicator.unidadMedida) }}</strong>
        <small>{{ baselineExplanation }}</small>
      </article>

      <article class="surface-card detail-metric-card detail-metric-card--latest">
        <span class="detail-metric-card__label">
          Último valor
          <HelpHint term-key="ultimoValor" />
        </span>
        <strong>{{ latest ? formatValue(latest.valor, indicator.unidadMedida) : '—' }}</strong>
        <small>{{ latest ? `Periodo ${latest.anio}` : 'Serie histórica en integración' }}</small>
      </article>

      <article class="surface-card detail-metric-card detail-metric-card--target">
        <span class="detail-metric-card__label">
          Meta 2030
          <HelpHint term-key="meta2030" />
        </span>
        <strong>{{ formatValue(indicator.meta2030, indicator.unidadMedida) }}</strong>
        <small>{{ indicator.meta2030 !== null ? 'Objetivo sexenal del PVD' : 'Sin meta numérica en ficha' }}</small>
      </article>

      <article class="surface-card detail-metric-card" :class="variationCardClass">
        <span class="detail-metric-card__label">
          Variación observada
          <HelpHint term-key="variacionObservada" />
        </span>
        <strong>{{ variationLabel }}</strong>
        <div class="detail-metric-card__foot">
          <Tag
            v-if="variationAssessment"
            :value="variationAssessment.label"
            :class="['trend-tag', variationAssessment.cls]"
          >
            <template #icon>
              <span class="sem-dot" aria-hidden="true"></span>
              <AppIcon :name="variationAssessment.icon" size="xs" />
            </template>
          </Tag>
          <small>{{ variationPeriodText }}</small>
        </div>
        <div v-if="variationBaseOptions.length" class="variation-base-control">
          <label for="variation-base-select">Comparar contra:</label>
          <Select
            inputId="variation-base-select"
            v-model="selectedBaseKey"
            :options="variationBaseOptions"
            optionLabel="label"
            optionValue="key"
            size="small"
            class="variation-base-select"
            aria-label="Seleccionar año o periodo base para calcular la variación observada"
          />
        </div>
      </article>
    </section>

    <!-- 4. Ficha técnica e interpretación (antes de la gráfica) -->
    <section class="surface-card detail-card detail-facts">
      <div class="detail-card__header">
        <div>
          <span class="section-kicker">FICHA TÉCNICA</span>
          <h2>Interpretación y método de cálculo</h2>
        </div>
      </div>

      <dl class="detail-facts__grid">
        <div>
          <dt>
            Sentido
            <HelpHint term-key="sentido" />
          </dt>
          <dd class="direction-value">
            <AppIcon :name="direction.icon" size="sm" />
            <span>
              {{ direction.label }}
              <template v-if="indicator.sentido">({{ indicator.sentido.toLowerCase() }})</template>
            </span>
          </dd>
        </div>

        <div>
          <dt>
            Eje rector
            <HelpHint term-key="ejeRector" />
          </dt>
          <dd>{{ indicator.ejeRector || 'Sin eje asignado en ficha' }}</dd>
        </div>

        <div>
          <dt>Entidad</dt>
          <dd>{{ data.resumen.entidad }}</dd>
        </div>

        <div>
          <dt>Unidad de medida</dt>
          <dd :class="{ 'detail-facts__muted': unitInfo.isFallback }">{{ unitInfo.text }}</dd>
        </div>

        <div class="detail-facts__item--full">
          <dt>
            Fórmula
            <HelpHint term-key="formula" />
          </dt>
          <dd>
            <p class="formula-text" :class="{ 'formula-text--fallback': formulaInfo.isFallback }">
              {{ formulaInfo.text }}
            </p>
            <small v-if="formulaInfo.isFallback" class="formula-badge">
              Explicación automática cuando la ficha del PVD no desglosa ecuación matemática.
            </small>
          </dd>
        </div>
      </dl>
    </section>

    <!-- 5. Gráfica histórica (debajo del contexto) -->
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
        :entity="data.resumen.entidad"
        :reference-date="data.resumen.fechaActualizacion"
      />
    </section>

    <!-- 6. Observaciones por año y Fuente oficial -->
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
              label="Exportar a Excel (CSV)"
              outlined
              size="small"
              @click="exportSeriesCsv"
            >
              <template #icon>
                <AppIcon name="download" size="sm" />
              </template>
            </Button>
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
          iconPos="right"
          text
          :aria-expanded="observationsExpanded"
          @click="observationsExpanded = !observationsExpanded"
        >
          <template #icon>
            <AppIcon :name="observationsExpanded ? 'expand_less' : 'expand_more'" size="sm" />
          </template>
        </Button>
      </section>

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
            <AppIcon name="open_in_new" size="sm" />
          </a>
          <span v-else class="source-unavailable">Enlace no disponible</span>
        </div>
      </section>
    </div>
  </section>

  <section v-else class="not-found-page">
    <div class="surface-card">
      <StatusState
        type="empty"
        title="Indicador no encontrado"
        :message="`La clave “${String(route.params.id)}” no existe o fue actualizada.`"
      >
        <template #actions>
          <Button label="Ir al catálogo" @click="router.push('/indicadores')">
            <template #icon>
              <AppIcon name="monitoring" size="sm" />
            </template>
          </Button>
          <Button label="Ir al inicio" severity="secondary" outlined @click="router.push('/')">
            <template #icon>
              <AppIcon name="home" size="sm" />
            </template>
          </Button>
        </template>
      </StatusState>
    </div>
  </section>
</template>
