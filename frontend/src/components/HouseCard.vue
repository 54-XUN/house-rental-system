<template>
  <div
    :class="['house-card', `status-${house.status}`]"
    @click="handleClick"
  >
    <!-- 顶部颜色条：显示地址 -->
    <div class="card-header">
      <span class="header-address">{{ house.address }}</span>
    </div>
    
    <!-- 白色内容区 -->
    <div class="card-body">
      <div class="info-row">
        <span class="info-label">户型：</span>
        <span class="info-value">{{ house.room }}室{{ house.hall }}厅</span>
      </div>
      <div class="info-row">
        <span class="info-label">面积：</span>
        <span class="info-value">{{ house.area }}m²</span>
      </div>
      <div class="info-row">
        <span class="info-label">租金：</span>
        <span class="info-value rent">{{ house.rent }}元</span>
      </div>
      <div class="detail-row">
        <a class="detail-link" @click.stop="handleViewDetail">详情</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  house: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'edit', 'delete'])

const router = useRouter()

function handleClick() {
  emit('click', props.house)
}

function handleViewDetail() {
  router.push({
    path: '/house-detail',
    query: { house_id: props.house.id }
  })
}

function handleEdit() {
  emit('edit', props.house)
}

function handleDelete() {
  emit('delete', props.house)
}
</script>

<style scoped>
.house-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 4px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.house-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

/* 状态颜色 */
.status-空闲 .card-header {
  background-color: #7fcdbb;
}

.status-已租 .card-header {
  background-color: #c0c4cc;
}

.status-即将到期 .card-header {
  background-color: #f5c97a;
}

/* 顶部颜色条 */
.card-header {
  padding: 10px 12px;
  text-align: center;
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-address {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 白色内容区 */
.card-body {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-row {
  display: flex;
  align-items: center;
  font-size: 13px;
  height: 20px;
}

.info-label {
  color: #606266;
  width: 40px;
  flex-shrink: 0;
}

.info-value {
  color: #303133;
  flex: 1;
}

.rent {
  color: #f56c6c;
  font-weight: 500;
}

.detail-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 2px;
  height: 20px;
}

.detail-link {
  font-size: 13px;
  color: #303133;
  cursor: pointer;
  text-decoration: none;
}

.detail-link:hover {
  color: #409eff;
}
</style>
