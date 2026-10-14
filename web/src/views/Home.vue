<script setup>
import { onMounted, ref } from 'vue'
import { request } from '../api'

const username = ref('')
const error = ref('')

const features = [
  {
    path: '/chat',
    icon: '💬',
    title: '智能助手',
    desc: '用大白话提问，自动去查业务库，再把结论用文字和表格讲给你听。',
  },
  {
    path: '/admin',
    icon: '🗂',
    title: '数据管理',
    desc: '维护仓库和商品主数据。',
  },
  {
    path: '/stats',
    icon: '📊',
    title: '仓库统计',
    desc: '看各仓库的库存占比、库存预警和近半年的出入库趋势。',
  },
  {
    path: '/profile',
    icon: '👤',
    title: '个人中心',
    desc: '查看账号信息、修改登录密码，或者退出登录切换账号。',
  },
]

onMounted(async () => {
  try {
    const data = await request('/auth/me')
    username.value = data.username
  } catch (e) {
    error.value = e.message
  }
})
</script>

<template>
  <div class="home">
    <header class="hero">
      <h1>{{ username || '…' }},欢迎回来！</h1>
      <p class="muted">这里是 ChatBI 物流仓储数据分析助手，挑一个功能开始吧。</p>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="cards">
      <RouterLink v-for="f in features" :key="f.path" :to="f.path" class="feature card">
        <span class="ficon">{{ f.icon }}</span>
        <h3>{{ f.title }}</h3>
        <p class="fdesc">{{ f.desc }}</p>
        <span class="go">进入 →</span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.home { max-width: 1080px; margin: 0 auto; }

.hero { margin-bottom: 28px; }
.hero h1 { margin: 0 0 8px; font-size: 28px; }

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.feature {
  display: flex; flex-direction: column; align-items: flex-start; gap: 10px;
  padding: 24px; text-decoration: none; color: var(--text);
  transition: transform .12s, box-shadow .15s, border-color .15s;
}
.feature:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: #cfd4e2;
}
.ficon { font-size: 30px; }
.feature h3 { margin: 4px 0 0; font-size: 17px; }
.fdesc { margin: 0; color: var(--muted); font-size: 13.5px; line-height: 1.7; flex: 1; }
.go { color: var(--brand); font-size: 13px; font-weight: 600; }
</style>
