/**
 * 路由配置与角色守卫
 * - 管理员：可访问 /admin/** 后台与 /chat 对话页
 * - 普通用户：只能访问 /chat 对话页
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/chat/ChatView.vue'),
    meta: { title: '智能问答' },
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/admin/home',
    meta: { admin: true },
    children: [
      {
        path: 'home',
        name: 'AdminHome',
        component: () => import('@/views/admin/Home.vue'),
        meta: { title: '数据概览', icon: 'DataAnalysis', admin: true },
      },
      {
        path: 'kb',
        name: 'KnowledgeBase',
        component: () => import('@/views/admin/KnowledgeBase.vue'),
        meta: { title: '知识库管理', icon: 'Collection', admin: true },
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('@/views/admin/DocumentManage.vue'),
        meta: { title: '文档管理', icon: 'Document', admin: true },
      },
      {
        path: 'records',
        name: 'ChatRecords',
        component: () => import('@/views/admin/ChatRecords.vue'),
        meta: { title: '问答记录', icon: 'ChatDotSquare', admin: true },
      },
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { title: '用户管理', icon: 'User', admin: true },
      },
    ],
  },
  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * 全局前置守卫：登录校验 + 角色权限校验
 */
router.beforeEach((to) => {
  const store = useUserStore()
  document.title = `${to.meta.title ? to.meta.title + ' · ' : ''}智问企业知识库`

  if (to.meta.public) {
    // 已登录用户访问登录页，直接跳转到对应首页
    if (store.isLogin && to.path === '/login') {
      return store.isAdmin ? '/admin/home' : '/chat'
    }
    return true
  }
  if (!store.isLogin) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.admin && !store.isAdmin) {
    return '/chat'
  }
  return true
})

export default router
