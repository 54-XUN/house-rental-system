import request from '../utils/request'

export const 获取设置 = () => {
  return request.get('/settings')
}

export const 更新设置 = (data) => {
  return request.put('/settings', data)
}

export const 重置系统 = () => {
  return request.post('/settings/reset')
}

export const 导入示例数据 = () => {
  return request.post('/import-example')
}

export const 删除测试数据 = () => {
  return request.post('/delete-test-data')
}
