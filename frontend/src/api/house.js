import request from '../utils/request'

export const 获取房源列表 = (params) => {
  return request.get('/houses', { params })
}

export const 添加房源 = (data) => {
  return request.post('/houses', data)
}

export const 更新房源 = (id, data) => {
  return request.put(`/houses/${id}`, data)
}

export const 删除房源 = (id) => {
  return request.delete(`/houses/${id}`)
}

export const 根据编号获取房源 = (house_code) => {
  return request.get(`/houses/by_code/${house_code}`)
}

export const 获取设置 = () => {
  return request.get('/settings')
}

export const 刷新房源状态 = () => {
  return request.post('/houses/refresh-status')
}
