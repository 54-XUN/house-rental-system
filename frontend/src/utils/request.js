import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// API访问令牌（启动时从后端获取）
let _apiToken = null

/** 获取并缓存API令牌（应用启动时调用一次） */
export async function 初始化令牌() {
  try {
    const res = await axios.get('/api/token')
    _apiToken = res.data.token
    // 写入默认请求头
    request.defaults.headers['X-API-Token'] = _apiToken
  } catch (e) {
    console.warn('获取API令牌失败，写操作将被拒绝', e)
  }
}

request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    const res = response.data
    // 后端标准响应结构 {code, data, msg} — 直接透传，保持与现有组件兼容
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code !== 200) {
        // 业务错误：抛出明确错误，携带msg供组件展示
        const err = new Error(res.msg || '请求失败')
        err.code = res.code
        return Promise.reject(err)
      }
    }
    return res  // 成功时返回完整 {code, data, msg}，组件自行取 res.data
  },
  error => {
    // HTTP错误或网络错误：优先读后端的msg字段
    const 后端消息 = error.response?.data?.msg
    ElMessage.error(后端消息 || error.message || '请求失败')
    return Promise.reject(error)
  }
)

export default request
