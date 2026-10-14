import { ref } from 'vue'

const BASE = '/api'

// token 用 ref 存：localStorage 变化不是响应式的，套一层 ref 才能让界面自动更新
const token = ref(localStorage.getItem('token') || '')

export function getToken() {
  return token.value
}

export function setToken(value) {
  token.value = value
  localStorage.setItem('token', value)
}

export function clearToken() {
  token.value = ''
  localStorage.removeItem('token')
}

export function isLoggedIn() {
  return !!token.value
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function pickError(data, status) {
  if (typeof data?.detail === 'string') return data.detail
  if (Array.isArray(data?.detail)) return data.detail.map((d) => d.msg).join('；')
  return `请求失败 (${status})`
}

export async function request(path, { method = 'GET', body } = {}) {
  const headers = { ...authHeaders() }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(pickError(data, res.status))
  return data
}

// 流式对话：onToken 收正文，onStatus 收阶段提示（如「正在查询数据…」）
export async function streamChat({ question, thread_id }, { onToken, onStatus, onSqls } = {}) {
  const res = await fetch(BASE + '/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ question, thread_id }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(pickError(data, res.status))
  }
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    const lines = buf.split('\n')
    buf = lines.pop()
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      try {
        const data = JSON.parse(line.slice(6))
        if (data.token) onToken && onToken(data.token)
        else if (data.status) onStatus && onStatus(data.status)
        else if (data.sqls) onSqls && onSqls(data.sqls)
      } catch { /* 不完整的块，跳过 */ }
    }
  }
}
