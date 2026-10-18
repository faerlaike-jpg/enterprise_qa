/**
 * 知识库接口
 */
import request from './request'

/** 查询全部知识库 */
export const getKbList = () => request.get('/kb')

/** 新增知识库 */
export const createKb = (data) => request.post('/kb', data)

/** 修改知识库 */
export const updateKb = (id, data) => request.put(`/kb/${id}`, data)

/** 删除知识库（同时删除向量数据） */
export const deleteKb = (id) => request.delete(`/kb/${id}`)
