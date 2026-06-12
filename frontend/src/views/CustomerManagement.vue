<template>
  <div class="customer-management">
    <div class="main-content">
      <div class="toolbar">
        <div class="toolbar-left">
          <h2 class="title">客户明细</h2>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" @click="handleAdd">
            添加
          </el-button>
          <el-button :type="当前筛选状态 === '已签单' ? 'primary' : 'default'" @click="切换筛选('已签单')">
            已签单
          </el-button>
          <el-button :type="当前筛选状态 === '跟进中' ? 'primary' : 'default'" @click="切换筛选('跟进中')">
            跟进中
          </el-button>
          <el-button :type="当前筛选状态 === '已放弃' ? 'primary' : 'default'" @click="切换筛选('已放弃')">
            已放弃
          </el-button>
          <el-button :type="当前筛选状态 === '' ? 'primary' : 'default'" @click="切换筛选('')">
            全部
          </el-button>
        </div>
      </div>

      <CustomerTable
        :客户列表="客户列表"
        :loading="loading"
        @edit="handleEdit"
        @delete="handleDelete"
      />

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

    <CustomerForm
      v-model:visible="表单对话框可见"
      :客户信息="当前编辑客户"
      :可用标签列表="可用标签列表"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

import CustomerTable from '../components/CustomerTable.vue'
import CustomerForm from '../components/CustomerForm.vue'
import { 获取客户列表, 添加客户, 更新客户, 删除客户 } from '../api/customer.js'
import { 获取设置 } from '../api/house.js'
import eventBus from '../utils/event-bus.js'

const loading = ref(false)
const 客户列表 = ref([])
const 可用标签列表 = ref([])
const 当前筛选状态 = ref('')
const 表单对话框可见 = ref(false)
const 当前编辑客户 = ref(null)

// 分页相关状态
const 当前页码 = ref(1)
const 总记录数 = ref(0)
const 每页条数 = ref(20)

onMounted(() => {
  加载设置()
  加载客户列表()
  // 监听合同变更事件，自动刷新客户列表以同步状态
  eventBus.on('data-changed', 处理数据变更)
})

onUnmounted(() => {
  eventBus.off('data-changed', 处理数据变更)
})

function 处理数据变更(事件数据) {
  if (['contract-created', 'contract-deleted', 'contract-updated'].includes(事件数据?.type)) {
    加载客户列表(当前页码.value)
  }
}

async function 加载设置() {
  try {
    const res = await 获取设置()
    const data = res.data || res  // 兼容拦截器返回格式
    if (data.house_tags) {
      可用标签列表.value = typeof data.house_tags === 'string'
        ? JSON.parse(data.house_tags)
        : data.house_tags
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

async function 加载客户列表(页码 = 1) {
  loading.value = true
  try {
    const params = 当前筛选状态.value
      ? { status: 当前筛选状态.value, page: 页码, per_page: 每页条数.value }
      : { page: 页码, per_page: 每页条数.value }
    const res = await 获取客户列表(params)
    const data = res.data || res  // 兼容拦截器返回格式
    if (data && data.items) {
      客户列表.value = data.items
      总记录数.value = data.total || 0
      当前页码.value = data.current_page || 页码
    } else {
      客户列表.value = Array.isArray(data) ? data : []
      总记录数.value = Array.isArray(data) ? data.length : 0
      当前页码.value = 1
    }
  } catch (error) {
    console.error('加载客户失败:', error)
    客户列表.value = []
    总记录数.value = 0
  } finally {
    loading.value = false
  }
}

function 处理页码变化(新页码) {
  加载客户列表(新页码)
}

function 切换筛选(状态) {
  当前筛选状态.value = 状态
  当前页码.value = 1
  加载客户列表(1)
}

function handleAdd() {
  当前编辑客户.value = null
  表单对话框可见.value = true
}

function handleEdit(customer) {
  当前编辑客户.value = customer
  表单对话框可见.value = true
}

async function handleSubmit(data) {
  try {
    if (当前编辑客户.value) {
      await 更新客户(当前编辑客户.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await 添加客户(data)
      ElMessage.success('添加成功')
    }
    await 加载客户列表()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

async function handleDelete(customer) {
  try {
    await 删除客户(customer.id)
    ElMessage.success('删除成功')
    await 加载客户列表()
  } catch (error) {
    console.error('删除失败:', error)
  }
}
</script>

<style scoped>
.customer-management {
  background-color: #f5f7fa;
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

/* 分页组件样式 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 0 0 8px 8px;
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
</style>
