<template>
  <div id="app">
    <MainLayout />
  </div>
</template>

<script setup>
import MainLayout from './layouts/MainLayout.vue'
import './styles/variables.css'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--颜色-背景);
}

#app {
  width: 100%;
  height: 100vh;
}

/* 覆盖按钮默认圆角为2px */
.el-button {
  border-radius: var(--圆角-sm) !important;
}
</style>
