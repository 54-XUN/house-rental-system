<template>
  <el-container class="main-layout">
    <!-- 左侧菜单 -->
    <el-aside width="220px" class="aside-menu">
      <div class="menu-header">房屋出租管理系统</div>
      <el-menu
        :default-active="当前路由"
        class="side-menu"
        router
        background-color="#304156"
        text-color="#FFFFFF"
        active-text-color="#FFFFFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计看板</span>
        </el-menu-item>
        <el-menu-item index="/houses">
          <el-icon><House /></el-icon>
          <span>房源列表</span>
        </el-menu-item>
        <el-menu-item index="/house-detail">
          <el-icon><List /></el-icon>
          <span>房源明细</span>
        </el-menu-item>
        <el-menu-item index="/customers">
          <el-icon><User /></el-icon>
          <span>客户管理</span>
        </el-menu-item>
        <el-menu-item index="/contracts">
          <el-icon><Document /></el-icon>
          <span>交易流水</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>参数设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  House,
  User,
  Document,
  DataAnalysis,
  Setting,
  List
} from '@element-plus/icons-vue'

const route = useRoute()

const 当前路由 = computed(() => route.path)
</script>

<style scoped>
.main-layout {
  height: 100vh;
  width: 100%;
}

.aside-menu {
  background-color: #304156;
  color: #fff;
  overflow-y: auto;
}

.menu-header {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 16px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background-color: #263445;
}

.side-menu {
  border-right: none;
}

.side-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
}

.side-menu .el-menu-item:hover {
  background-color: rgba(64, 158, 255, 0.2) !important;
}

.side-menu .el-menu-item.is-active {
  background-color: rgba(64, 158, 255, 0.3) !important;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
}
</style>
