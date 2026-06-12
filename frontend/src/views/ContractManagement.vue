<template>
  <div class="contract-management">
    <div class="main-content">
      <div class="toolbar">
        <div class="toolbar-left">
          <h2 class="title">合同信息</h2>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加交易
          </el-button>
        </div>
      </div>

      <ContractTable
        :合同列表="合同列表"
        :loading="loading"
        @view="handleView"
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

    <ContractForm
      v-model:visible="表单对话框可见"
      :合同信息="当前查看合同"
      :mode="表单模式"
      @submit="handleSubmit"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import ContractTable from '../components/ContractTable.vue'
import ContractForm from '../components/ContractForm.vue'
import { 获取合同列表, 添加合同, 更新合同, 删除合同 } from '../api/contract.js'
import eventBus from '../utils/event-bus.js'

const loading = ref(false)
const 合同列表 = ref([])
const 表单对话框可见 = ref(false)
const 当前查看合同 = ref(null)
const 表单模式 = ref('add')
const route = useRoute()

// 分页相关状态
const 当前页码 = ref(1)
const 总记录数 = ref(0)
const 每页条数 = ref(20)

onMounted(() => {
  加载合同列表()
  检查路由参数()
})

async function 检查路由参数() {
  const action = route.query.action
  if (action === 'view' && route.query.contract_id) {
    await 加载合同列表()
    const contract = 合同列表.value.find(c => c.contract_code === route.query.contract_id)
    if (contract) {
      handleView(contract)
    } else {
      ElMessage.warning('未找到该合同信息')
    }
  } else if (action === 'add' && route.query.house_code) {
    await 加载合同列表()
    当前查看合同.value = {
      house_code: route.query.house_code,
      monthly_rent: route.query.rent ? Number(route.query.rent) : null
    }
    表单模式.value = 'add'
    表单对话框可见.value = true
  }
}

async function 加载合同列表(页码 = 1) {
  loading.value = true
  try {
    const res = await 获取合同列表({ page: 页码, per_page: 每页条数.value })
    // 兼容拦截器返回格式：{code, data:{items,total}, msg}
    const data = res.data || res
    if (data && data.items) {
      合同列表.value = data.items
      总记录数.value = data.total || 0
      当前页码.value = data.current_page || 页码
    } else {
      合同列表.value = Array.isArray(data) ? data : []
      总记录数.value = Array.isArray(data) ? data.length : 0
      当前页码.value = 1
    }
  } catch (error) {
    console.error('加载合同失败:', error)
    合同列表.value = []
    总记录数.value = 0
  } finally {
    loading.value = false
  }
}

function 处理页码变化(新页码) {
  加载合同列表(新页码)
}

function handleAdd() {
  当前查看合同.value = null
  表单模式.value = 'add'
  表单对话框可见.value = true
}

function handleView(contract) {
  当前查看合同.value = contract
  表单模式.value = 'edit'
  表单对话框可见.value = true
}

async function handleSubmit(data) {
  try {
    if (表单模式.value === 'edit' && 当前查看合同.value) {
      await 更新合同(当前查看合同.value.id, data)
      ElMessage.success('更新成功')
      eventBus.emit('data-changed', { type: 'contract-updated' })
    } else {
      await 添加合同(data)
      ElMessage.success('添加成功')
      eventBus.emit('data-changed', { type: 'contract-created' })
    }
    await 加载合同列表()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

async function handleDelete() {
  if (!当前查看合同.value) return
  try {
    await 删除合同(当前查看合同.value.id)
    ElMessage.success('删除成功')
    表单对话框可见.value = false
    await 加载合同列表()
    eventBus.emit('data-changed', { type: 'contract-deleted' })
  } catch (error) {
    console.error('删除失败:', error)
  }
}
</script>

<style scoped>
.contract-management {
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
