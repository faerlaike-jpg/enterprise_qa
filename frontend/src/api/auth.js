/**
 * 认证相关接口
 */
import request from './request'

/** 登录，password 需为 MD5 后的值 */
export const login = (data) => request.post('/auth/login', data)

/** 获取当前用户信息 */
export const getUserInfo = () => request.get('/auth/info')

/** 修改密码（新旧密码均为 MD5 值） */
export const changePassword = (data) => request.put('/auth/password', data)
