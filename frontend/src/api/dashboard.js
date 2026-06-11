import request from '../utils/request'

export const 获取汇总数据 = () => {
  return request.get('/dashboard/summary')
}

export const 获取金额趋势 = () => {
  return request.get('/dashboard/amount_trend')
}

export const 获取客户趋势 = () => {
  return request.get('/dashboard/customer_trend')
}

export const 获取房源状态分布 = () => {
  return request.get('/dashboard/house_status')
}

export const 获取小区排名 = () => {
  return request.get('/dashboard/top_communities')
}

export const 获取最高成交日 = () => {
  return request.get('/dashboard/best_day')
}

export const 获取最高客户月 = () => {
  return request.get('/dashboard/best_month_customers')
}
