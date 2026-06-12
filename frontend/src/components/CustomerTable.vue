<template>
  <div class="table-container">
    <el-table
      :data="客户列表"
      :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }"
      border
      stripe
      row-class-name="hover-row"
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="add_date" label="添加日期" width="120" align="center" />
      <el-table-column prop="customer_code" label="客户编号" width="120" fixed />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column label="身份证号" width="180">
        <template #default="{ row }">
          {{ 脱敏身份证(row.id_card) }}
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="联系电话" width="130" />
      <el-table-column prop="wechat" label="微信" width="130" />
      <el-table-column label="标签" min-width="200" show-overflow-tooltip>
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
      <el-table-column prop="status" label="状态" width="100" align="center" fixed="right">
        <template #default="{ row }">
          <el-tag :type="获取状态类型(row.status)" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="$emit('edit', row)">
            编辑
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ElMessageBox } from 'element-plus'

defineProps({
  客户列表: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete'])

function 脱敏身份证(id_card) {
  if (!id_card || id_card.length < 8) return id_card || '-'
  return id_card.substring(0, 6) + '********' + id_card.substring(id_card.length - 4)
}

function 获取标签列表(tags) {
  if (!tags) return []
  return tags.split(',').filter(tag => tag.trim())
}

function 获取状态类型(status) {
  const 状态映射 = {
    '跟进中': 'primary',
    '已签单': 'success',
    '已放弃': 'info'
  }
  return 状态映射[status] || 'info'
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除客户 ${row.name}（${row.customer_code}）吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('delete', row)
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.table-container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
}

:deep(.el-table) {
  border-color: #ebeef5;
}

:deep(.el-table th.el-table__cell) {
  border-color: #ebeef5;
}

:deep(.el-table td.el-table__cell) {
  border-color: #ebeef5;
}

:deep(.hover-row:hover > td.el-table__cell) {
  background-color: #ecf5ff !important;
}

.tag-item {
  margin-right: 6px;
  margin-bottom: 4px;
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
