<template>
  <el-dialog
    v-model="dialogVisible"
    title="高级筛选"
    width="500px"
    @close="handleClose"
  >
    <el-form :model="表单数据" label-width="80px">
      <el-form-item label="房源状态">
        <el-radio-group v-model="表单数据.status">
          <el-radio value="">全部</el-radio>
          <el-radio value="空闲">空闲</el-radio>
          <el-radio value="即将到期">即将到期</el-radio>
          <el-radio value="已租">已租</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="面积范围">
        <div class="range-input">
          <el-input
            v-model="表单数据.area_min"
            type="text"
            placeholder="最小面积"
          />
          <span class="separator">-</span>
          <el-input
            v-model="表单数据.area_max"
            type="text"
            placeholder="最大面积"
          />
        </div>
      </el-form-item>
      
      <el-form-item label="房源标签">
        <el-checkbox-group v-model="表单数据.选中标签">
          <el-checkbox
            v-for="tag in 可用标签列表"
            :key="tag"
            :label="tag"
            :value="tag"
          >
            {{ tag }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      
      <el-form-item label="室数">
        <el-input
          v-model="表单数据.room"
          type="text"
          placeholder="精确匹配室数"
        />
      </el-form-item>

      <el-form-item label="厅数">
        <el-input
          v-model="表单数据.hall"
          type="text"
          placeholder="精确匹配厅数"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" @click="handleSubmit">确认筛选</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const 存储键 = 'house_filter_params'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  可用标签列表: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'filter'])

const dialogVisible = ref(false)

const 表单数据 = reactive({
  status: '',
  area_min: undefined,
  area_max: undefined,
  选中标签: [],
  room: undefined,
  hall: undefined
})

watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    读取筛选条件()
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

function handleSubmit() {
  const 最小面积 = Number(表单数据.area_min)
  const 最大面积 = Number(表单数据.area_max)
  if (!isNaN(最小面积) && !isNaN(最大面积) && 最小面积 > 最大面积) {
    ElMessage.warning('最小面积不能大于最大面积')
    return
  }

  const params = {}
  
  if (表单数据.status) {
    params.status = 表单数据.status
  }
  
  if (表单数据.area_min !== undefined && 表单数据.area_min !== null) {
    params.area_min = 表单数据.area_min
  }
  
  if (表单数据.area_max !== undefined && 表单数据.area_max !== null) {
    params.area_max = 表单数据.area_max
  }
  
  if (表单数据.选中标签.length > 0) {
    params.tags = 表单数据.选中标签.join(',')
  }
  
  if (表单数据.room !== undefined && 表单数据.room !== null) {
    params.room = 表单数据.room
  }
  
  if (表单数据.hall !== undefined && 表单数据.hall !== null) {
    params.hall = 表单数据.hall
  }
  
  emit('filter', params)
  保存筛选条件()
  dialogVisible.value = false
}

function handleReset() {
  表单数据.status = ''
  表单数据.area_min = undefined
  表单数据.area_max = undefined
  表单数据.选中标签 = []
  表单数据.room = undefined
  表单数据.hall = undefined
  localStorage.removeItem(存储键)
}

function 保存筛选条件() {
  const 数据 = {
    status: 表单数据.status,
    area_min: 表单数据.area_min,
    area_max: 表单数据.area_max,
    选中标签: 表单数据.选中标签,
    room: 表单数据.room,
    hall: 表单数据.hall
  }
  localStorage.setItem(存储键, JSON.stringify(数据))
}

function 读取筛选条件() {
  try {
    const 原始数据 = localStorage.getItem(存储键)
    if (原始数据) {
      const 数据 = JSON.parse(原始数据)
      表单数据.status = 数据.status || ''
      表单数据.area_min = 数据.area_min || undefined
      表单数据.area_max = 数据.area_max || undefined
      表单数据.选中标签 = 数据.选中标签 || []
      表单数据.room = 数据.room || undefined
      表单数据.hall = 数据.hall || undefined
    }
  } catch (e) {
    // 解析失败忽略，使用默认值
  }
}

function handleClose() {
  dialogVisible.value = false
}
</script>

<style scoped>
.range-input {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.separator {
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
