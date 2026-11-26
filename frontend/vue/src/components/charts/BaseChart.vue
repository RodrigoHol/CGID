<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { ChartConfiguration, ChartData, ChartOptions, Plugin } from 'chart.js'
import { Chart } from './chartSetup'

type SupportedChartType = 'doughnut' | 'bar' | 'line'

const props = withDefaults(
  defineProps<{
    type: SupportedChartType
    data: ChartData<SupportedChartType>
    options?: ChartOptions<SupportedChartType>
    plugins?: Plugin<SupportedChartType>[]
    height?: number | string
    ariaLabel?: string
  }>(),
  {
    options: () => ({}),
    plugins: () => [],
    height: 240,
    ariaLabel: 'Gráfica estadística',
  },
)

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart<SupportedChartType> | null = null

const containerStyle = computed(() => ({
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
}))

function cloneData(source: ChartData<SupportedChartType>): ChartData<SupportedChartType> {
  return {
    labels: source.labels ? [...source.labels] : [],
    datasets: source.datasets.map((dataset) => ({ ...dataset })),
  }
}

function renderChart() {
  const canvas = canvasRef.value
  if (!canvas) return

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const config: ChartConfiguration<SupportedChartType> = {
    type: props.type,
    data: cloneData(props.data),
    options: {
      responsive: true,
      maintainAspectRatio: false,
      ...props.options,
    },
    plugins: props.plugins,
  }

  chartInstance = new Chart(canvas, config)
}

onMounted(() => {
  renderChart()
})

watch(
  [() => props.type, () => props.data, () => props.options],
  ([nextType], [prevType]) => {
    if (!chartInstance || nextType !== prevType) {
      renderChart()
      return
    }
    chartInstance.data = cloneData(props.data)
    chartInstance.options = {
      responsive: true,
      maintainAspectRatio: false,
      ...props.options,
    }
    chartInstance.update()
  },
  { deep: true },
)

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<template>
  <div class="chart-canvas-box" :style="containerStyle">
    <canvas ref="canvasRef" role="img" :aria-label="ariaLabel"></canvas>
  </div>
</template>
