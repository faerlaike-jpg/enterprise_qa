/**
 * 首页统计接口
 */
import request from './request'

/** 获取首页统计数据 */
export const getStats = () => request.get('/dashboard/stats')
