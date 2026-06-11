<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span class="loading-text">加载中...</span>
    </div>
    <div v-else-if="!数据.length" class="chart-empty">
      <el-icon class="empty-icon"><DataLine /></el-icon>
      <div class="empty-text">暂无数据</div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { graphic } from 'echarts'
import { Loading, DataLine } from '@element-plus/icons-vue'

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  数据: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
const loading = ref(true)
let chartInstance = null

function 初始化图表() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  更新图表()
}

function 更新图表() {
  if (!chartInstance) return

  if (!props.数据.length) {
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '10%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: [],
        axisLabel: {
          fontSize: 11,
          color: '#909399'
        },
        axisLine: { lineStyle: { color: '#dcdfe6' } }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          fontSize: 11,
          color: '#909399',
          formatter: '¥{value}'
        },
        splitLine: { lineStyle: { color: '#f0f2f5' } }
      },
      series: [
        {
          name: '成交金额',
          type: 'line',
          data: [],
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { width: 3, color: '#377EB8' },
          itemStyle: { color: '#377EB8' },
          areaStyle: {
            color: new graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(55,126,184,0.3)' },
              { offset: 1, color: 'rgba(55,126,184,0.02)' }
            ])
          }
        }
      ]
    }

    chartInstance.setOption(option)
    return
  }

  const xData = props.数据.map(item => item.date)
  const yData = props.数据.map(item => item.amount)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>成交金额: ¥{c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: {
        fontSize: 11,
        color: '#909399'
      },
      axisLine: { lineStyle: { color: '#dcdfe6' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 11,
        color: '#909399',
        formatter: '¥{value}'
      },
      splitLine: { lineStyle: { color: '#f0f2f5' } }
    },
    series: [
      {
        name: '成交金额',
        type: 'line',
        data: yData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 3, color: '#377EB8' },
        itemStyle: { color: '#377EB8' },
        areaStyle: {
          color: new graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(55,126,184,0.3)' },
            { offset: 1, color: 'rgba(55,126,184,0.02)' }
          ])
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

function handleResize() {
  chartInstance?.resize()
}

watch(() => props.数据, () => {
  更新图表()
}, { deep: true })

onMounted(() => {
  setTimeout(() => {
    loading.value = false
    初始化图表()
  }, 300)
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 350px;
  position: relative;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.chart-wrapper:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.12);
}

.chart-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  z-index: 10;
}

.loading-icon {
  font-size: 32px;
  color: #409eff;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: #909399;
  font-size: 14px;
  font-weight: 500;
}

.chart-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  z-index: 10;
}

.empty-icon {
  font-size: 64px;
  color: #c0c4cc;
}

.empty-text {
  color: #909399;
  font-size: 14px;
  font-weight: 500;
}

.chart-container {
  width: 100%;
  height: 100%;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chart-wrapper {
    height: 300px;
  }
}

@media (max-width: 480px) {
  .chart-wrapper {
    height: 250px;
  }
}
</style>
