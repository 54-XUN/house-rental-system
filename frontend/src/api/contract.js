import request from '../utils/request'

export const 获取合同列表 = (params = {}) => {
  return request.get('/contracts', { params })
}

export const 添加合同 = (data) => {
  return request.post('/contracts', data)
}

export const 删除合同 = (id) => {
  return request.delete(`/contracts/${id}`)
}

export const 更新合同 = (id, data) => {
  return request.put(`/contracts/${id}`, data)
}

export const 根据编号获取房源 = (house_code) => {
  return request.get(`/houses/by_code/${house_code}`)
}

export const 根据编号获取客户 = (customer_code) => {
  return request.get(`/customers/by_code/${customer_code}`)
}
