/**
 * axios 请求封装
 * - 请求拦截：自动携带 JWT Token
 * - 响应拦截：统一处理业务错误码与登录失效
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'qa_token'

/** 读取本地 Token */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

/** 保存 Token */
export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

/** 清除 Token */
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

const service = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

// 请求拦截器：注入 Authorization 头
service.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * 登录失效处理：清空本地登录信息并跳转登录页
 */
function handleUnauthorized() {
  removeToken()
  localStorage.removeItem('qa_user')
  if (!location.pathname.startsWith('/login')) {
    location.href = '/login'
  }
}

// 响应拦截器：code === 200 视为成功，直接返回 data 部分
service.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 200) {
      return res
    }
    ElMessage.error(res.msg || '请求失败')
    return Promise.reject(new Error(res.msg))
  },
  (err) => {
    const status = err.response?.status
    const msg = err.response?.data?.msg
    if (status === 401) {
      ElMessage.error(msg || '登录已失效')
      handleUnauthorized()
    } else {
      ElMessage.error(msg || err.message || '网络异常')
    }
    return Promise.reject(err)
  },
)

export default service
