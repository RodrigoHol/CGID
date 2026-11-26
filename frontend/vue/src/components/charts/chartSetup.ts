import {
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  DoughnutController,
  Filler,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from 'chart.js'

Chart.register(
  ArcElement,
  BarElement,
  LineElement,
  PointElement,
  DoughnutController,
  BarController,
  LineController,
  CategoryScale,
  LinearScale,
  Filler,
  Tooltip,
  Legend,
)

Chart.defaults.font.family = 'Inter, Arial, sans-serif'
Chart.defaults.color = '#5B6461'
Chart.defaults.plugins.tooltip.backgroundColor = '#18332F'
Chart.defaults.plugins.tooltip.titleColor = '#FFFFFF'
Chart.defaults.plugins.tooltip.bodyColor = '#F5F2EC'
Chart.defaults.plugins.tooltip.padding = 10
Chart.defaults.plugins.tooltip.cornerRadius = 10
Chart.defaults.plugins.tooltip.displayColors = true

export { Chart }
