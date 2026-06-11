<template>
  <el-card class="settings-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="card-title">{{ 标题 }}</span>
      </div>
    </template>
    <slot></slot>
  </el-card>
</template>

<script setup>
defineProps({
  标题: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.settings-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.settings-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.settings-card :deep(.el-card__body) {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
</style>
