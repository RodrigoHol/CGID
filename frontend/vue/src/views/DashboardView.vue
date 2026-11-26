<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { ChartData, ChartOptions, ScriptableContext } from 'chart.js'
import Button from 'primevue/button'
import paisajeVeracruz from '../assets/paisaje-veracruz.jpg'
import BaseChart from '../components/charts/BaseChart.vue'
import AppIcon from '../components/common/AppIcon.vue'
import HelpHint from '../components/common/HelpHint.vue'
import { useFrontendData } from '../composables/useFrontendData'
import { useTheme } from '../composables/useTheme'
import { CATALOGO_TOTAL_INDICADORES } from '../config/site'

const router = useRouter()
const data = useFrontendData()
const { isDark } = useTheme()

const coveragePercent = computed(() => {
  if (!data.resumen.totalIndicadores) return 0
  return Math.round(
    (data.resumen.indicadoresConHistorico / data.resumen.totalIndicadores) * 100,
  )
})

const firstPeriod = computed(() => data.resumen.periodosHistoricos[0] ?? '—')
const lastPeriod = computed(() => data.resumen.periodosHistoricos.at(-1) ?? '—')
const pendingIntegration = computed(() => data.resumen.porEstadoHistorico.fuente_identificada ?? 0)
const pendingReview = computed(() => data.resumen.porEstadoHistorico.pendiente_revision ?? 0)

const heroBackgroundStyle = {
  backgroundImage: `linear-gradient(96deg, rgba(24, 51, 47, 0.92) 0%, rgba(24, 51, 47, 0.78) 44%, rgba(24, 51, 47, 0.18) 78%, rgba(24, 51, 47, 0.04) 100%), url(${paisajeVeracruz})`,
}

// Paleta reactiva para Chart.js según modo claro/oscuro
const chartColors = computed(() => ({
  text: isDark.value ? '#F1F5F9' : '#000000',
  muted: isDark.value ? '#CBD5E1' : '#3A3A3A',
  grid: isDark.value ? '#2E363D' : '#EDE8DF',
  surfaceBorder: isDark.value ? '#181D21' : '#FFFFFF',
  green: isDark.value ? '#22C55E' : '#16A34A',
  amber: isDark.value ? '#F59E0B' : '#D97706',
  red: isDark.value ? '#F87171' : '#DC2626',
  line: isDark.value ? '#E57A99' : '#7A1737',
  pointBg: isDark.value ? '#181D21' : '#FFFFFF',
}))

// 1. Indicadores por Eje Rector (barras horizontales apiladas con semáforo)
interface AxisStat {
  fullName: string
  shortName: string
  ready: number
  integration: number
  review: number
}

function shortenAxisName(name: string): string {
  const cleaned = name.replace(/^\d+\.\s*/, '')
  return cleaned.length > 26 ? `${cleaned.slice(0, 24)}…` : cleaned
}

const axisStats = computed<AxisStat[]>(() => {
  const grouped = new Map<string, AxisStat>()
  for (const ind of data.indicadores) {
    const key = ind.ejeRector || 'Sin eje asignado'
    let entry = grouped.get(key)
    if (!entry) {
      entry = {
        fullName: key,
        shortName: shortenAxisName(key),
        ready: 0,
        integration: 0,
        review: 0,
      }
      grouped.set(key, entry)
    }
    if (ind.estadoHistorico === 'procesado') {
      entry.ready += 1
    } else if (ind.estadoHistorico === 'pendiente_revision') {
      entry.review += 1
    } else {
      entry.integration += 1
    }
  }
  return Array.from(grouped.values()).sort(
    (a, b) => (b.ready + b.integration + b.review) - (a.ready + a.integration + a.review),
  )
})

const axisChartData = computed<ChartData<'bar'>>(() => ({
  labels: axisStats.value.map((item) => item.shortName),
  datasets: [
    {
      label: 'Disponibles',
      data: axisStats.value.map((item) => item.ready),
      backgroundColor: chartColors.value.green,
      borderRadius: 6,
      barThickness: 20,
    },
    {
      label: 'En integración',
      data: axisStats.value.map((item) => item.integration),
      backgroundColor: chartColors.value.amber,
      borderRadius: 6,
      barThickness: 20,
    },
    {
      label: 'En revisión',
      data: axisStats.value.map((item) => item.review),
      backgroundColor: chartColors.value.red,
      borderRadius: 6,
      barThickness: 20,
    },
  ],
}))

const axisChartOptions = computed<ChartOptions<'bar'>>(() => ({
  indexAxis: 'y',
  onHover: (event, elements) => {
    const target = event.native?.target as HTMLElement | null
    if (target) target.style.cursor = elements.length ? 'pointer' : 'default'
  },
  onClick: (_event, elements) => {
    if (!elements.length) return
    const idx = elements[0].index
    const axis = axisStats.value[idx]
    if (axis) {
      router.push({ path: '/indicadores', query: { eje: axis.fullName } })
    }
  },
  plugins: {
    legend: {
      position: 'bottom',
      align: 'start',
      labels: {
        color: chartColors.value.text,
        usePointStyle: true,
        pointStyle: 'circle',
        boxWidth: 10,
        padding: 16,
        font: { size: 13, weight: 600 },
      },
    },
    tooltip: {
      callbacks: {
        title: (items) => {
          const idx = items[0]?.dataIndex ?? 0
          return axisStats.value[idx]?.fullName ?? ''
        },
        afterBody: () => 'Clic para ver este eje en el catálogo',
      },
    },
  },
  scales: {
    x: {
      stacked: true,
      beginAtZero: true,
      grid: { color: chartColors.value.grid },
      border: { display: false },
      ticks: { color: chartColors.value.muted, precision: 0, font: { size: 12.5 } },
    },
    y: {
      stacked: true,
      grid: { display: false },
      border: { display: false },
      ticks: { color: chartColors.value.text, font: { size: 13, weight: 600 } },
    },
  },
}))

// 2. Anillo de avance de integración (semaforizado)
const coverageDoughnutData = computed<ChartData<'doughnut'>>(() => ({
  labels: ['Disponibles (con serie)', 'En integración', 'En revisión'],
  datasets: [
    {
      data: [
        data.resumen.indicadoresConHistorico,
        pendingIntegration.value,
        pendingReview.value,
      ],
      backgroundColor: [
        chartColors.value.green,
        chartColors.value.amber,
        chartColors.value.red,
      ],
      borderColor: chartColors.value.surfaceBorder,
      borderWidth: 2,
      borderRadius: 6,
    },
  ],
}))

const coverageDoughnutOptions = computed<ChartOptions<'doughnut'>>(() => ({
  cutout: '76%',
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.label}: ${ctx.parsed} indicadores`,
      },
    },
  },
}))

// 3. Cobertura histórica por año (área/línea)
const coverageTimeline = computed(() => {
  const counts = new Map<number, number>()
  for (const year of data.resumen.periodosHistoricos) {
    counts.set(year, 0)
  }
  for (const series of Object.values(data.historicos)) {
    const seenYears = new Set<number>()
    for (const pt of series.datos) {
      if (!seenYears.has(pt.anio)) {
        seenYears.add(pt.anio)
        counts.set(pt.anio, (counts.get(pt.anio) ?? 0) + 1)
      }
    }
  }
  return Array.from(counts.entries()).sort((a, b) => a[0] - b[0])
})

const timelineChartData = computed<ChartData<'line'>>(() => ({
  labels: coverageTimeline.value.map(([year]) => String(year)),
  datasets: [
    {
      label: 'Indicadores con dato observado',
      data: coverageTimeline.value.map(([, count]) => count),
      borderColor: chartColors.value.line,
      borderWidth: 2.5,
      tension: 0.35,
      fill: true,
      backgroundColor: (context: ScriptableContext<'line'>) => {
        const { ctx, chartArea } = context.chart
        const baseRgb = isDark.value ? '229, 122, 153' : '122, 23, 55'
        if (!chartArea) return `rgba(${baseRgb}, 0.12)`
        const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
        gradient.addColorStop(0, `rgba(${baseRgb}, 0.24)`)
        gradient.addColorStop(1, `rgba(${baseRgb}, 0.0)`)
        return gradient
      },
      pointRadius: 2.5,
      pointHoverRadius: 6,
      pointBackgroundColor: chartColors.value.pointBg,
      pointBorderColor: chartColors.value.line,
      pointHoverBackgroundColor: '#BA864A',
      pointHoverBorderColor: '#FFFFFF',
      pointHoverBorderWidth: 2,
    },
  ],
}))

const timelineChartOptions = computed<ChartOptions<'line'>>(() => ({
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (items) => `Año ${items[0]?.label ?? ''}`,
        label: (ctx) => ` ${ctx.parsed.y} indicadores publicados`,
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      border: { display: false },
      ticks: { color: chartColors.value.muted, maxTicksLimit: 9, font: { size: 12.5 } },
    },
    y: {
      beginAtZero: true,
      grid: { color: chartColors.value.grid },
      border: { display: false },
      ticks: { color: chartColors.value.muted, precision: 0, font: { size: 12.5 } },
    },
  },
}))

// 4. Principales instituciones fuente (dona)
const SOURCE_PALETTE = ['#7A1737', '#BA864A', '#18332F', '#B94A6B', '#D6B384', '#64748B']

const topSources = computed(() => {
  const counts = new Map<string, number>()
  for (const source of data.fuentes) {
    const inst = source.institucion || 'Otra institución'
    counts.set(inst, (counts.get(inst) ?? 0) + 1)
  }
  const sorted = Array.from(counts.entries()).sort((a, b) => b[1] - a[1])
  const top = sorted.slice(0, 5)
  const rest = sorted.slice(5).reduce((sum, [, n]) => sum + n, 0)
  if (rest > 0) top.push(['Otras fuentes', rest])
  return top.map(([name, count], idx) => ({
    name,
    count,
    color: SOURCE_PALETTE[idx % SOURCE_PALETTE.length],
  }))
})

const sourcesChartData = computed<ChartData<'doughnut'>>(() => ({
  labels: topSources.value.map((s) => s.name),
  datasets: [
    {
      data: topSources.value.map((s) => s.count),
      backgroundColor: topSources.value.map((s) => s.color),
      borderColor: chartColors.value.surfaceBorder,
      borderWidth: 2,
      borderRadius: 4,
    },
  ],
}))

const sourcesChartOptions: ChartOptions<'doughnut'> = {
  cutout: '66%',
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.label}: ${ctx.parsed} indicadores`,
      },
    },
  },
}

// Interpretaciones ejecutivas automáticas para las gráficas del tablero (C06)
const axisChartInsight = computed(() => {
  if (!axisStats.value.length) return ''
  const topAxis = axisStats.value[0]
  const topTotal = topAxis.ready + topAxis.integration + topAxis.review
  const bestCoverage = [...axisStats.value].sort((a, b) => {
    const rateA = a.ready / Math.max(1, a.ready + a.integration + a.review)
    const rateB = b.ready / Math.max(1, b.ready + b.integration + b.review)
    return rateB - rateA
  })[0]
  const bestTotal = bestCoverage.ready + bestCoverage.integration + bestCoverage.review
  const bestRate = Math.round((bestCoverage.ready / Math.max(1, bestTotal)) * 100)
  return `${topAxis.shortName} concentra ${topTotal} indicadores; ${bestCoverage.shortName} tiene la mayor disponibilidad (${bestRate}% con serie lista).`
})

const coverageRingInsight = computed(
  () =>
    `${coveragePercent.value}% del catálogo ya tiene cifras integradas; ${pendingIntegration.value} están en integración y ${pendingReview.value} en revisión.`,
)

const timelineChartInsight = computed(() => {
  if (!coverageTimeline.value.length) return ''
  let peakYear = coverageTimeline.value[0][0]
  let peakCount = coverageTimeline.value[0][1]
  for (const [year, count] of coverageTimeline.value) {
    if (count > peakCount) {
      peakYear = year
      peakCount = count
    }
  }
  const [latestYear, latestCount] = coverageTimeline.value[coverageTimeline.value.length - 1]
  return `La mayor cobertura histórica se registró en ${peakYear} (${peakCount} indicadores) y en ${latestYear} hay ${latestCount} con dato publicado.`
})

const sourcesChartInsight = computed(() => {
  if (!topSources.value.length) return ''
  const mainSource = topSources.value[0]
  const share = Math.round((mainSource.count / Math.max(1, data.fuentes.length)) * 100)
  return `${mainSource.name} respalda ${mainSource.count} indicadores (${share}% del catálogo oficial).`
})
</script>

<template>
  <div class="dashboard-bento">
    <!-- Banner Hero limpio con El Tajín -->
    <section class="surface-card tajin-hero" :style="heroBackgroundStyle">
      <div class="tajin-hero__content">
        <span class="tajin-hero__badge">
          <AppIcon name="verified" size="sm" filled />
          <span>Plan Veracruzano de Desarrollo 2025–2030</span>
        </span>
        <h2>Indicadores claros para el desarrollo de Veracruz</h2>
        <p>
          Consulta cifras históricas, metas al 2030 y fuentes oficiales en un formato sencillo
          y listo para el análisis económico y presupuestal.
        </p>
        <div class="tajin-hero__actions">
          <Button
            label="Explorar indicadores"
            iconPos="right"
            @click="router.push('/indicadores')"
          >
            <template #icon>
              <AppIcon name="arrow_forward" size="sm" />
            </template>
          </Button>
          <RouterLink class="tajin-hero__link" to="/acerca">
            <AppIcon name="menu_book" size="sm" />
            <span>¿Cómo leer el catálogo?</span>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Guía rápida de semáforo para reducir carga cognitiva -->
    <div class="surface-card semaphore-bar" aria-label="Significado de colores del semáforo">
      <span class="semaphore-bar__title">
        Semáforo de disponibilidad
        <HelpHint term-key="semaforo" />
      </span>
      <span class="semaphore-item semaphore-item--green">
        <span class="sem-dot" aria-hidden="true"></span>
        <strong>Verde:</strong> Datos disponibles ({{ data.resumen.indicadoresConHistorico }})
      </span>
      <span class="semaphore-item semaphore-item--amber">
        <span class="sem-dot" aria-hidden="true"></span>
        <strong>Ámbar:</strong> En integración ({{ pendingIntegration }})
      </span>
      <span class="semaphore-item semaphore-item--red">
        <span class="sem-dot" aria-hidden="true"></span>
        <strong>Rojo:</strong> En revisión ({{ pendingReview }})
      </span>
    </div>

    <!-- Fila de 4 tarjetas KPI -->
    <section class="kpi-grid" aria-label="Resumen ejecutivo del catálogo">
      <article class="surface-card kpi-card">
        <div class="kpi-card__top">
          <span class="kpi-card__icon kpi-card__icon--primary">
            <AppIcon name="inventory_2" size="md" />
          </span>
          <HelpHint term-key="totalCatalogo" />
        </div>
        <strong class="kpi-card__value">{{ CATALOGO_TOTAL_INDICADORES }}</strong>
        <span class="kpi-card__label">Total en catálogo PVD</span>
        <small class="kpi-card__meta">
          {{ data.resumen.indicadoresConMeta2030 }} con meta 2030 definida
        </small>
      </article>

      <RouterLink class="surface-card kpi-card kpi-card--interactive kpi-card--green" to="/indicadores?estado=procesado">
        <div class="kpi-card__top">
          <span class="kpi-card__icon kpi-card__icon--green">
            <AppIcon name="check_circle" size="md" />
          </span>
          <HelpHint term-key="conSerieHistorica" />
        </div>
        <strong class="kpi-card__value kpi-card__value--green">{{ data.resumen.indicadoresConHistorico }}</strong>
        <span class="kpi-card__label">Datos disponibles</span>
        <small class="kpi-card__meta kpi-card__meta--green">Listos para consultar y exportar</small>
      </RouterLink>

      <RouterLink class="surface-card kpi-card kpi-card--interactive kpi-card--amber" to="/indicadores?estado=fuente_identificada">
        <div class="kpi-card__top">
          <span class="kpi-card__icon kpi-card__icon--amber">
            <AppIcon name="schedule" size="md" />
          </span>
          <HelpHint term-key="enIntegracion" />
        </div>
        <strong class="kpi-card__value kpi-card__value--amber">{{ pendingIntegration }}</strong>
        <span class="kpi-card__label">En integración</span>
        <small class="kpi-card__meta">
          Más {{ pendingReview }} en revisión documental
        </small>
      </RouterLink>

      <article class="surface-card kpi-card">
        <div class="kpi-card__top">
          <span class="kpi-card__icon kpi-card__icon--neutral">
            <AppIcon name="date_range" size="md" />
          </span>
          <HelpHint term-key="serieHistorica" />
        </div>
        <strong class="kpi-card__value">{{ firstPeriod }}–{{ lastPeriod }}</strong>
        <span class="kpi-card__label">Periodo cubierto</span>
        <small class="kpi-card__meta">{{ data.resumen.periodosHistoricos.length }} años con registros</small>
      </article>
    </section>

    <!-- Fila Bento Principal: Ejes Rectores + Avance circular -->
    <section class="bento-row bento-row--primary">
      <article class="surface-card bento-card">
        <div class="bento-card__header">
          <div>
            <span class="section-kicker">DISTRIBUCIÓN POR TEMA</span>
            <h3 class="bento-card__title-inline">
              Indicadores por Eje Rector
              <HelpHint term-key="ejeRector" />
            </h3>
          </div>
          <span class="bento-chip">Clic en una barra para filtrar</span>
        </div>
        <BaseChart
          type="bar"
          :data="axisChartData"
          :options="axisChartOptions"
          :height="285"
          aria-label="Distribución de indicadores por Eje Rector del Plan Veracruzano de Desarrollo"
        />
        <div v-if="axisChartInsight" class="chart-insight">
          <span class="chart-insight__icon" aria-hidden="true">
            <AppIcon name="insights" size="sm" />
          </span>
          <p class="chart-insight__text">
            {{ axisChartInsight }}
          </p>
        </div>
      </article>

      <article class="surface-card bento-card bento-card--centered">
        <div class="bento-card__header bento-card__header--stack">
          <span class="section-kicker">AVANCE GENERAL</span>
          <h3>Disponibilidad de datos</h3>
        </div>

        <div class="ring-wrap">
          <BaseChart
            type="doughnut"
            :data="coverageDoughnutData"
            :options="coverageDoughnutOptions"
            :height="195"
            aria-label="Porcentaje de indicadores con serie histórica disponible"
          />
          <div class="ring-center" aria-hidden="true">
            <strong>{{ coveragePercent }}%</strong>
            <span>disponible</span>
          </div>
        </div>

        <p class="ring-summary">
          {{ coverageRingInsight }}
        </p>

        <Button
          label="Ver todos los indicadores"
          class="ring-cta"
          @click="router.push('/indicadores')"
        >
          <template #icon>
            <AppIcon name="monitoring" size="sm" />
          </template>
        </Button>
      </article>
    </section>

    <!-- Fila Bento Secundaria: Cobertura temporal + Fuentes principales -->
    <section class="bento-row bento-row--secondary">
      <article class="surface-card bento-card">
        <div class="bento-card__header">
          <div>
            <span class="section-kicker">HISTORIAL ANUAL</span>
            <h3>Indicadores con cifras por año</h3>
          </div>
          <span class="bento-chip">{{ firstPeriod }}–{{ lastPeriod }}</span>
        </div>
        <BaseChart
          type="line"
          :data="timelineChartData"
          :options="timelineChartOptions"
          :height="235"
          aria-label="Cantidad de indicadores con datos observados por año"
        />
        <div v-if="timelineChartInsight" class="chart-insight">
          <span class="chart-insight__icon" aria-hidden="true">
            <AppIcon name="insights" size="sm" />
          </span>
          <p class="chart-insight__text">
            {{ timelineChartInsight }}
          </p>
        </div>
      </article>

      <article class="surface-card bento-card">
        <div class="bento-card__header">
          <div>
            <span class="section-kicker">ORIGEN OFICIAL</span>
            <h3>Principales instituciones</h3>
          </div>
          <RouterLink class="bento-link" to="/fuentes">
            <span>Ver todas</span>
            <AppIcon name="arrow_forward" size="xs" />
          </RouterLink>
        </div>

        <div class="sources-donut-layout">
          <div class="sources-donut-box">
            <BaseChart
              type="doughnut"
              :data="sourcesChartData"
              :options="sourcesChartOptions"
              :height="180"
              aria-label="Distribución de indicadores por institución fuente"
            />
          </div>
          <ul class="sources-legend">
            <li v-for="src in topSources" :key="src.name">
              <span class="sources-legend__dot" :style="{ background: src.color }" aria-hidden="true"></span>
              <span class="sources-legend__name">{{ src.name }}</span>
              <strong>{{ src.count }}</strong>
            </li>
          </ul>
        </div>

        <div v-if="sourcesChartInsight" class="chart-insight">
          <span class="chart-insight__icon" aria-hidden="true">
            <AppIcon name="account_balance" size="sm" />
          </span>
          <p class="chart-insight__text">
            {{ sourcesChartInsight }}
          </p>
        </div>
      </article>
    </section>

    <!-- Accesos rápidos -->
    <section class="explore-grid" aria-label="Accesos directos">
      <RouterLink class="surface-card explore-card" to="/indicadores">
        <div class="explore-card__icon explore-card__icon--primary" aria-hidden="true">
          <AppIcon name="manage_search" size="lg" />
        </div>
        <div class="explore-card__body">
          <h3>Catálogo y descarga</h3>
          <p>Filtra por tema o semáforo y exporta las tablas a Excel.</p>
        </div>
      </RouterLink>

      <RouterLink class="surface-card explore-card" to="/fuentes">
        <div class="explore-card__icon explore-card__icon--forest" aria-hidden="true">
          <AppIcon name="database" size="lg" />
        </div>
        <div class="explore-card__body">
          <h3>Fuentes oficiales</h3>
          <p>Consulta qué organismo genera cada cifra y su enlace directo.</p>
        </div>
      </RouterLink>

      <RouterLink class="surface-card explore-card" to="/acerca">
        <div class="explore-card__icon explore-card__icon--gold" aria-hidden="true">
          <AppIcon name="menu_book" size="lg" />
        </div>
        <div class="explore-card__body">
          <h3>Guía de lectura</h3>
          <p>Aprende cómo interpretar la línea base, metas y tendencias.</p>
        </div>
      </RouterLink>
    </section>
  </div>
</template>
