<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="chart-loading">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span class="loading-text">加载中...</span>
    </div>
    <div v-else-if="isEmpty" class="chart-empty">
      <el-icon class="empty-icon"><DataLine /></el-icon>
      <div class="empty-text">暂无数据</div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { Loading, DataLine } from '@element-plus/icons-vue'

echarts.use([PieChart, LegendComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  数据: {
    type: Object,
    default: () => ({})
  }
})

const chartRef = ref(null)
const loading = ref(true)
let chartInstance = null

const isEmpty = computed(() => {
  const { vacant = 0, rented = 0, expiring = 0 } = props.数据
  return vacant === 0 && rented === 0 && expiring === 0
})

function 初始化图表() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  更新图表()
}

function 更新图表() {
  if (!chartInstance) return

  if (isEmpty.value) {
    const option = {
      tooltip: {
        trigger: 'item'
      },
      legend: {
        bottom: '5%',
        itemWidth: 12,
        itemHeight: 12,
        textStyle: { fontSize: 12, color: '#606266' }
      },
      color: ['#67c23a', '#909399', '#e6a23c'],
      series: [
        {
          name: '房源分布',
          type: 'pie',
          radius: ['45%', '70%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 6,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}\n{c}套',
            fontSize: 12
          },
          data: [
            { value: 0, name: '空闲' },
            { value: 0, name: '已租' },
            { value: 0, name: '即将到期' }
          ]
        }
      ]
    }
    chartInstance.setOption(option)
    return
  }

  const { vacant = 0, rented = 0, expiring = 0 } = props.数据

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 套 ({d}%)'
    },
    legend: {
      bottom: '5%',
      itemWidth: 12,
      itemHeight: 12,
      textStyle: { fontSize: 12, color: '#606266' }
    },
    color: ['#67c23a', '#909399', '#e6a23c'],
    series: [
      {
        name: '房源分布',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}套',
          fontSize: 12
        },
        data: [
          { value: vacant, name: '空闲' },
          { value: rented, name: '已租' },
          { value: expiring, name: '即将到期' }
        ]
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
