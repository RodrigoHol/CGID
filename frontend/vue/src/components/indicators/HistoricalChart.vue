<script setup lang="ts">
import { computed } from 'vue'
import type { ChartData, ChartOptions, Plugin, ScriptableContext } from 'chart.js'
import { useTheme } from '../../composables/useTheme'
import type { Baseline, HistoricalPoint } from '../../types/contract'
import { formatNumber, formatValue } from '../../utils/labels'
import BaseChart from '../charts/BaseChart.vue'
import AppIcon from '../common/AppIcon.vue'

const props = defineProps<{
  points: HistoricalPoint[]
  baseline: Baseline
  target: number | null
  direction: string
  unit?: string
}>()

const { isDark } = useTheme()

const bounds = computed(() => {
  const vals = [
    ...props.points.map((p) => p.valor),
    ...(props.baseline.valor === null ? [] : [props.baseline.valor]),
    ...(props.target === null ? [] : [props.target]),
  ]
  if (!vals.length) return { min: 0, max: 100 }
  const minVal = Math.min(...vals)
  const maxVal = Math.max(...vals)
  const span = Math.max(maxVal - minVal, 2)
  return {
    min: minVal >= 0 ? Math.max(0, minVal - span * 0.14) : minVal - span * 0.14,
    max: maxVal + span * 0.14,
  }
})

const lineColor = computed(() => (isDark.value ? '#E57A99' : '#7A1737'))
const baselineColor = computed(() => (isDark.value ? '#F59E0B' : '#BA864A'))
const targetColor = computed(() => (isDark.value ? '#22C55E' : '#18332F'))

const chartData = computed<ChartData<'line'>>(() => ({
  labels: props.points.map((p) => String(p.anio)),
  datasets: [
    {
      label: 'Valor observado',
      data: props.points.map((p) => p.valor),
      borderColor: lineColor.value,
      borderWidth: 3,
      tension: 0.28,
      fill: true,
      backgroundColor: (context: ScriptableContext<'line'>) => {
        const { ctx, chartArea } = context.chart
        const baseRgb = isDark.value ? '229, 122, 153' : '122, 23, 55'
        if (!chartArea) return `rgba(${baseRgb}, 0.12)`
        const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
        gradient.addColorStop(0, `rgba(${baseRgb}, 0.22)`)
        gradient.addColorStop(1, `rgba(${baseRgb}, 0.0)`)
        return gradient
      },
      pointRadius: 5.5,
      pointHoverRadius: 7.5,
      pointBackgroundColor: isDark.value ? '#181D21' : '#FFFFFF',
      pointBorderColor: lineColor.value,
      pointBorderWidth: 2.5,
      pointHoverBackgroundColor: '#BA864A',
      pointHoverBorderColor: '#FFFFFF',
      pointHoverBorderWidth: 2,
    },
  ],
}))

const chartOptions = computed<ChartOptions<'line'>>(() => ({
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (items) => `Periodo ${items[0]?.label ?? ''}`,
        label: (ctx) => ` Valor observado: ${formatValue(ctx.parsed.y, props.unit)}`,
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      border: { display: false },
      ticks: {
        color: isDark.value ? '#CBD5E1' : '#111111',
        maxRotation: 0,
        autoSkipPadding: 14,
        font: { size: 13, weight: 600 },
      },
    },
    y: {
      suggestedMin: bounds.value.min,
      suggestedMax: bounds.value.max,
      grid: { color: isDark.value ? '#2E363D' : '#EAE4D9' },
      border: { display: false },
      ticks: {
        color: isDark.value ? '#CBD5E1' : '#111111',
        font: { size: 13 },
        callback: (value) => formatNumber(Number(value)),
      },
    },
  },
}))

const referenceLinesPlugin: Plugin<'line'> = {
  id: 'cgidReferenceLines',
  afterDatasetsDraw(chart) {
    const { ctx, chartArea, scales } = chart
    const yScale = scales.y
    if (!chartArea || !yScale) return

    const drawRef = (val: number | null, color: string, label: string, alignTop: boolean) => {
      if (val === null || Number.isNaN(val)) return
      const yPos = yScale.getPixelForValue(val)
      if (yPos < chartArea.top - 4 || yPos > chartArea.bottom + 4) return

      ctx.save()
      ctx.beginPath()
      ctx.setLineDash([6, 5])
      ctx.lineWidth = 2
      ctx.strokeStyle = color
      ctx.moveTo(chartArea.left, yPos)
      ctx.lineTo(chartArea.right, yPos)
      ctx.stroke()

      ctx.setLineDash([])
      ctx.font = '700 12px Inter, Arial, sans-serif'
      const textWidth = ctx.measureText(label).width
      const pillW = textWidth + 14
      const pillH = 22
      const pillX = chartArea.right - pillW
      const pillY = alignTop ? Math.max(chartArea.top, yPos - pillH - 4) : Math.min(chartArea.bottom - pillH, yPos + 4)

      ctx.fillStyle = color
      ctx.beginPath()
      ctx.roundRect(pillX, pillY, pillW, pillH, 6)
      ctx.fill()

      ctx.fillStyle = '#FFFFFF'
      ctx.textBaseline = 'middle'
      ctx.fillText(label, pillX + 7, pillY + pillH / 2)
      ctx.restore()
    }

    drawRef(props.baseline.valor, baselineColor.value, 'Línea base', false)
    drawRef(props.target, targetColor.value, 'Meta 2030', true)
  },
}

const chartAriaLabel = computed(() => {
  if (!props.points.length) return 'Gráfica histórica del indicador sin datos'
  const first = props.points[0]
  const last = props.points[props.points.length - 1]
  return `Serie histórica de ${first.anio} (${formatValue(first.valor, props.unit)}) a ${last.anio} (${formatValue(last.valor, props.unit)}), con ${props.points.length} observaciones.`
})
</script>

<template>
  <div v-if="points.length" class="chart-wrap">
    <div class="chart-legend">
      <span><i class="legend-line legend-line--history" aria-hidden="true"></i>Valor observado</span>
      <span v-if="baseline.valor !== null">
        <i class="legend-line legend-line--baseline" aria-hidden="true"></i>
        Línea base {{ baseline.anio }}: {{ formatValue(baseline.valor, unit) }}
      </span>
      <span v-if="target !== null">
        <i class="legend-line legend-line--target" aria-hidden="true"></i>
        Meta 2030: {{ formatValue(target, unit) }}
      </span>
    </div>

    <BaseChart
      type="line"
      :data="chartData"
      :options="chartOptions"
      :plugins="[referenceLinesPlugin]"
      :height="310"
      :aria-label="chartAriaLabel"
    />

    <p class="chart-note">
      La gráfica muestra únicamente los años con dato oficial publicado. No se estiman ni rellenan años faltantes.
    </p>
  </div>
  <div v-else class="chart-empty">
    <span class="chart-empty__icon" aria-hidden="true">
      <AppIcon name="show_chart" size="lg" />
    </span>
    <strong>Cifras históricas en proceso de integración</strong>
    <p>
      Este indicador ya cuenta con ficha técnica y fuente oficial. Puedes consultar el documento original
      en la sección de fuente de información al final de esta página.
    </p>
  </div>
</template>

<style scoped>
.chart-wrap { width: 100%; }
.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 14px;
  color: var(--color-text);
  font-size: 14px;
  font-weight: 600;
}
.chart-legend span { display: inline-flex; align-items: center; gap: 8px; }
.legend-line { width: 22px; height: 4px; display: inline-block; border-radius: 2px; }
.legend-line--history { background: var(--color-primary); }
.legend-line--baseline { background: var(--color-secondary); }
.legend-line--target { background: var(--sem-green-solid); }
.chart-note { margin: 14px 0 0; color: var(--color-muted); font-size: 14px; }
.chart-empty {
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 40px 24px;
  border-radius: var(--radius-md);
  background: var(--color-ivory-light);
  color: var(--color-muted);
  text-align: center;
}
.chart-empty__icon {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  background: var(--sem-amber-bg);
  color: var(--sem-amber-text);
}
.chart-empty strong {
  color: var(--color-ink);
  font-size: 17px;
}
.chart-empty p {
  margin: 0;
  max-width: 520px;
  font-size: 15px;
  line-height: 1.6;
}
</style>
