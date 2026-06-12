<template>
  <el-dialog
    v-model="dialogVisible"
    :title="是否编辑模式 ? '查看交易' : '添加交易'"
    width="750px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="表单数据"
      :rules="验证规则"
      label-width="100px"
      label-position="right"
    >
      <el-divider content-position="left">合同信息</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="合同编号">
            <el-input v-model="表单数据.contract_code" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="租住月数" prop="months">
            <el-input v-model="表单数据.months" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="起始日期" prop="start_date">
            <el-date-picker
              v-model="表单数据.start_date"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="结束日期" prop="end_date">
            <el-date-picker
              v-model="表单数据.end_date"
              type="date"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="押金金额">
            <el-input v-model="表单数据.deposit" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="合同金额">
            <el-input :model-value="'¥' + 合同金额" disabled />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">房源信息</el-divider>

      <el-form-item label="房源编号" prop="house_code">
        <el-input
          v-model="表单数据.house_code"
          @blur="查询房源信息"
          :disabled="是否编辑模式"
        />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="小区名称">
            <el-input :model-value="房源详情?.community || ''" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="详细地址">
            <el-input :model-value="房源详情?.address || ''" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="楼层">
            <el-input :model-value="房源详情?.floor || ''" disabled />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="室">
            <el-input :model-value="房源详情?.room || ''" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="厅">
            <el-input :model-value="房源详情?.hall || ''" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="面积">
            <el-input :model-value="房源详情?.area ? 房源详情.area + '㎡' : ''" disabled />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="租金">
            <el-input :model-value="房源详情?.rent ? '¥' + 房源详情.rent : ''" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="房源标签">
            <el-input :model-value="房源详情?.tags || ''" disabled />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">客户信息</el-divider>

      <el-form-item label="客户编号" prop="customer_code">
        <el-input
          v-model="表单数据.customer_code"
          @blur="查询客户信息"
          :disabled="是否编辑模式"
        />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="姓名">
            <el-input :model-value="客户详情?.name || ''" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="身份证号">
            <el-input :model-value="脱敏身份证(客户详情?.id_card)" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="联系电话">
            <el-input :model-value="客户详情?.phone || ''" disabled />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="重置表单">重置</el-button>
        <el-button @click="dialogVisible = false">返回</el-button>
        <el-button
          v-if="是否编辑模式"
          type="danger"
          @click="handleDelete"
        >
          删除
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 根据编号获取房源, 根据编号获取客户 } from '../api/contract.js'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  合同信息: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'add'
  }
})

const emit = defineEmits(['update:visible', 'submit', 'delete'])

const dialogVisible = ref(false)
const formRef = ref(null)
const 房源详情 = ref(null)
const 客户详情 = ref(null)

const 是否编辑模式 = computed(() => props.mode === 'edit' && !!props.合同信息)

const 表单数据 = reactive({
  contract_code: '',
  months: 1,
  start_date: '',
  end_date: '',
  deposit: 0,
  monthly_rent: 0,
  house_code: '',
  customer_code: ''
})

const 合同金额 = computed(() => {
  const 月数 = 表单数据.months || 0
  const 月租 = 表单数据.monthly_rent || (房源详情.value?.rent || 0)
  const 押金 = 表单数据.deposit || 0
  return (月数 * Number(月租) + Number(押金)).toFixed(2)
})

const 验证规则 = {
  months: [{ required: true, message: '请输入租住月数', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择起始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  house_code: [{ required: true, message: '请输入房源编号', trigger: 'blur' }],
  customer_code: [{ required: true, message: '请输入客户编号', trigger: 'blur' }]
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
  房源详情.value = null
  客户详情.value = null
  if (props.合同信息) {
    Object.assign(表单数据, {
      contract_code: props.合同信息.contract_code || '',
      months: props.合同信息.months || 1,
      start_date: props.合同信息.start_date || '',
      end_date: props.合同信息.end_date || '',
      deposit: props.合同信息.deposit || 0,
      monthly_rent: props.合同信息.monthly_rent || 0,
      house_code: props.合同信息.house_code || '',
      customer_code: props.合同信息.customer_code || ''
    })
    if (props.合同信息.house_code) {
      查询房源信息()
    }
    if (props.合同信息.customer_code) {
      查询客户信息()
    }
  } else {
    重置表单()
  }
}

function 重置表单() {
  表单数据.contract_code = ''
  表单数据.months = 1
  表单数据.start_date = ''
  表单数据.end_date = ''
  表单数据.deposit = 0
  表单数据.monthly_rent = 0
  表单数据.house_code = ''
  表单数据.customer_code = ''
  房源详情.value = null
  客户详情.value = null
}

async function 查询房源信息() {
  if (!表单数据.house_code) return
  try {
    const res = await 根据编号获取房源(表单数据.house_code)
    // 响应拦截器返回 {code, data, msg}，取 data 字段
    const 实际数据 = res.data !== undefined ? res.data : res
    房源详情.value = 实际数据
    // 自动填入月租金
    if (实际数据?.rent) {
      表单数据.monthly_rent = 实际数据.rent
    }
  } catch {
    ElMessage.warning('未找到该房源')
    房源详情.value = null
  }
}

async function 查询客户信息() {
  if (!表单数据.customer_code) return
  try {
    const res = await 根据编号获取客户(表单数据.customer_code)
    // 响应拦截器返回 {code, data, msg}，取 data 字段
    const 实际数据 = res.data !== undefined ? res.data : res
    客户详情.value = 实际数据
  } catch {
    ElMessage.warning('未找到该客户')
    客户详情.value = null
  }
}

function 脱敏身份证(id_card) {
  if (!id_card || id_card.length < 8) return id_card || '-'
  return id_card.substring(0, 6) + '********' + id_card.substring(id_card.length - 4)
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    const 提交数据 = { ...表单数据 }
    emit('submit', 提交数据)
    dialogVisible.value = false
  } catch {
    ElMessage.warning('请填写必填项')
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      '确定要删除该交易记录吗？此操作不可恢复！',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('delete')
  } catch {
    // 用户取消
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

.dialog-footer .el-button {
  border-radius: 2px;
}
</style>
