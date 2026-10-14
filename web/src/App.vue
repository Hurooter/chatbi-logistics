<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearToken, isLoggedIn } from './api'

const route = useRoute()
const router = useRouter()

const navs = [
  { path: '/home', label: '首页', icon: '🏠' },
  { path: '/chat', label: '智能助手', icon: '💬' },
  { path: '/stats', label: '仓库统计', icon: '📊' },
  { path: '/admin', label: '数据管理', icon: '🗂' },
  { path: '/profile', label: '个人中心', icon: '👤' },
]

// isLoggedIn() 读的是响应式 ref，route 也是响应式的，两者任一变化都会重算
const showNav = computed(() => isLoggedIn() && route.path !== '/login')

function logout() {
  clearToken()
  router.push('/login')
}
</script>

<template>
  <div class="shell" :class="{ 'has-sidebar': showNav }">
    <aside v-if="showNav" class="sidebar">
      <div class="brand">
        <span class="mark">📊</span>
        <div class="brand-text">
          <span class="name">ChatBI</span>
          <span class="sub">物流仓储数据分析</span>
        </div>
      </div>

      <nav class="nav">
        <RouterLink
          v-for="n in navs"
          :key="n.path"
          :to="n.path"
          class="nav-item"
          :class="{ active: route.path === n.path }"
        >
          <span class="icon">{{ n.icon }}</span>
          <span class="label">{{ n.label }}</span>
        </RouterLink>
      </nav>

      <div class="foot">
        <button class="ghost small logout" @click="logout">退出登录</button>
      </div>
    </aside>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.shell { height: 100%; display: flex; }

/* ---- 左侧导航栏 ---- */
.sidebar {
  width: 224px; flex-shrink: 0;
  display: flex; flex-direction: column;
  padding: 20px 14px 16px;
  background: #fff;
  border-right: 1px solid var(--border);
}

.brand { display: flex; align-items: center; gap: 11px; padding: 0 8px 20px; }
.mark {
  width: 38px; height: 38px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 19px; border-radius: 11px;
  background: linear-gradient(140deg, #4f46e5, #7c3aed);
  box-shadow: 0 4px 12px rgba(79, 70, 229, .3);
}
.brand-text { display: flex; flex-direction: column; line-height: 1.25; min-width: 0; }
.name { font-weight: 700; font-size: 16px; color: var(--text); }
.sub { font-size: 11px; color: var(--muted); white-space: nowrap; }

.nav { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.nav-item {
  position: relative;
  display: flex; align-items: center; gap: 11px;
  padding: 11px 13px; border-radius: 10px;
  color: #4b5563; text-decoration: none; font-size: 14px;
  transition: background .15s, color .15s;
}
.nav-item .icon { font-size: 16px; width: 20px; text-align: center; }
.nav-item:hover { background: #f3f4f6; }
.nav-item.active { background: var(--brand-soft); color: var(--brand); font-weight: 600; }
.nav-item.active::before {
  content: ''; position: absolute; left: -14px; top: 9px; bottom: 9px;
  width: 3px; border-radius: 0 3px 3px 0; background: var(--brand);
}

.foot { border-top: 1px solid var(--border); padding-top: 14px; }
.logout { width: 100%; }

/* ---- 内容区 ---- */
.content { flex: 1; min-width: 0; min-height: 0; padding: 22px 26px; overflow-y: auto; }
/* 未登录（登录页）时不显示侧栏，内容区不留白，登录页铺满整屏 */
.shell:not(.has-sidebar) .content { padding: 0; }

@media (max-width: 820px) {
  .sidebar { width: 68px; padding: 20px 8px 16px; }
  .brand-text, .nav-item .label, .foot .logout { display: none; }
  .brand { justify-content: center; padding-bottom: 18px; }
  .nav-item { justify-content: center; padding: 12px 0; }
  .nav-item.active::before { left: -8px; }
  .content { padding: 16px; }
}
</style>
