<template>
  <div class="table-container">
    <el-table
      :data="合同列表"
      :header-cell-style="{ background: '#e6f0ff', color: '#303133', fontWeight: '600' }"
      border
      stripe
      row-class-name="hover-row"
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="sign_date" label="签订日期" width="110" align="center" />
      <el-table-column prop="contract_code" label="合同编号" width="130" fixed />
      <el-table-column prop="months" label="租住月数" width="90" align="center" />
      <el-table-column prop="start_date" label="起始日期" width="110" align="center" />
      <el-table-column prop="end_date" label="结束日期" width="110" align="center" />
      <el-table-column prop="deposit" label="押金金额" width="100" align="right">
        <template #default="{ row }">
          {{ row.deposit != null ? '¥' + Number(row.deposit).toFixed(2) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="total_amount" label="合同金额" width="120" align="right">
        <template #default="{ row }">
          <span class="amount-text">¥{{ row.total_amount }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="house_code" label="房源编号" width="120" />
      <el-table-column prop="monthly_rent" label="每月租金" width="110" align="right">
        <template #default="{ row }">
          <span class="rent-text">¥{{ row.monthly_rent }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="customer_code" label="客户编号" width="120" />
      <el-table-column label="操作" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="$emit('view', row)">
            查看
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
defineProps({
  合同列表: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view'])
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

.rent-text {
  color: #e6a23c;
  font-weight: bold;
}

.amount-text {
  color: #f56c6c;
  font-weight: bold;
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
