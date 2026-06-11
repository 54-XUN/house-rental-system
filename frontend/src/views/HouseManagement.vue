<template>
  <div class="house-management">
    <!-- 右侧内容区 -->
    <div class="main-content">
        <!-- 顶部操作栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <h2 class="title">房源列表</h2>
          </div>
          
          <div class="toolbar-right">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              添加房源
            </el-button>
            <el-button @click="handleToggleAll">
              {{ 全部展开 ? '全部折叠' : '全部展开' }}
            </el-button>
            <el-button @click="handleLoadAll">
              全部房源
            </el-button>
            <el-button @click="筛选对话框可见 = true">
              <el-icon><Filter /></el-icon>
              高级筛选
            </el-button>
          </div>
        </div>

        <!-- 卡片视图 -->
        <div class="card-view">
          <div v-if="分组后房源列表.length === 0" class="empty-state">
            <el-empty description="暂无房源数据" />
          </div>
          
          <div v-else class="community-groups">
            <div
              v-for="(group, index) in 分组后房源列表"
              :key="group.名称"
              class="community-group"
            >
              <div class="group-header" @click="toggleGroup(index)">
                <div class="group-title">
                  <el-icon class="toggle-icon">
                    <component :is="group.展开 ? 'Minus' : 'Plus'" />
                  </el-icon>
                  <span>{{ group.名称 }}</span>
                  <el-badge :value="group.房源.length" :max="99" class="count-badge" />
                </div>
              </div>
              
              <el-collapse-transition>
                <div v-show="group.展开" class="group-content">
                  <div class="house-grid" :style="{ gridTemplateColumns: `repeat(${卡片列数}, 1fr)` }">
                    <HouseCard
                      v-for="house in group.房源"
                      :key="house.id"
                      :house="house"
                      @click="handleViewHouse"
                      @edit="handleEdit"
                      @delete="handleDelete"
                    />
                  </div>
                </div>
              </el-collapse-transition>
            </div>
          </div>
        </div>
      </div>

    <!-- 进度条对话框 -->
    <ProgressBar
      v-model:visible="进度条可见"
      :total="房源总数"
      @complete="handleProgressComplete"
    />

    <!-- 高级筛选对话框 -->
    <HouseFilter
      v-model:visible="筛选对话框可见"
      :可用标签列表="可用标签列表"
      @filter="handleFilter"
    />

    <!-- 添加/编辑表单对话框 -->
    <HouseForm
      v-model:visible="表单对话框可见"
      :房源信息="当前编辑房源"
      :小区列表="小区列表"
      :可用标签列表="可用标签列表"
      @submit="handleSubmit"
    />

    <!-- 房源详情对话框 -->
    <el-dialog
      v-model="详情对话框可见"
      title="房源详情"
      width="600px"
      :append-to-body="true"
      :close-on-click-modal="false"
      :modal-transition="false"
      :dialog-transition="false"
      destroy-on-close
      class="房源详情对话框"
    >
      <el-descriptions :column="2" border class="房源描述列表">
        <el-descriptions-item label="房源编号" label-class-name="描述标签" content-class-name="描述内容">{{ 查看中的房源?.house_code }}</el-descriptions-item>
        <el-descriptions-item label="状态" label-class-name="描述标签" content-class-name="描述内容">
          <el-tag :type="获取状态类型(查看中的房源?.status)" size="small">
            {{ 查看中的房源?.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="小区名称" label-class-name="描述标签" content-class-name="描述内容">{{ 查看中的房源?.community }}</el-descriptions-item>
        <el-descriptions-item label="详细地址" label-class-name="描述标签" content-class-name="描述内容">{{ 查看中的房源?.address }}</el-descriptions-item>
        <el-descriptions-item label="楼层" label-class-name="描述标签" content-class-name="描述内容">{{ 查看中的房源?.floor }}层</el-descriptions-item>
        <el-descriptions-item label="户型" label-class-name="描述标签" content-class-name="描述内容">
          {{ 查看中的房源?.room }}室{{ 查看中的房源?.hall }}厅
        </el-descriptions-item>
        <el-descriptions-item label="面积" label-class-name="描述标签" content-class-name="描述内容">{{ 查看中的房源?.area }}㎡</el-descriptions-item>
        <el-descriptions-item label="月租金" label-class-name="描述标签" content-class-name="描述内容">
          ¥{{ 查看中的房源?.rent }}
        </el-descriptions-item>
        <el-descriptions-item label="标签" :span="2" label-class-name="描述标签-标签行" content-class-name="描述内容-标签行">
          <div class="标签容器">
            <el-tag
              v-for="tag in 获取标签列表(查看中的房源?.tags)"
              :key="tag"
              size="small"
              type="info"
              effect="plain"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="添加日期" label-class-name="描述标签" content-class-name="描述内容">{{ 查看中的房源?.add_date }}</el-descriptions-item>
        <el-descriptions-item label="到期日期" label-class-name="描述标签" content-class-name="描述内容">{{ 查看中的房源?.expire_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="合同编号" :span="2" label-class-name="描述标签" content-class-name="描述内容">
          {{ 查看中的房源?.contract_code || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Filter,
  Minus
} from '@element-plus/icons-vue'
import HouseCard from '../components/HouseCard.vue'
import HouseFilter from '../components/HouseFilter.vue'
import HouseForm from '../components/HouseForm.vue'
import ProgressBar from '../components/ProgressBar.vue'
import { 获取房源列表, 添加房源, 更新房源, 删除房源, 获取设置 } from '../api/house.js'

const router = useRouter()

const loading = ref(false)
const 房源列表 = ref([])
const 小区列表 = ref([])
const 可用标签列表 = ref([])
const 卡片列数 = ref(5)

const 筛选对话框可见 = ref(false)
const 表单对话框可见 = ref(false)
const 进度条可见 = ref(false)
const 当前编辑房源 = ref(null)
const 全部展开 = ref(true)

const 详情对话框可见 = ref(false)
const 查看中的房源 = ref(null)

const 分组数据 = ref([])

const 房源总数 = computed(() => 房源列表.value.length)

const 分组后房源列表 = computed(() => {
  return 分组数据.value
})

onMounted(() => {
  加载设置()
  加载房源列表()
  响应式布局监听()
})

function 响应式布局监听() {
  const 更新列数 = () => {
    const 宽度 = window.innerWidth
    if (宽度 >= 1200) {
      卡片列数.value = 5
    } else if (宽度 >= 992) {
      卡片列数.value = 4
    } else {
      卡片列数.value = 3
    }
  }
  
  更新列数()
  window.addEventListener('resize', 更新列数)
}

async function 加载设置() {
  try {
    const res = await 获取设置()
    const data = res.data || res  // 兼容拦截器返回格式
    if (data.communities) {
      小区列表.value = typeof data.communities === 'string'
        ? JSON.parse(data.communities)
        : data.communities
    }
    if (data.house_tags) {
      可用标签列表.value = typeof data.house_tags === 'string'
        ? JSON.parse(data.house_tags)
        : data.house_tags
    }
    if (data.card_columns) {
      卡片列数.value = data.card_columns
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败，部分功能可能不可用')
  }
}

async function 加载房源列表(params = {}) {
  loading.value = true
  try {
    const 默认参数 = { per_page: 500, status_exclude: '已租' }
    const 合并参数 = { ...默认参数, ...params }
    const res = await 获取房源列表(合并参数)
    const data = res.data || res  // 兼容拦截器返回格式
    房源列表.value = Array.isArray(data) ? data : (data.items || [])
    按小区分组()

    if (Object.keys(params).length > 0 && data.total !== undefined) {
      ElMessage.success(`找到 ${data.total} 条符合条件的房源`)
    }
  } catch (error) {
    console.error('加载房源失败:', error)
    ElMessage.error('加载房源失败，请检查网络连接后重试')
    房源列表.value = []
  } finally {
    loading.value = false
  }
}

function 按小区分组() {
  const groups = {}
  
  房源列表.value.forEach(house => {
    const community = house.community || '未分类'
    if (!groups[community]) {
      groups[community] = []
    }
    groups[community].push(house)
  })
  
  分组数据.value = Object.keys(groups).map(名称 => ({
    名称,
    房源: groups[名称],
    展开: 全部展开.value
  }))
}

function toggleGroup(index) {
  if (分组数据.value[index]) {
    分组数据.value[index].展开 = !分组数据.value[index].展开
  }
}

function handleToggleAll() {
  全部展开.value = !全部展开.value
  分组数据.value.forEach(group => {
    group.展开 = 全部展开.value
  })
}

function handleLoadAll() {
  if (房源总数.value > 0) {
    进度条可见.value = true
  } else {
    ElMessage.warning('暂无房源数据')
  }
}

function handleProgressComplete() {
  全部展开.value = true
  分组数据.value.forEach(group => {
    group.展开 = true
  })
}

function handleFilter(params) {
  加载房源列表(params)
}

function handleAdd() {
  当前编辑房源.value = null
  表单对话框可见.value = true
}

function handleEdit(house) {
  当前编辑房源.value = house
  表单对话框可见.value = true
}

async function handleSubmit(data) {
  try {
    if (当前编辑房源.value) {
      await 更新房源(当前编辑房源.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await 添加房源(data)
      ElMessage.success('添加成功')
    }
    await 加载房源列表()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请稍后重试')
  }
}

async function handleDelete(house) {
  try {
    await ElMessageBox.confirm(
      `确认删除房源 ${house.house_code} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await 删除房源(house.id)
    ElMessage.success('删除成功')
    await 加载房源列表()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

function handleViewHouse(house) {
  查看中的房源.value = house
  详情对话框可见.value = true
}

function 获取标签列表(tags) {
  if (!tags) return []
  return tags.split(',').filter(tag => tag.trim())
}

function 获取状态类型(status) {
  const 状态映射 = {
    '空闲': 'success',
    '已租': 'info',
    '即将到期': 'warning'
  }
  return 状态映射[status] || 'info'
}
</script>

<style scoped>
.house-management {
  width: 100%;
  height: 100%;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

.card-view {
  min-height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: #fff;
  border-radius: 8px;
}

.community-groups {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.community-group {
  margin-bottom: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.community-group:last-child {
  margin-bottom: 0;
}

.group-header {
  padding: 15px 20px;
  background: #f5f7fa;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s;
}

.group-header:hover {
  background: #ecf5ff;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.toggle-icon {
  font-size: 14px;
  color: #909399;
}

.count-badge {
  margin-left: auto;
}

.group-content {
  padding: 20px;
  background: #fff;
}

.house-grid {
  display: grid;
  gap: 16px;
}

.tag-item {
  margin-right: 6px;
  margin-bottom: 4px;
}

.标签容器 {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 禁用房源详情对话框动画 */
:deep(.房源详情对话框 .el-overlay-dialog) {
  transition: none !important;
  animation: none !important;
}

:deep(.房源详情对话框 .el-dialog) {
  transition: none !important;
  animation: none !important;
  margin-top: 15vh !important;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

:deep(.房源详情对话框 .el-dialog__header) {
  padding: 16px 20px 10px;
  margin: 0;
  flex-shrink: 0;
}

:deep(.房源详情对话框 .el-dialog__body) {
  padding: 20px;
  overflow-y: auto;
  flex-shrink: 1;
}

/* 固定描述列表布局 */
:deep(.房源描述列表) {
  table-layout: fixed !important;
  width: 100% !important;
}

:deep(.房源描述列表 .el-descriptions__table) {
  table-layout: fixed !important;
}

:deep(.描述标签) {
  width: 90px !important;
  min-width: 90px !important;
  max-width: 90px !important;
  white-space: nowrap !important;
}

:deep(.描述内容) {
  min-width: 180px !important;
  word-break: break-all !important;
}

:deep(.描述标签-标签行) {
  width: 90px !important;
  min-width: 90px !important;
  max-width: 90px !important;
  vertical-align: top !important;
}

:deep(.描述内容-标签行) {
  width: auto !important;
}
</style>
