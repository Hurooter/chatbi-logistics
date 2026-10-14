<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { clearToken, request } from '../api'

const router = useRouter()
const oldPassword = ref('')
const newPassword = ref('')
const error = ref('')
const hint = ref('')
const loading = ref(false)

async function changePassword() {
  error.value = ''
  hint.value = ''
  if (!oldPassword.value || !newPassword.value) {
    error.value = '原密码和新密码都要填'
    return
  }
  loading.value = true
  try {
    await request('/auth/password', {
      method: 'POST',
      body: { old_password: oldPassword.value, new_password: newPassword.value },
    })
    hint.value = '密码已修改，下次登录请用新密码'
    oldPassword.value = ''
    newPassword.value = ''
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function logout() {
  clearToken()
  router.push('/login')
}
</script>

<template>
  <div class="profile">
    <header class="hero">
      <div class="avatar">👤</div>
      <div>
        <h1>个人中心</h1>
        <p class="muted">管理账号信息与安全设置</p>
      </div>
    </header>

    <div class="panels">
      <section class="card panel">
        <h2>修改密码</h2>
        <p class="muted">定期更换密码，账号更安全</p>
        <label class="field">
          <span>原密码</span>
          <input v-model="oldPassword" type="password" placeholder="请输入原密码" />
        </label>
        <label class="field">
          <span>新密码</span>
          <input v-model="newPassword" type="password" placeholder="请输入新密码" />
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="hint" class="hint">{{ hint }}</p>
        <button :disabled="loading" @click="changePassword">
          {{ loading ? '处理中…' : '确认修改' }}
        </button>
      </section>

      <section class="card panel">
        <h2>切换账号</h2>
        <p class="muted">退出后，用另一个账号登录即可切换</p>
        <div class="spacer"></div>
        <button class="ghost" @click="logout">退出登录</button>
      </section>
    </div>
  </div>
</template>

<style scoped>
.profile { max-width: 1080px; margin: 0 auto; }

.hero { display: flex; align-items: center; gap: 18px; margin-bottom: 26px; }
.avatar {
  width: 62px; height: 62px; border-radius: 50%;
  background: linear-gradient(140deg, #4f46e5, #7c3aed);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; box-shadow: var(--shadow-md);
}
.hero h1 { margin: 0 0 4px; font-size: 24px; }

.panels { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }
.panel { padding: 26px; display: flex; flex-direction: column; }
.panel h2 { margin: 0 0 6px; font-size: 17px; }
.panel > .muted { margin-bottom: 20px; }

.field { display: block; margin-bottom: 14px; }
.field span { display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; }

.hint { color: var(--ok); font-size: 14px; margin: 4px 0 0; }
.panel button { align-self: flex-start; margin-top: 8px; }
.spacer { flex: 1; }
</style>
