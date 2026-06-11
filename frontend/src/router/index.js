import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/houses'
  },
  {
    path: '/houses',
    name: 'HouseManagement',
    component: () => import('../views/HouseManagement.vue'),
    meta: { title: '房源列表' }
  },
  {
    path: '/house-detail',
    name: 'HouseDetail',
    component: () => import('../views/HouseDetail.vue'),
    meta: { title: '房源明细' }
  },
  {
    path: '/customers',
    name: 'CustomerManagement',
    component: () => import('../views/CustomerManagement.vue'),
    meta: { title: '客户管理' }
  },
  {
    path: '/contracts',
    name: 'ContractManagement',
    component: () => import('../views/ContractManagement.vue'),
    meta: { title: '交易流水' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '统计看板' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { title: '参数设置' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '房屋出租管理系统'
  next()
})

export default router
