<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Baseline, HistoricalPoint } from '../../types/contract'

const props = defineProps<{
  points: HistoricalPoint[]
  baseline: Baseline
  target: number | null
  direction: string
}>()
const hoveredYear = ref<number | null>(null)

const width = 760
const height = 315
const padding = { top: 28, right: 28, bottom: 45, left: 58 }
const plotWidth = width - padding.left - padding.right
const plotHeight = height - padding.top - padding.bottom

const values = computed(() => [
  ...props.points.map((point) => point.valor),
  ...(props.baseline.valor === null ? [] : [props.baseline.valor]),
  ...(props.target === null ? [] : [props.target]),
])
const minValue = computed(() => {
  const min = Math.min(...values.value)
  return Math.max(0, Math.floor((min - Math.max(2, (Math.max(...values.value) - min) * .12)) / 5) * 5)
})
const maxValue = computed(() => {
  const max = Math.max(...values.value)
  return Math.ceil((max + Math.max(2, (max - minValue.value) * .12)) / 5) * 5
})
const x = (index: number) => padding.left + (props.points.length <= 1 ? plotWidth / 2 : (index / (props.points.length - 1)) * plotWidth)
const y = (value: number) => padding.top + plotHeight - ((value - minValue.value) / (maxValue.value - minValue.value || 1)) * plotHeight
const linePath = computed(() => props.points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${x(index)} ${y(point.valor)}`).join(' '))
const gridLines = computed(() => Array.from({ length: 5 }, (_, index) => {
  const value = minValue.value + ((maxValue.value - minValue.value) * index) / 4
  return { value: Math.round(value * 10000) / 10000, y: y(value) }
}))
const pointsWithLabels = computed(() => props.points.map((point, index) => ({
  ...point,
  x: x(index),
  y: y(point.valor),
})))
const showPointLabels = computed(() => props.points.length <= 12)
const yearLabelStep = computed(() => Math.max(1, Math.ceil(props.points.length / 8)))
const hoveredPoint = computed(() => pointsWithLabels.value.find((point) => point.anio === hoveredYear.value))
const formatValue = (value: number) => value.toLocaleString('es-MX', {
  maximumFractionDigits: 4,
  minimumFractionDigits: 0,
})
</script>

<template>
  <div v-if="points.length" class="chart-wrap">
    <div class="chart-legend">
      <span><i class="legend-line legend-line--history"></i>Valor observado</span>
      <span v-if="baseline.valor !== null"><i class="legend-line legend-line--baseline"></i>Línea base {{ baseline.anio }}: {{ formatValue(baseline.valor) }}</span>
      <span v-if="target !== null"><i class="legend-line legend-line--target"></i>Meta 2030: {{ formatValue(target) }}</span>
    </div>
    <div class="chart-scroll" @mouseleave="hoveredYear = null">
      <svg :viewBox="`0 0 ${width} ${height}`" role="img" aria-label="Gráfica histórica del indicador">
        <g class="chart-grid">
          <line v-for="line in gridLines" :key="line.value" :x1="padding.left" :x2="width - padding.right" :y1="line.y" :y2="line.y" />
          <text v-for="line in gridLines" :key="`label-${line.value}`" :x="padding.left - 10" :y="line.y + 4" text-anchor="end">{{ formatValue(line.value) }}</text>
        </g>
        <line v-if="baseline.valor !== null" class="chart-reference chart-reference--baseline" :x1="padding.left" :x2="width - padding.right" :y1="y(baseline.valor)" :y2="y(baseline.valor)" />
        <line v-if="target !== null" class="chart-reference chart-reference--target" :x1="padding.left" :x2="width - padding.right" :y1="y(target)" :y2="y(target)" />
        <path class="chart-path" :d="linePath" />
        <g v-for="(point, index) in pointsWithLabels" :key="point.anio">
          <line v-if="hoveredYear === point.anio" class="chart-hover-guide" :x1="point.x" :x2="point.x" :y1="padding.top" :y2="height - padding.bottom" />
          <circle class="chart-point" :class="{ 'chart-point--active': hoveredYear === point.anio }" :cx="point.x" :cy="point.y" r="5" @mouseenter="hoveredYear = point.anio" @focus="hoveredYear = point.anio" @blur="hoveredYear = null" tabindex="0" role="button" :aria-label="`${point.anio}: ${formatValue(point.valor)}`" />
          <text v-if="showPointLabels || hoveredYear === point.anio" class="chart-value" :x="point.x" :y="point.y - 12" text-anchor="middle">{{ formatValue(point.valor) }}</text>
          <text v-if="index % yearLabelStep === 0 || index === pointsWithLabels.length - 1" class="chart-year" :x="point.x" :y="height - 15" text-anchor="middle">{{ point.anio }}</text>
        </g>
        <g v-if="hoveredPoint" class="chart-tooltip" :transform="`translate(${Math.min(hoveredPoint.x + 12, width - 145)} ${Math.max(hoveredPoint.y - 65, 8)})`">
          <rect width="132" height="48" rx="4" />
          <text x="10" y="19">{{ hoveredPoint.anio }}</text>
          <text x="10" y="37">{{ formatValue(hoveredPoint.valor) }}</text>
        </g>
      </svg>
    </div>
    <button v-if="hoveredYear !== null" class="chart-clear" @click="hoveredYear = null">Mostrar todos los valores</button>
    <p class="chart-note">La gráfica muestra únicamente los periodos publicados por la fuente. No se interpolan años faltantes.</p>
  </div>
  <div v-else class="chart-empty">Este indicador aún no cuenta con una serie histórica procesada.</div>
</template>

<style scoped>
.chart-wrap { width: 100%; }
.chart-legend { display: flex; flex-wrap: wrap; gap: 18px; margin-bottom: 12px; color: #6e6e6e; font-size: 12px; }
.chart-legend span { display: inline-flex; align-items: center; gap: 7px; }
.legend-line { width: 20px; height: 3px; display: inline-block; border-radius: 2px; }
.legend-line--history { background: #7a1737; }
.legend-line--baseline { background: #b28854; }
.legend-line--target { background: #267c78; }
.chart-scroll { overflow-x: auto; }
svg { display: block; min-width: 650px; width: 100%; height: auto; }
.chart-grid line { stroke: #ece7e8; stroke-width: 1; }
.chart-grid text { fill: #898387; font-size: 11px; }
.chart-reference { stroke-width: 2; stroke-dasharray: 6 5; }
.chart-reference--baseline { stroke: #b28854; }
.chart-reference--target { stroke: #267c78; }
.chart-path { fill: none; stroke: #7a1737; stroke-linecap: round; stroke-linejoin: round; stroke-width: 3; }
.chart-point { fill: #fff; stroke: #7a1737; stroke-width: 3; cursor: pointer; outline: none; }
.chart-point:hover, .chart-point--active { fill: #b28854; stroke-width: 4; }
.chart-value { fill: #7a1737; font-size: 11px; font-weight: 700; }
.chart-hover-guide { stroke: #b28854; stroke-dasharray: 3 4; stroke-width: 1; }
.chart-tooltip rect { fill: #7a1737; }
.chart-tooltip text { fill: #fff; font-size: 11px; font-weight: 700; }
.chart-clear { margin-top: 5px; padding: 0; border: 0; color: #7a1737; background: none; cursor: pointer; font-size: 11px; font-weight: 700; }
.chart-year { fill: #6e6e6e; font-size: 11px; }
.chart-note { margin: 8px 0 0; color: #858585; font-size: 11px; }
.chart-empty { padding: 55px 20px; color: #6e6e6e; text-align: center; }
</style>
