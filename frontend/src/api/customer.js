import request from '../utils/request'

export const 获取客户列表 = (params) => {
  return request.get('/customers', { params })
}

export const 添加客户 = (data) => {
  return request.post('/customers', data)
}

export const 更新客户 = (id, data) => {
  return request.put(`/customers/${id}`, data)
}

export const 删除客户 = (id) => {
  return request.delete(`/customers/${id}`)
}

export const 根据编号获取客户 = (customer_code) => {
  return request.get(`/customers/by_code/${customer_code}`)
}
