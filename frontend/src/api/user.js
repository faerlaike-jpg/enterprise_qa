/**
 * 用户管理接口（管理员）
 */
import request from './request'

/** 分页查询用户 */
export const getUsers = (params) => request.get('/users', { params })

/** 新增用户 */
export const createUser = (data) => request.post('/users', data)

/** 修改用户 */
export const updateUser = (id, data) => request.put(`/users/${id}`, data)

/** 重置密码为 123456 */
export const resetPassword = (id) => request.put(`/users/${id}/reset-password`)

/** 删除用户 */
export const deleteUser = (id) => request.delete(`/users/${id}`)
