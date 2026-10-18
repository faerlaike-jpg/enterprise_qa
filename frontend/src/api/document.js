/**
 * 知识库文档接口
 */
import request from './request'

/** 分页查询文档 */
export const getDocuments = (params) => request.get('/documents', { params })

/** 上传文档（FormData：kb_id + file），上传后后端同步向量化 */
export const uploadDocument = (formData, onUploadProgress) =>
  request.post('/documents/upload', formData, { onUploadProgress, timeout: 600000 })

/** 重新向量化 */
export const vectorizeDocument = (id) => request.post(`/documents/${id}/vectorize`, null, { timeout: 600000 })

/** 删除文档 */
export const deleteDocument = (id) => request.delete(`/documents/${id}`)
