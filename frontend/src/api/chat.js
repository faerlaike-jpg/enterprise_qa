/**
 * 智能问答接口
 */
import request, { getToken } from './request'

/** 当前用户的会话列表 */
export const getSessions = () => request.get('/chat/sessions')

/** 新建会话 */
export const createSession = (data) => request.post('/chat/sessions', data)

/** 修改会话（标题 / 知识库） */
export const updateSession = (id, data) => request.put(`/chat/sessions/${id}`, data)

/** 删除会话 */
export const deleteSession = (id) => request.delete(`/chat/sessions/${id}`)

/** 会话消息列表 */
export const getMessages = (id) => request.get(`/chat/sessions/${id}/messages`)

/** 点赞 / 点踩 */
export const sendFeedback = (messageId, type) => request.post(`/chat/messages/${messageId}/feedback`, { type })

/** 问答记录（管理员） */
export const getRecords = (params) => request.get('/chat/records', { params })

/**
 * SSE 流式问答
 * 由于 EventSource 不支持 POST 与自定义请求头，这里使用 fetch + ReadableStream 手动解析 SSE
 * @param {Object} data { session_id, question }
 * @param {Function} onEvent 每收到一个事件时回调，参数为事件对象
 * @param {AbortSignal} signal 用于中断请求
 */
export async function streamChat(data, onEvent, signal) {
  const resp = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
    signal,
  })

  // 非流式响应说明参数校验失败，直接返回 JSON 错误
  const contentType = resp.headers.get('content-type') || ''
  if (!contentType.includes('text/event-stream')) {
    const json = await resp.json().catch(() => ({}))
    throw new Error(json.msg || `请求失败（${resp.status}）`)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE 以空行分隔事件
    const parts = buffer.split('\n\n')
    buffer = parts.pop()
    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data:')) continue
      try {
        onEvent(JSON.parse(line.slice(5).trim()))
      } catch (e) {
        console.warn('SSE 解析失败', line)
      }
    }
  }
}
