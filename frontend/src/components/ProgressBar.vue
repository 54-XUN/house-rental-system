<template>
  <el-dialog
    v-model="dialogVisible"
    title="加载房源"
    width="400px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
  >
    <div class="progress-container">
      <el-progress
        :percentage="percentage"
        :stroke-width="20"
        :text-inside="true"
        :status="isComplete ? 'success' : ''"
      />
      <div class="progress-text">
        当前进度：{{ current }} --- {{ total }}
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  total: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:visible', 'complete'])

const dialogVisible = ref(false)
const current = ref(0)
const percentage = ref(0)
const isComplete = ref(false)
let 定时器ID = null

onUnmounted(() => {
  清理定时器()
})

watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    开始进度动画()
  } else {
    重置进度()
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

function 开始进度动画() {
  清理定时器()
  
  current.value = 0
  percentage.value = 0
  isComplete.value = false

  const 总数 = props.total || 1
  const 步长 = Math.max(1, Math.floor(总数 / 20))
  let 当前值 = 0

  定时器ID = setInterval(() => {
    当前值 += 步长
    if (当前值 >= 总数) {
      当前值 = 总数
      清理定时器()

      current.value = 当前值
      percentage.value = 100
      isComplete.value = true

      setTimeout(() => {
        ElMessage.success('加载完成')
        emit('complete')
        dialogVisible.value = false
      }, 800)
    } else {
      current.value = 当前值
      percentage.value = Math.floor((当前值 / 总数) * 100)
    }
  }, 25)
}

function 清理定时器() {
  if (定时器ID) {
    clearInterval(定时器ID)
    定时器ID = null
  }
}

function 重置进度() {
  清理定时器()
  current.value = 0
  percentage.value = 0
  isComplete.value = false
}
</script>

<style scoped>
.progress-container {
  padding: 20px 0;
}

.progress-text {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
  color: #606266;
}
</style>
