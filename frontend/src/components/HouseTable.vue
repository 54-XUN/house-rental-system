<template>
  <div class="table-container">
    <el-table
      :data="房源列表"
      border
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="house_code" label="房源编号" width="120" fixed />
      
      <el-table-column prop="community" label="小区名称" width="150" />
      
      <el-table-column prop="address" label="详细地址" min-width="200" show-overflow-tooltip />
      
      <el-table-column prop="floor" label="楼层" width="70" align="center" />
      
      <el-table-column label="户型" width="100" align="center">
        <template #default="{ row }">
          {{ row.room }}室{{ row.hall }}厅
        </template>
      </el-table-column>
      
      <el-table-column prop="area" label="面积(㎡)" width="100" align="right">
        <template #default="{ row }">
          {{ row.area }}
        </template>
      </el-table-column>
      
      <el-table-column prop="rent" label="月租金(元)" width="120" align="right">
        <template #default="{ row }">
          <span class="rent-text">¥{{ row.rent }}</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="tags" label="标签" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <el-tag
            v-for="tag in 获取标签列表(row.tags)"
            :key="tag"
            size="small"
            type="info"
            effect="plain"
            class="tag-item"
          >
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="获取状态类型(row.status)" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="add_date" label="添加日期" width="120" align="center" />
      
      <el-table-column prop="expire_date" label="到期日期" width="120" align="center">
        <template #default="{ row }">
          {{ row.expire_date || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="contract_code" label="合同编号" width="140" align="center">
        <template #default="{ row }">
          {{ row.contract_code || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleView(row)">
            查看
          </el-button>
          <el-button type="success" link size="small" @click="handleOrder(row)">
            开单
          </el-button>
          <el-button type="primary" link size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog
      v-model="详情对话框可见"
      title="房源详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="房源编号">{{ 当前房源?.house_code }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="获取状态类型(当前房源?.status)" size="small">
            {{ 当前房源?.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="小区名称">{{ 当前房源?.community }}</el-descriptions-item>
        <el-descriptions-item label="详细地址">{{ 当前房源?.address }}</el-descriptions-item>
        <el-descriptions-item label="楼层">{{ 当前房源?.floor }}层</el-descriptions-item>
        <el-descriptions-item label="户型">
          {{ 当前房源?.room }}室{{ 当前房源?.hall }}厅
        </el-descriptions-item>
        <el-descriptions-item label="面积">{{ 当前房源?.area }}㎡</el-descriptions-item>
        <el-descriptions-item label="月租金">
          ¥{{ 当前房源?.rent }}
        </el-descriptions-item>
        <el-descriptions-item label="标签" :span="2">
          <el-tag
            v-for="tag in 获取标签列表(当前房源?.tags)"
            :key="tag"
            size="small"
            type="info"
            effect="plain"
            class="tag-item"
          >
            {{ tag }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="添加日期">{{ 当前房源?.add_date }}</el-descriptions-item>
        <el-descriptions-item label="到期日期">{{ 当前房源?.expire_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="合同编号" :span="2">
          {{ 当前房源?.contract_code || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  房源列表: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete', 'order'])

const 详情对话框可见 = ref(false)
const 当前房源 = ref(null)

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

function handleView(row) {
  当前房源.value = row
  详情对话框可见.value = true
}

function handleEdit(row) {
  emit('edit', row)
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除房源 ${row.house_code} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('delete', row)
  } catch {
    // 用户取消删除
  }
}

function handleOrder(row) {
  emit('order', row)
}
</script>

<style scoped>
.table-container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}

.rent-text {
  color: #f56c6c;
  font-weight: bold;
}

.tag-item {
  margin-right: 6px;
  margin-bottom: 4px;
}
</style>
