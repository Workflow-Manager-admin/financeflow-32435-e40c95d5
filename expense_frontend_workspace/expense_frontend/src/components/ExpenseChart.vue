<template>
  <div>
    <Chart
      :chart-data="chartData"
      :chart-options="chartOptions"
      :type="type || 'bar'"
      style="height:320px"
    />
  </div>
</template>

<script setup lang="ts">
import Chart from 'vue3-chart-v2/lib/chart'

interface ChartProps {
  chartData: Record<string, unknown>
  chartOptions?: Record<string, unknown>
  type?: string // 'bar' or 'pie'
}
const { chartData, chartOptions, type } = defineProps<ChartProps>()
</script>
