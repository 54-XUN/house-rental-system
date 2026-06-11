<template>
  <div class="tag-editor">
    <div class="tag-list">
      <div
        v-for="(item, index) in 列表"
        :key="index"
        class="tag-item"
      >
        <el-input
          v-model="列表[index]"
          :placeholder="占位文本"
          size="default"
          class="tag-input"
        />
        <el-button
          type="danger"
          :icon="Delete"
          circle
          size="small"
          @click="删除项(index)"
        />
      </div>
    </div>
    <el-button
      type="primary"
      :icon="Plus"
      size="default"
      plain
      @click="添加项"
    >
      + 添加
    </el-button>
  </div>
</template>

<script setup>
import { Delete, Plus } from '@element-plus/icons-vue'

const props = defineProps({
  列表: {
    type: Array,
    required: true
  },
  占位文本: {
    type: String,
    default: '请输入内容'
  }
})

const emit = defineEmits(['update:列表'])

function 删除项(index) {
  const 新列表 = [...props.列表]
  新列表.splice(index, 1)
  emit('update:列表', 新列表)
}

function 添加项() {
  const 新列表 = [...props.列表, '']
  emit('update:列表', 新列表)
}
</script>

<style scoped>
.tag-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tag-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-input {
  flex: 1;
  max-width: 400px;
}
</style>
