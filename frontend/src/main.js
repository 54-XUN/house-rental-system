import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/dialog-no-animation.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import App from './App.vue'
import router from './router'
import { 初始化令牌 } from './utils/request'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus, {
  locale: zhCn
})
app.use(router)

// 先获取API访问令牌，再挂载应用（避免写操作401）
;(async function 启动() {
  await 初始化令牌()
  app.mount('#app')
})()
