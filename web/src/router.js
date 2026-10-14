import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from './api'

import Login from './views/Login.vue'
import Home from './views/Home.vue'
import Chat from './views/Chat.vue'
import Profile from './views/Profile.vue'
import Admin from './views/Admin.vue'
import Stats from './views/Stats.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', name: 'login', component: Login },
  { path: '/home', name: 'home', component: Home, meta: { auth: true } },
  { path: '/chat', name: 'chat', component: Chat, meta: { auth: true } },
  { path: '/profile', name: 'profile', component: Profile, meta: { auth: true } },
  { path: '/admin', name: 'admin', component: Admin, meta: { auth: true } },
  { path: '/stats', name: 'stats', component: Stats, meta: { auth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：没登录一律赶去登录页；已登录就别再进登录页
router.beforeEach((to) => {
  const logged = !!getToken()
  if (to.meta.auth && !logged) return '/login'
  if (to.path === '/login' && logged) return '/home'
})

export default router
