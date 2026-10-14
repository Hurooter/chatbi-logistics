<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { request, setToken } from '../api'

const router = useRouter()
const mode = ref('login')
const username = ref('')
const password = ref('')
const error = ref('')
const hint = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  hint.value = ''
  if (!username.value || !password.value) {
    error.value = '用户名和密码都要填'
    return
  }
  loading.value = true
  try {
    if (mode.value === 'register') {
      await request('/auth/register', {
        method: 'POST',
        body: { username: username.value, password: password.value },
      })
      mode.value = 'login'
      hint.value = '注册成功，请登录'
      return
    }
    const { token } = await request('/auth/login', {
      method: 'POST',
      body: { username: username.value, password: password.value },
    })
    setToken(token)
    router.push('/home')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth">
    <section class="brand-pane">
      <div class="brand-inner">
        <div class="logo">📊</div>
        <h1>ChatBI</h1>
        <p class="tagline">物流仓储数据分析助手</p>
      </div>
    </section>

    <section class="form-pane">
      <div class="form-inner">
        <h2>{{ mode === 'login' ? '欢迎回来' : '创建账号' }}</h2>
        <p class="muted">{{ mode === 'login' ? '登录后开始你的数据分析' : '注册一个账号，马上开始' }}</p>

        <div class="tabs">
          <button :class="{ ghost: mode !== 'login' }" @click="mode = 'login'">登录</button>
          <button :class="{ ghost: mode !== 'register' }" @click="mode = 'register'">注册</button>
        </div>

        <label class="field">
          <span>用户名</span>
          <input v-model="username" placeholder="请输入用户名" @keyup.enter="submit" />
        </label>
        <label class="field">
          <span>密码</span>
          <input v-model="password" type="password" placeholder="请输入密码" @keyup.enter="submit" />
        </label>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="hint" class="hint">{{ hint }}</p>

        <button class="submit" :disabled="loading" @click="submit">
          {{ loading ? '处理中…' : (mode === 'login' ? '登 录' : '注 册') }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.auth { display: grid; grid-template-columns: 1.05fr .95fr; min-height: 100vh; }

.brand-pane {
  background: linear-gradient(150deg, #4f46e5 0%, #6d28d9 55%, #7c3aed 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 56px;
}
.brand-inner { max-width: 460px; }
.logo { font-size: 56px; margin-bottom: 22px; }
.brand-pane h1 { font-size: 54px; margin: 0 0 10px; }
.tagline { font-size: 22px; opacity: .9; margin: 0; }

.form-pane { display: flex; align-items: center; justify-content: center; padding: 40px; }
.form-inner { width: 100%; max-width: 360px; }
.form-inner h2 { margin: 0 0 6px; font-size: 26px; }
.form-inner > .muted { margin-bottom: 26px; }

.tabs { display: flex; gap: 8px; margin-bottom: 22px; }
.tabs button { flex: 1; }

.field { display: block; margin-bottom: 16px; }
.field span { display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; }

.hint { color: var(--ok); font-size: 14px; margin: 4px 0 0; }
.submit { width: 100%; padding: 12px; margin-top: 10px; font-size: 15px; }

@media (max-width: 860px) {
  .auth { grid-template-columns: 1fr; }
  .brand-pane { display: none; }
}
</style>
