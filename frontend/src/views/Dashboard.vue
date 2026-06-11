<template>
  <div class="dashboard">
    <div v-loading="loading" class="dashboard-content" element-loading-text="正在加载看板数据..." element-loading-spinner="el-icon-loading" element-loading-background="rgba(255, 255, 255, 0.7)">
      <!-- 欢迎标语 -->
      <div class="welcome-banner">
        <h1 class="welcome-text">欢迎使用房屋出租管理系统</h1>
      </div>

      <!-- 第一部分 - 数据概览 -->
      <el-card class="overview-card" :shadow="'always'">
        <div class="overview-header">
          <span class="overview-title">数据概览</span>
          <div class="overview-actions">
            <el-tooltip content="刷新数据" placement="bottom">
              <el-icon class="action-icon" @click="刷新数据"><Refresh /></el-icon>
            </el-tooltip>
            <el-tooltip content="查看详情" placement="bottom">
              <el-icon class="action-icon" @click="打开详情抽屉"><DataAnalysis /></el-icon>
            </el-tooltip>
          </div>
        </div>
        <el-row :gutter="16" class="stat-row">
          <el-col :xs="24" :sm="12" :md="6">
            <StatCard
              标题="当前房源数"
              :数值="汇总数据.total_houses || 0"
              icon="House"
              图标颜色="#377EB8"
              图标背景色="#E8F4FD"
            />
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <StatCard
              标题="本月成交金额"
              :数值="汇总数据.month_amount || 0"
              icon="Money"
              图标颜色="#FB8072"
              图标背景色="#FDEBE9"
              :是否金额="true"
            />
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <StatCard
              标题="本月成交数量"
              :数值="汇总数据.month_count || 0"
              icon="Document"
              图标颜色="#F4A460"
              图标背景色="#FFF5E6"
            />
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <StatCard
              标题="客户数"
              :数值="汇总数据.total_customers || 0"
              icon="User"
              图标颜色="#66C2A4"
              图标背景色="#EDFAF3"
            />
          </el-col>
        </el-row>
      </el-card>

      <!-- 第二部分 - 成交金额 -->
      <el-card class="section-card" :shadow="'hover'">
        <template #header>
          <span class="section-title">成交金额</span>
        </template>
        <AmountTrendChart :数据="金额趋势数据" />
        <div v-if="最高成交日.date" class="chart-summary">
          <el-icon><Trophy /></el-icon>
          <span>{{ 格式化日期(最高成交日.date) }}成交金额最高 {{ 格式化金额(最高成交日.amount) }}元</span>
        </div>
      </el-card>

      <!-- 第三部分 - 房源分布 -->
      <el-card class="section-card" :shadow="'hover'">
        <template #header>
          <div class="section-header-row">
            <span class="section-title">房源分布</span>
            <el-tag type="success" size="large" effect="plain">
              出租率 {{ 出租率 }}%
            </el-tag>
          </div>
        </template>
        <HouseStatusChart :数据="房源状态数据" />
        <div v-if="房源状态数据 && Object.keys(房源状态数据).length" class="status-summary">
          <span class="status-item">空闲：<b>{{ 房源状态数据.vacant || 0 }}</b>套</span>
          <span class="status-item">已租：<b>{{ 房源状态数据.rented || 0 }}</b>套</span>
          <span class="status-item">即将到期：<b>{{ 房源状态数据.expiring || 0 }}</b>套</span>
        </div>
      </el-card>

      <!-- 第四部分 - 新增客户 + 小区排名 -->
      <el-row :gutter="16" class="dual-section">
        <el-col :xs="24" :md="12">
          <el-card class="section-card" :shadow="'hover'">
            <template #header>
              <span class="section-title">新增客户</span>
            </template>
            <CustomerTrendChart :数据="客户趋势数据" />
            <div v-if="最高客户月.month" class="chart-summary success">
              <el-icon><Trophy /></el-icon>
              <span>{{ 最高客户月.month }}新增客户最高 {{ 最高客户月.count || 0 }}人</span>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-card class="section-card ranking-card" :shadow="'hover'">
            <template #header>
              <span class="section-title">小区排名</span>
            </template>
            <div class="ranking-content">
              <div v-if="小区排名数据.length" class="community-summary">
                <el-icon><Medal /></el-icon>
                <span><b>{{ 小区排名数据[0]?.community }}</b>最多 <b>{{ 小区排名数据[0]?.count }}</b> 套</span>
              </div>
              <el-table :data="小区排名数据" stripe :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }" :border="true">
                <el-table-column type="index" label="排名" width="70" align="center">
                  <template #default="{ $index }">
                    <el-tag
                      :type="$index < 3 ? 'danger' : 'info'"
                      size="small"
                      round
                    >
                      {{ $index + 1 }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="community" label="小区名称" />
                <el-table-column prop="count" label="房源数量" width="100" align="center" />
              </el-table>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 详情抽屉 -->
      <DashboardDrawer
        v-model:visible="详情抽屉可见"
        :看板数据="{
          汇总数据,
          金额趋势数据,
          客户趋势数据,
          房源状态数据,
          小区排名数据,
          最高成交日,
          最高客户月
        }"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Refresh, DataAnalysis, Trophy, Medal } from '@element-plus/icons-vue'
import StatCard from '../components/StatCard.vue'
import AmountTrendChart from '../components/charts/AmountTrendChart.vue'
import CustomerTrendChart from '../components/charts/CustomerTrendChart.vue'
import HouseStatusChart from '../components/charts/HouseStatusChart.vue'
import DashboardDrawer from '../components/DashboardDrawer.vue'
import {
  获取汇总数据,
  获取金额趋势,
  获取客户趋势,
  获取房源状态分布,
  获取小区排名,
  获取最高成交日,
  获取最高客户月
} from '../api/dashboard.js'

const loading = ref(false)
const 详情抽屉可见 = ref(false)
const 汇总数据 = ref({})
const 金额趋势数据 = ref([])
const 客户趋势数据 = ref([])
const 房源状态数据 = ref({})
const 小区排名数据 = ref([])
const 最高成交日 = ref({})
const 最高客户月 = ref({})

const 出租率 = computed(() => {
  const data = 房源状态数据.value
  if (!data) return 0
  const total = (data.vacant || 0) + (data.rented || 0) + (data.expiring || 0)
  if (total === 0) return 0
  return (((data.rented || 0) + (data.expiring || 0)) / total * 100).toFixed(1)
})

function 格式化日期(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

function 格式化金额(amount) {
  if (!amount) return '0'
  return Number(amount).toLocaleString('zh-CN')
}

async function 刷新数据() {
  await 加载所有数据()
}

async function 打开详情抽屉() {
  if (!房源状态数据.value || Object.keys(房源状态数据.value).length === 0) {
    await 加载所有数据()
  }
  详情抽屉可见.value = true
}

onMounted(() => {
  加载所有数据()
})

async function 加载所有数据() {
  loading.value = true
  try {
    const [summary, amountTrend, customerTrend, houseStatus, topCommunities, bestDay, bestMonth] = await Promise.allSettled([
      获取汇总数据(),
      获取金额趋势(),
      获取客户趋势(),
      获取房源状态分布(),
      获取小区排名(),
      获取最高成交日(),
      获取最高客户月()
    ])

    if (summary.status === 'fulfilled') {
      汇总数据.value = summary.value || {}
    }

    if (amountTrend.status === 'fulfilled') {
      金额趋势数据.value = Array.isArray(amountTrend.value) ? amountTrend.value : []
    }

    if (customerTrend.status === 'fulfilled') {
      客户趋势数据.value = Array.isArray(customerTrend.value) ? customerTrend.value : []
    }

    if (houseStatus.status === 'fulfilled') {
      房源状态数据.value = houseStatus.value || {}
    }

    if (topCommunities.status === 'fulfilled') {
      小区排名数据.value = Array.isArray(topCommunities.value) ? topCommunities.value : []
    }

    if (bestDay.status === 'fulfilled') {
      最高成交日.value = bestDay.value || {}
    }

    if (bestMonth.status === 'fulfilled') {
      最高客户月.value = bestMonth.value || {}
    }
  } catch (error) {
    console.error('加载看板数据失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dashboard {
  background-color: #f5f7fa;
  padding: 20px;
  min-height: calc(100vh - 84px);
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎标语 */
.welcome-banner {
  text-align: center;
  padding: 24px 20px 16px;
}

.welcome-text {
  font-size: 26px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 2px;
  margin: 0;
}

/* 第一部分 - 数据概览 */
.overview-card {
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.overview-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.overview-actions {
  display: flex;
  gap: 12px;
}

.action-icon {
  font-size: 20px;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s;
  padding: 4px;
  border-radius: 4px;
}

.action-icon:hover {
  color: #409eff;
  background-color: #ecf5ff;
  transform: rotate(180deg);
}

.stat-row {
  margin: 0;
}

/* 第二、三部分 - 统一卡片样式 */
.section-card {
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.section-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 图表下方总结文字 */
.chart-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  background-color: #FFF5F5;
  border-radius: 6px;
  color: #FB8072;
  font-size: 14px;
  font-weight: 500;
}

.chart-summary .el-icon {
  font-size: 18px;
}

.chart-summary.success {
  background-color: #F0F9EB;
  color: #66C2A4;
}

/* 状态统计 */
.status-summary {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
  font-size: 14px;
  color: #606266;
}

.status-item b {
  color: #303133;
  font-weight: 600;
}

/* 第四部分 - 双栏布局 */
.dual-section {
  margin-bottom: 20px;
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 16px !important;
}

.dual-section .el-col {
  width: 100% !important;
  max-width: 100% !important;
  display: block !important;
}

.dual-section .section-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dual-section .section-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.community-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background-color: #FFF9E6;
  border-radius: 6px;
  color: #E6A23C;
  font-size: 14px;
  font-weight: 500;
}

.community-summary b {
  color: #303133;
}

.ranking-card {
  height: 100%;
}

.ranking-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.ranking-content :deep(.el-table) {
  flex: 1;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .dual-section {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 12px;
  }

  .overview-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .status-summary {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
