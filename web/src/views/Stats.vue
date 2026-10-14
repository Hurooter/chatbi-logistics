<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { request } from '../api'

const error = ref('')
const pieEl = ref(null)
const barEl = ref(null)
const lineEl = ref(null)
const charts = []

function draw(el, option) {
  const c = echarts.init(el)
  c.setOption(option)
  charts.push(c)
}

function onResize() {
  charts.forEach((c) => c.resize())
}

onMounted(async () => {
  window.addEventListener('resize', onResize)
  try {
    const rows = await request('/stats/warehouses')

    // 1) 各仓库存占比（饼图）
    draw(pieEl.value, {
      tooltip: { trigger: 'item', formatter: '{b}<br/>{c} 件（{d}%）' },
      legend: { bottom: 0, type: 'scroll' },
      series: [{
        type: 'pie',
        radius: ['42%', '66%'],
        center: ['50%', '45%'],
        itemStyle: { borderColor: '#fff', borderWidth: 2 },
        label: { formatter: '{b}\n{d}%', fontSize: 11 },
        data: rows.map((r) => ({ name: r.name, value: r.stock_qty })),
      }],
    })

    // 2) 各仓低于安全库存的 SKU 数（柱状图，按数量升序）
    const byLow = [...rows].sort((a, b) => a.low_cnt - b.low_cnt)
    draw(barEl.value, {
      grid: { left: 76, right: 24, top: 16, bottom: 24 },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'value', splitLine: { lineStyle: { color: '#eef0f5' } } },
      yAxis: { type: 'category', data: byLow.map((r) => r.name) },
      series: [{
        type: 'bar',
        barWidth: '58%',
        itemStyle: { color: '#f59e0b', borderRadius: [0, 4, 4, 0] },
        label: { show: true, position: 'right', fontSize: 11 },
        data: byLow.map((r) => r.low_cnt),
      }],
    })

    // 3) 近半年入库 / 出库趋势（折线图）
    const trend = await request('/stats/trend')
    draw(lineEl.value, {
      grid: { left: 70, right: 24, top: 24, bottom: 48 },
      tooltip: { trigger: 'axis' },
      legend: { data: ['入库量', '出库量'], bottom: 0 },
      xAxis: { type: 'category', boundaryGap: false, data: trend.map((t) => t.month) },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#eef0f5' } } },
      series: [
        {
          name: '入库量', type: 'line', smooth: true,
          itemStyle: { color: '#4f46e5' },
          areaStyle: { opacity: .08 },
          data: trend.map((t) => t.inbound),
        },
        {
          name: '出库量', type: 'line', smooth: true,
          itemStyle: { color: '#10b981' },
          areaStyle: { opacity: .08 },
          data: trend.map((t) => t.outbound),
        },
      ],
    })
  } catch (e) {
    error.value = e.message
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  charts.forEach((c) => c.dispose())
})
</script>

<template>
  <div class="stats">
    <header class="head">
      <h1>仓库统计</h1>
      <p class="muted">各仓库库存与运营概况一览</p>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="grid">
      <section class="card chart-card">
        <h3>各仓库存占比</h3>
        <div ref="pieEl" class="chart"></div>
      </section>

      <section class="card chart-card">
        <h3>各仓低于安全库存的 SKU 数</h3>
        <div ref="barEl" class="chart"></div>
      </section>

      <section class="card chart-card wide">
        <h3>近半年入库 / 出库趋势</h3>
        <div ref="lineEl" class="chart"></div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.stats { max-width: 1180px; margin: 0 auto; }

.head { margin-bottom: 20px; }
.head h1 { margin: 0 0 4px; font-size: 24px; }

.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.chart-card { padding: 18px 18px 6px; }
.chart-card h3 { margin: 0 0 10px; font-size: 15px; }
.chart { width: 100%; height: 320px; }
.wide { grid-column: 1 / -1; }

@media (max-width: 900px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
