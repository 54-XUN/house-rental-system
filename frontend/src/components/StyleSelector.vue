<template>
  <div class="style-selector">
    <el-select
      :model-value="modelValue"
      @update:model-value="$emit('update:modelValue', $event)"
      :placeholder="占位文本"
      size="default"
      style="width: 200px"
    >
      <el-option
        v-for="选项 in 选项列表"
        :key="选项.value"
        :label="选项.label"
        :value="选项.value"
      >
        <div class="style-option">
          <span
            class="color-preview"
            :style="{ backgroundColor: 选项.color }"
          ></span>
          <span>{{ 选项.label }}</span>
        </div>
      </el-option>
    </el-select>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: 'WPS'
  },
  占位文本: {
    type: String,
    default: '请选择样式'
  },
  选项列表: {
    type: Array,
    default: () => [
      { label: 'WPS推荐', value: 'WPS', color: '#f0f9eb' },
      { label: '自定义', value: '自定义', color: '#409eff' }
    ]
  }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.style-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-preview {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid #dcdfe6;
}
</style>
