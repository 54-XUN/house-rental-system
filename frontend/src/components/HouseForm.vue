<template>
  <el-dialog
    v-model="dialogVisible"
    :title="是否编辑 ? '编辑房源' : '添加房源'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="表单数据"
      :rules="验证规则"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="房源编号" prop="house_code">
        <el-input
          v-model="表单数据.house_code"
          placeholder="自动生成或手动输入"
          :disabled="是否编辑"
        />
      </el-form-item>
      
      <el-form-item label="小区名称" prop="community">
        <el-input v-model="表单数据.community" style="width: 100%" />
      </el-form-item>
      
      <el-form-item label="详细地址" prop="address">
        <el-input v-model="表单数据.address" />
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="楼层" prop="floor">
            <el-input v-model="表单数据.floor" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="室" prop="room">
            <el-input v-model="表单数据.room" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="厅" prop="hall">
            <el-input v-model="表单数据.hall" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="面积(㎡)" prop="area">
            <el-input v-model="表单数据.area" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="月租金(元)" prop="rent">
            <el-input v-model="表单数据.rent" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="标签">
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
      
      <el-form-item label="添加日期" prop="add_date">
        <el-date-picker
          v-model="表单数据.add_date"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  房源信息: {
    type: Object,
    default: null
  },
  小区列表: {
    type: Array,
    default: () => []
  },
  可用标签列表: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'submit'])

const dialogVisible = ref(false)
const formRef = ref(null)

const 是否编辑 = computed(() => !!props.房源信息)

const 表单数据 = reactive({
  house_code: '',
  community: '',
  address: '',
  floor: undefined,
  room: undefined,
  hall: undefined,
  area: undefined,
  rent: undefined,
  选中标签: [],
  add_date: new Date().toISOString().split('T')[0]
})

const 验证规则 = {
  community: [
    { required: true, message: '请选择小区', trigger: 'change' }
  ],
  address: [
    { required: true, message: '请输入详细地址', trigger: 'blur' }
  ],
  area: [
    { required: true, message: '请输入面积', trigger: 'blur' }
  ],
  rent: [
    { required: true, message: '请输入月租金', trigger: 'blur' }
  ]
}

watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    初始化表单()
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

function 初始化表单() {
  if (props.房源信息) {
    Object.assign(表单数据, {
      house_code: props.房源信息.house_code || '',
      community: props.房源信息.community || '',
      address: props.房源信息.address || '',
      floor: props.房源信息.floor,
      room: props.房源信息.room,
      hall: props.房源信息.hall,
      area: props.房源信息.area,
      rent: props.房源信息.rent,
      选中标签: props.房源信息.tags ? props.房源信息.tags.split(',') : [],
      add_date: props.房源信息.add_date || new Date().toISOString().split('T')[0]
    })
  } else {
    重置表单()
  }
}

function 重置表单() {
  表单数据.house_code = ''
  表单数据.community = ''
  表单数据.address = ''
  表单数据.floor = undefined
  表单数据.room = undefined
  表单数据.hall = undefined
  表单数据.area = undefined
  表单数据.rent = undefined
  表单数据.选中标签 = []
  表单数据.add_date = new Date().toISOString().split('T')[0]
}

async function handleSubmit() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    const 提交数据 = {
      ...表单数据,
      tags: 表单数据.选中标签.join(',')
    }
    delete 提交数据.选中标签
    
    emit('submit', 提交数据)
    dialogVisible.value = false
  } catch (error) {
    ElMessage.warning('请填写必填项')
  }
}

function handleClose() {
  重置表单()
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
