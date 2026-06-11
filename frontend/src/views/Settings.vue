<template>
  <div class="settings-page">
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 左列 - 列表卡片设置 -->
        <el-col :span="8">
          <el-card class="settings-card">
            <template #header>
              <div class="card-header">
                <span>列表卡片设置</span>
              </div>
            </template>

            <div class="setting-item">
              <label>列表卡片列数</label>
              <el-input-number
                v-model="settings.card_columns"
                :min="1"
                :max="10"
                :step="1"
                size="default"
                style="width: 100%"
              />
            </div>

            <div class="status-colors">
              <div class="color-item">
                <div class="color-block" style="background-color: #67c23a;"></div>
                <span>空闲</span>
              </div>
              <div class="color-item">
                <div class="color-block" style="background-color: #909399;"></div>
                <span>已租</span>
              </div>
              <div class="color-item">
                <div class="color-block" style="background-color: #e6a23c;"></div>
                <span>即将到期</span>
              </div>
            </div>

            <div class="setting-item">
              <label>即将到期提醒天数</label>
              <el-input-number
                v-model="settings.expiring_days"
                :min="1"
                :max="365"
                :step="1"
                size="default"
                style="width: 100%"
              />
            </div>

            <el-button type="primary" @click="保存设置" :loading="保存中" style="width: 100%; margin-top: 16px;">
              保存设置
            </el-button>
          </el-card>
        </el-col>

        <!-- 中列 - 字段设置 -->
        <el-col :span="8">
          <el-card class="settings-card">
            <template #header>
              <div class="card-header">
                <span>字段设置</span>
              </div>
            </template>

            <el-row :gutter="12">
              <el-col :span="12">
                <div class="field-section">
                  <h4 class="field-title">小区名称列表</h4>
                  <div class="field-list">
                    <div
                      v-for="(item, index) in 小区列表"
                      :key="index"
                      class="list-item"
                    >
                      {{ item }}
                    </div>
                    <div v-if="!小区列表.length" class="empty-text">暂无数据</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="field-section">
                  <h4 class="field-title">房源标签列表</h4>
                  <div class="field-list">
                    <div
                      v-for="(item, index) in 房源标签列表"
                      :key="index"
                      class="list-item"
                    >
                      {{ item }}
                    </div>
                    <div v-if="!房源标签列表.length" class="empty-text">暂无数据</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-col>

        <!-- 右列 - 模板初始化 -->
        <el-col :span="8">
          <el-card class="settings-card">
            <template #header>
              <div class="card-header">
                <span>模板初始化</span>
              </div>
            </template>

            <el-button type="warning" @click="模板初始化" style="width: 100%; margin-bottom: 16px;">
              模板初始化
            </el-button>

            <el-alert
              type="warning"
              :closable="false"
              show-icon
            >
              <template #title>
                <div class="alert-content">
                  注：初始化功能会将【房源明细】、【客户管理】、【交易流水】这三个工作中的数据清空，同时列表卡片恢复默认设置，操作前请数据备份！
                </div>
              </template>
            </el-alert>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  获取设置,
  更新设置,
  重置系统
} from '../api/settings.js'

const 保存中 = ref(false)

const settings = reactive({
  card_columns: 5,
  expiring_days: 30
})

const 小区列表 = ref([])
const 房源标签列表 = ref([])

onMounted(() => {
  加载设置()
})

async function 加载设置() {
  try {
    const res = await 获取设置()
    const data = res.data || res
    if (data.card_columns) settings.card_columns = parseInt(data.card_columns)
    if (data.expiring_days) settings.expiring_days = parseInt(data.expiring_days)
    if (data.communities) {
      小区列表.value = typeof data.communities === 'string'
        ? JSON.parse(data.communities)
        : data.communities
    }
    if (data.house_tags) {
      房源标签列表.value = typeof data.house_tags === 'string'
        ? JSON.parse(data.house_tags)
        : data.house_tags
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  }
}

async function 保存设置() {
  保存中.value = true
  try {
    const data = {
      card_columns: String(settings.card_columns),
      expiring_days: String(settings.expiring_days)
    }
    await 更新设置(data)
    ElMessage.success('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  } finally {
    保存中.value = false
  }
}

async function 模板初始化() {
  try {
    await ElMessageBox.confirm(
      '确定要初始化吗？此操作不可恢复！',
      '初始化确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 二次确认：输入管理密码
    const { value: 密码 } = await ElMessageBox.prompt(
      '请输入管理密码以确认重置（首次使用或未设置密码可直接确定）',
      '安全验证',
      {
        confirmButtonText: '确定重置',
        cancelButtonText: '取消',
        inputType: 'password',
        inputPlaceholder: '请输入管理密码'
      }
    )

    await 重置系统(密码 || '')
    ElMessage.success('系统已重置')
    await 加载设置()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重置失败:', error)
      ElMessage.error('重置失败')
    }
  }
}
</script>

<style scoped>
.settings-page {
  background-color: #f5f7fa;
  min-height: 100%;
}

.main-content {
  padding: 20px;
}

.settings-card {
  height: 100%;
  min-height: 500px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item label {
  display: block;
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.status-colors {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 4px;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.color-block {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.field-section {
  margin-bottom: 16px;
}

.field-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.field-list {
  max-height: 360px;
  overflow-y: auto;
}

.list-item {
  padding: 8px 12px;
  margin-bottom: 4px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  text-align: center;
}

.empty-text {
  text-align: center;
  color: #909399;
  padding: 20px;
  font-size: 13px;
}

.alert-content {
  font-size: 13px;
  line-height: 1.6;
}
</style>
