<template>
  <el-drawer
    v-model="drawerVisible"
    direction="rtl"
    size="80%"
    title="看板数据详情"
    :destroy-on-close="true"
  >
    <div class="drawer-content">
      <!-- 1. 房源分布统计 -->
      <div class="table-section">
        <h3 class="section-title">房源分布统计</h3>
        <el-table :data="房源分布表格数据" stripe border style="width: 100%" :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }">
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column prop="count" label="数量" align="center" />
        </el-table>
      </div>

      <!-- 2. 成交金额明细 -->
      <div class="table-section">
        <h3 class="section-title">成交金额明细（最近15天）</h3>
        <el-table :data="成交金额表格数据" stripe border style="width: 100%" :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }">
          <el-table-column prop="date" label="日期" width="150" />
          <el-table-column prop="amount" label="金额（元）" align="right">
            <template #default="{ row }">
              {{ Number(row.amount).toLocaleString('zh-CN') }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 3. 新增客户明细 -->
      <div class="table-section">
        <h3 class="section-title">新增客户明细（最近7个月）</h3>
        <el-table :data="新增客户表格数据" stripe border style="width: 100%" :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }">
          <el-table-column prop="month" label="年月" width="120" />
          <el-table-column prop="count" label="人数" align="center" />
        </el-table>
      </div>

      <!-- 4. 小区排名 -->
      <div class="table-section">
        <h3 class="section-title">小区排名（前5）</h3>
        <el-table :data="小区排名表格数据" stripe border style="width: 100%" :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }">
          <el-table-column type="index" label="排名" width="70" align="center">
            <template #default="{ $index }">
              <el-tag :type="$index < 3 ? 'danger' : 'info'" size="small" round>
                {{ $index + 1 }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="community" label="小区名称" />
          <el-table-column prop="count" label="房源数量" align="center" />
        </el-table>
      </div>

      <!-- 5. 最高成交日 -->
      <div class="table-section">
        <h3 class="section-title">最高成交日</h3>
        <el-table :data="最高成交日表格数据" stripe border style="width: 100%" :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }">
          <el-table-column prop="date" label="日期" width="180" />
          <el-table-column prop="amount" label="金额（元）" align="right">
            <template #default="{ row }">
              {{ Number(row.amount).toLocaleString('zh-CN') }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 6. 最高新增客户月 -->
      <div class="table-section">
        <h3 class="section-title">最高新增客户月</h3>
        <el-table :data="最高客户月表格数据" stripe border style="width: 100%" :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }">
          <el-table-column prop="month" label="月份" width="150" />
          <el-table-column prop="count" label="人数" align="center" />
        </el-table>
      </div>

      <!-- 关闭按钮 -->
      <div class="drawer-footer">
        <el-button type="primary" @click="关闭抽屉">关闭</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  看板数据: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible'])

const drawerVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const 房源分布表格数据 = computed(() => {
  const data = props.看板数据.房源状态数据 || {}
  return [
    { status: '空闲', count: data.vacant || 0 },
    { status: '已租', count: data.rented || 0 },
    { status: '即将到期', count: data.expiring || 0 }
  ]
})

const 成交金额表格数据 = computed(() => {
  return props.看板数据.金额趋势数据 || []
})

const 新增客户表格数据 = computed(() => {
  return props.看板数据.客户趋势数据 || []
})

const 小区排名表格数据 = computed(() => {
  return props.看板数据.小区排名数据 || []
})

const 最高成交日表格数据 = computed(() => {
  const data = props.看板数据.最高成交日 || {}
  if (!data.date) return []
  return [data]
})

const 最高客户月表格数据 = computed(() => {
  const data = props.看板数据.最高客户月 || {}
  if (!data.month) return []
  return [data]
})

function 关闭抽屉() {
  drawerVisible.value = false
}
</script>

<style scoped>
.drawer-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.table-section {
  background: #fff;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

.drawer-footer {
  margin-top: 24px;
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* 表格统一样式 */
.table-section :deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

.table-section :deep(.el-table th.el-table__cell) {
  background-color: #e6f0ff !important;
  color: #303133;
  font-weight: 600;
}

.table-section :deep(.el-table--border) {
  border-color: #ebeef5;
}

.table-section :deep(.el-table--border::after),
.table-section :deep(.el-table--group::after),
.table-section .el-table::before {
  background-color: #ebeef5;
}
</style>
