<template>
  <div class="house-detail">
    <div class="main-content">
      <!-- 顶部操作栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <h2 class="title">房源明细</h2>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" @click="handleStatusRefresh" :loading="刷新中" class="refresh-btn">
            状态刷新
          </el-button>
        </div>
      </div>

      <!-- 房源表格 -->
      <div class="table-container">
        <el-table
          :data="房源列表"
          :row-class-name="表格行类名"
          stripe
          border
          style="width: 100%"
          :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: 'bold' }"
          v-loading="loading"
        >
          <el-table-column prop="add_date" label="添加日期" width="90" />
          <el-table-column prop="house_code" label="房源编号" width="85" />
          <el-table-column prop="community" label="小区名称" width="95" show-overflow-tooltip />
          <el-table-column prop="address" label="详细地址" width="145" show-overflow-tooltip />
          <el-table-column prop="floor" label="楼层" width="50" align="center" />
          <el-table-column prop="room" label="室" width="40" align="center" />
          <el-table-column prop="hall" label="厅" width="40" align="center" />
          <el-table-column prop="area" label="面积" width="65" align="right">
            <template #default="{ row }">
              {{ row.area }}㎡
            </template>
          </el-table-column>
          <el-table-column prop="rent" label="租金" width="75" align="right">
            <template #default="{ row }">
              ¥{{ row.rent }}
            </template>
          </el-table-column>
          <el-table-column prop="tags" label="房源标签" min-width="120" show-overflow-tooltip>
            <template #default="{ row }">
              <el-tag
                v-for="tag in 获取标签列表(row.tags)"
                :key="tag"
                size="small"
                type="info"
                effect="plain"
                class="tag-item-compact"
              >
                {{ tag }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="contract_code" label="合同编号" width="100" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.contract_code || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="expire_date" label="到期日" width="90" align="center">
            <template #default="{ row }">
              {{ row.expire_date || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="查看详情(row)">
                查看
              </el-button>
              <el-button type="success" link size="small" @click="开单(row)">
                开单
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center" fixed="right">
            <template #default="{ row }">
              <el-tag
                :type="获取状态类型(row.status)"
                size="small"
                effect="dark"
              >
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页组件 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="当前页码"
            :page-size="每页条数"
            :total="总记录数"
            layout="total, prev, pager, next, jumper"
            background
            @current-change="处理页码变化"
          />
        </div>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="详情对话框可见"
      title="房源详情"
      width="600px"
      :append-to-body="true"
      :modal-append-to-body="true"
      :close-on-click-modal="true"
      :show-transition="false"
      :hide-transition="false"
      :show-close="true"
      :custom-class="'no-animation-dialog'"
      :enter-active-class="''"
      :leave-active-class="''"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="房源编号">{{ 查看中的房源?.house_code }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="获取状态类型(查看中的房源?.status)" size="small">
            {{ 查看中的房源?.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="小区名称">{{ 查看中的房源?.community }}</el-descriptions-item>
        <el-descriptions-item label="详细地址">{{ 查看中的房源?.address }}</el-descriptions-item>
        <el-descriptions-item label="楼层">{{ 查看中的房源?.floor }}层</el-descriptions-item>
        <el-descriptions-item label="户型">
          {{ 查看中的房源?.room }}室{{ 查看中的房源?.hall }}厅
        </el-descriptions-item>
        <el-descriptions-item label="面积">{{ 查看中的房源?.area }}㎡</el-descriptions-item>
        <el-descriptions-item label="月租金">
          ¥{{ 查看中的房源?.rent }}
        </el-descriptions-item>
        <el-descriptions-item label="标签" :span="2">
          <el-tag
            v-for="tag in 获取标签列表(查看中的房源?.tags)"
            :key="tag"
            size="small"
            type="info"
            effect="plain"
            class="tag-item"
          >
            {{ tag }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="添加日期">{{ 查看中的房源?.add_date }}</el-descriptions-item>
        <el-descriptions-item label="到期日期">{{ 查看中的房源?.expire_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="合同编号" :span="2">
          {{ 查看中的房源?.contract_code || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'

import { 获取房源列表, 刷新房源状态 } from '../api/house.js'
import eventBus from '../utils/event-bus.js'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const 房源列表 = ref([])
const 高亮房源ID = ref(null)
const 刷新中 = ref(false)

// 分页相关状态
const 当前页码 = ref(1)
const 总记录数 = ref(0)
const 每页条数 = ref(20)

const 详情对话框可见 = ref(false)
const 查看中的房源 = ref(null)

onMounted(() => {
  获取URL参数()
  加载房源列表()
  eventBus.on('data-changed', handleDataChanged)
})

onUnmounted(() => {
  eventBus.off('data-changed', handleDataChanged)
})

function handleDataChanged(data) {
  if (data && ['contract-deleted', 'contract-created', 'contract-updated'].includes(data.type)) {
    加载房源列表()
  }
}

function 获取URL参数() {
  const houseId = route.query.house_id
  if (houseId) {
    高亮房源ID.value = parseInt(houseId)
  }
}

async function 加载房源列表(页码 = 1) {
  loading.value = true
  try {
    const res = await 获取房源列表({ page: 页码, per_page: 每页条数.value })
    if (res && res.items) {
      房源列表.value = res.items
      总记录数.value = res.total || 0
      当前页码.value = res.current_page || 页码
    } else {
      房源列表.value = Array.isArray(res) ? res : []
      总记录数.value = Array.isArray(res) ? res.length : 0
      当前页码.value = 1
    }
  } catch (error) {
    console.error('加载房源失败:', error)
    ElMessage.error('加载房源失败，请检查网络连接后重试')
    房源列表.value = []
    总记录数.value = 0
  } finally {
    loading.value = false
  }
}

function 处理页码变化(新页码) {
  加载房源列表(新页码)
}

async function handleStatusRefresh() {
  刷新中.value = true
  try {
    const res = await 刷新房源状态()

    if (res.updated_count > 0) {
      ElMessage({
        message: `🎉 成功刷新 ${res.updated_count} 条房源状态`,
        type: 'success',
        duration: 3000,
        customClass: 'status-refresh-message'
      })
    } else {
      ElMessage({
        message: '<span style="color: #909399;">✅ 所有房源状态已是最新</span>',
        type: 'info',
        duration: 2500,
        dangerouslyUseHTMLString: true
      })
    }

    await 加载房源列表()
  } catch (error) {
    console.error('刷新状态失败:', error)
    ElMessage({
      message: '<span style="color: #f56c6c;">❌ 状态刷新失败，请检查网络连接后重试</span>',
      type: 'error',
      duration: 3000,
      dangerouslyUseHTMLString: true
    })
  } finally {
    刷新中.value = false
  }
}

function 表格行类名({ row }) {
  if (高亮房源ID.value && row.id === 高亮房源ID.value) {
    return 'highlight-row'
  }
  return ''
}

function 查看详情(house) {
  查看中的房源.value = house
  详情对话框可见.value = true
}

function 开单(house) {
  if (house.contract_code) {
    router.push({
      path: '/contracts',
      query: {
        action: 'view',
        contract_id: house.contract_code
      }
    })
  } else {
    router.push({
      path: '/contracts',
      query: {
        action: 'add',
        house_code: house.house_code,
        rent: house.rent
      }
    })
  }
}

function 获取标签列表(tags) {
  if (!tags) return []
  return tags.split(',').filter(tag => tag.trim())
}

function 获取状态类型(status) {
  const 状态映射 = {
    '空闲': 'success',
    '已租': 'info',
    '即将到期': 'warning'
  }
  return 状态映射[status] || 'info'
}
</script>

<style scoped>
.house-detail {
  width: 100%;
  height: 100%;
}

:deep(.el-dialog) {
  animation: none !important;
}

:deep(.el-overlay) {
  animation: none !important;
}

:deep(.el-dialog__wrapper) {
  animation: none !important;
  transition: none !important;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.refresh-btn {
  background-color: #409eff;
  border-color: #409eff;
}

.table-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.tag-item {
  margin-right: 6px;
  margin-bottom: 4px;
}

:deep(.el-table) {
  border-color: #ebeef5;
}

:deep(.el-table th.el-table__cell) {
  background-color: #e6f0ff !important;
  color: #303133;
  font-weight: bold;
  border-color: #ebeef5;
}

:deep(.el-table td.el-table__cell) {
  border-color: #ebeef5;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background-color: #fafafa;
}

:deep(.el-table__body tr:hover > td.el-table__cell) {
  background-color: #ecf5ff !important;
}

:deep(.highlight-row) {
  background-color: #fffbe6 !important;
}

/* 状态刷新消息样式 */
:deep(.status-refresh-message) {
  min-width: 320px;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 紧凑型表格样式 - 使用缩放方案 */
.table-container {
  transform: scale(0.85);
  transform-origin: top left;
  width: 117.6%; /* 100 / 0.85 ≈ 117.6% */
}

:deep(.el-table) {
  font-size: 14px;
}

.tag-item-compact {
  margin-right: 4px;
  margin-bottom: 3px;
}

/* 分页组件样式 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-pagination) {
  font-size: 14px;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  background: #fff;
}

:deep(.el-pager li) {
  background: #fff;
}

:deep(.el-pager li.is-active) {
  background-color: #409eff;
}

/* 禁止表头列宽拖拽 */
:deep(.el-table__header th .col-resize-proxy) {
  display: none;
}

:deep(.el-table__header th) {
  cursor: default;
}

:deep(.el-table__header-wrapper th) {
  cursor: default;
}
</style>
