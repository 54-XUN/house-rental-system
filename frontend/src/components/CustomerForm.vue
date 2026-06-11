<template>
  <el-dialog
    v-model="dialogVisible"
    :title="是否编辑 ? '编辑客户' : '添加客户'"
    width="550px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="表单数据"
      :rules="验证规则"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="客户编号">
        <el-input v-model="表单数据.customer_code" placeholder="自动生成" disabled />
      </el-form-item>

      <el-form-item label="姓名" prop="name">
        <el-input v-model="表单数据.name" placeholder="请输入姓名" />
      </el-form-item>

      <el-form-item label="身份证号" prop="id_card">
        <el-input v-model="表单数据.id_card" placeholder="请输入身份证号" />
      </el-form-item>

      <el-form-item label="联系电话" prop="phone">
        <el-input v-model="表单数据.phone" placeholder="请输入电话" />
      </el-form-item>

      <el-form-item label="微信">
        <el-input v-model="表单数据.wechat" placeholder="请输入微信号" />
      </el-form-item>

      <el-form-item label="标签">
        <div style="display: flex; gap: 8px; flex: 1;">
          <el-input v-model="表单数据.tags" placeholder="点击右侧按钮选择标签" readonly style="flex: 1;" />
          <el-button type="primary" @click="打开标签选择弹窗">选</el-button>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="handleSubmit">确认</el-button>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 标签选择二级弹窗 -->
  <el-dialog
    v-model="标签选择弹窗可见"
    title="选择标签"
    width="400px"
    append-to-body
    @close="关闭标签选择弹窗"
  >
    <el-checkbox-group v-model="临时选中标签" style="display: flex; flex-direction: column; gap: 12px;">
      <el-checkbox
        v-for="tag in 可用标签列表"
        :key="tag"
        :label="tag"
        :value="tag"
        style="margin-right: 0;"
      >
        {{ tag }}
      </el-checkbox>
    </el-checkbox-group>

    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="确认选择标签">确认</el-button>
        <el-button @click="标签选择弹窗可见 = false">取消</el-button>
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
  客户信息: {
    type: Object,
    default: null
  },
  可用标签列表: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'submit'])

const dialogVisible = ref(false)
const formRef = ref(null)
const 标签选择弹窗可见 = ref(false)
const 临时选中标签 = ref([])

const 是否编辑 = computed(() => !!props.客户信息)

const 表单数据 = reactive({
  customer_code: '',
  name: '',
  id_card: '',
  phone: '',
  wechat: '',
  tags: ''
})

const 验证规则 = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入电话', trigger: 'blur' }]
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
  if (props.客户信息) {
    Object.assign(表单数据, {
      customer_code: props.客户信息.customer_code || '',
      name: props.客户信息.name || '',
      id_card: props.客户信息.id_card || '',
      phone: props.客户信息.phone || '',
      wechat: props.客户信息.wechat || '',
      tags: props.客户信息.tags || ''
    })
  } else {
    重置表单()
  }
}

function 重置表单() {
  表单数据.customer_code = ''
  表单数据.name = ''
  表单数据.id_card = ''
  表单数据.phone = ''
  表单数据.wechat = ''
  表单数据.tags = ''
}

function 打开标签选择弹窗() {
  临时选中标签.value = 表单数据.tags ? 表单数据.tags.split(',').filter(tag => tag.trim()) : []
  标签选择弹窗可见.value = true
}

function 确认选择标签() {
  表单数据.tags = 临时选中标签.value.join(',')
  标签选择弹窗可见.value = false
}

function 关闭标签选择弹窗() {
  临时选中标签.value = []
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
