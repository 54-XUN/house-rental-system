<template>
  <el-card class="stat-card" shadow="hover">
    <div class="stat-card-body">
      <div class="stat-icon" :style="{ backgroundColor: 图标背景色 }">
        <el-icon :size="28" :color="图标颜色">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="stat-info">
        <div class="stat-value">{{ formattedValue }}</div>
        <div class="stat-label">{{ 标题 }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  标题: {
    type: String,
    required: true
  },
  数值: {
    type: [Number, String],
    default: 0
  },
  icon: {
    type: [String, Object],
    default: 'DataLine'
  },
  图标颜色: {
    type: String,
    default: '#377EB8'
  },
  图标背景色: {
    type: String,
    default: '#E8F4FD'
  },
  是否金额: {
    type: Boolean,
    default: false
  }
})

const formattedValue = computed(() => {
  if (props.是否金额) {
    return '¥' + Number(props.数值).toLocaleString('zh-CN', { minimumFractionDigits: 0 })
  }
  return Number(props.数值).toLocaleString('zh-CN')
})
</script>

<style scoped>
.stat-card {
  border-radius: 8px;
  border: none;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-card-body {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s;
}

.stat-card:hover .stat-icon {
  transform: scale(1.05);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>
