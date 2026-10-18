/**
 * 用户状态管理（Pinia）
 * 保存 Token 与当前登录用户信息，并持久化到 localStorage
 */
import { defineStore } from 'pinia'
import md5 from 'js-md5'
import { login as loginApi, getUserInfo } from '@/api/auth'
import { getToken, removeToken, setToken } from '@/api/request'

const USER_KEY = 'qa_user'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken() || '',
    user: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
  }),

  getters: {
    /** 是否已登录 */
    isLogin: (state) => !!state.token,
    /** 是否管理员 */
    isAdmin: (state) => state.user?.role === 'admin',
    /** 显示名称 */
    displayName: (state) => state.user?.nickname || state.user?.username || '',
  },

  actions: {
    /**
     * 登录：前端先对明文密码做 MD5，再提交给后端
     * @param {string} username 账号
     * @param {string} password 明文密码
     */
    async login(username, password) {
      const res = await loginApi({ username, password: md5(password) })
      this.token = res.data.token
      this.user = res.data.user
      setToken(this.token)
      localStorage.setItem(USER_KEY, JSON.stringify(this.user))
      return this.user
    },

    /** 从后端刷新当前用户信息 */
    async fetchInfo() {
      const res = await getUserInfo()
      this.user = res.data
      localStorage.setItem(USER_KEY, JSON.stringify(this.user))
    },

    /** 退出登录 */
    logout() {
      this.token = ''
      this.user = null
      removeToken()
      localStorage.removeItem(USER_KEY)
    },
  },
})
