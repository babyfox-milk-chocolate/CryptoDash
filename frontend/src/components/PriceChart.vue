<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, LineElement, PointElement,
  LinearScale, CategoryScale, Filler, Tooltip,
} from 'chart.js'

// регистрируем только нужные части Chart.js (tree-shaking)
ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Filler, Tooltip)

const props = defineProps({
  prices: { type: Array, required: true },  // [[ts, price], ...]
  up: { type: Boolean, default: true },      // цвет линии по тренду
})

const chartData = computed(() => {
  const color = props.up ? '#34d399' : '#f87171'  // emerald / red
  return {
    labels: props.prices.map(([ts]) =>
      new Date(ts).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
    ),
    datasets: [{
      data: props.prices.map(([, price]) => price),
      borderColor: color,
      backgroundColor: color + '20',  // полупрозрачная заливка под линией
      fill: true,
      tension: 0.3,        // сглаживание линии
      pointRadius: 0,       // без точек — только линия
      borderWidth: 2,
    }],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#6b7280', maxTicksLimit: 6 }, grid: { display: false } },
    y: { ticks: { color: '#6b7280' }, grid: { color: '#37415133' } },
  },
}
</script>

<template>
  <div class="h-64">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>