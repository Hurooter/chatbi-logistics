<script setup>
import { nextTick, onMounted, reactive, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import { request, streamChat } from '../api'

const md = new MarkdownIt({ linkify: true, breaks: true })

const conversations = ref([])
const currentId = ref('')
const messages = ref([])
const input = ref('')
const sending = ref(false)
const status = ref('')
const error = ref('')
const bodyEl = ref(null)

async function loadConversations() {
  try {
    conversations.value = await request('/conversations')
  } catch (e) {
    error.value = e.message
  }
}

async function newConversation() {
  error.value = ''
  const { thread_id } = await request('/conversations', { method: 'POST' })
  await loadConversations()
  await openConversation(thread_id)
}

async function openConversation(id) {
  currentId.value = id
  messages.value = []
  try {
    messages.value = await request(`/conversations/${id}/messages`)
    scrollDown()
  } catch (e) {
    error.value = e.message
  }
}

async function removeConversation(c) {
  if (!confirm('确定删除这个会话？')) return
  error.value = ''
  try {
    await request(`/conversations/${c.thread_id}`, { method: 'DELETE' })
    await loadConversations()
    if (currentId.value === c.thread_id) {
      if (conversations.value.length) {
        await openConversation(conversations.value[0].thread_id)
      } else {
        currentId.value = ''
        messages.value = []
      }
    }
  } catch (e) {
    error.value = e.message
  }
}

function scrollDown() {
  nextTick(() => {
    if (bodyEl.value) bodyEl.value.scrollTop = bodyEl.value.scrollHeight
  })
}

async function send() {
  const q = input.value.trim()
  if (!q || sending.value) return
  if (!currentId.value) {
    try {
      await newConversation()
    } catch (e) {
      error.value = e.message
      return
    }
  }
  error.value = ''
  input.value = ''
  messages.value.push({ role: 'user', content: q })
  const ai = reactive({ role: 'ai', content: '', sqls: [] })
  messages.value.push(ai)
  sending.value = true
  status.value = '正在思考…'
  scrollDown()
  try {
    await streamChat({ question: q, thread_id: currentId.value }, {
      onToken: (token) => {
        ai.content += token
        scrollDown()
      },
      onStatus: (s) => {
        status.value = s
      },
      onSqls: (list) => {
        ai.sqls = list
      },
    })
  } catch (e) {
    ai.content = `出错了：${e.message}`
  } finally {
    sending.value = false
    status.value = ''
    loadConversations()
  }
}

async function init() {
  await loadConversations()
  // 空列表不自动建会话，等用户直接输入时再懒创建（见 send）
  if (conversations.value.length) {
    await openConversation(conversations.value[0].thread_id)
  }
}

onMounted(init)
</script>

<template>
  <div class="chat">
    <aside class="card side">
      <div class="side-head">
        <span class="side-title">我的会话</span>
        <button class="small" @click="newConversation">＋ 新建</button>
      </div>
      <ul>
        <li
          v-for="c in conversations"
          :key="c.thread_id"
          :class="{ active: c.thread_id === currentId }"
          @click="openConversation(c.thread_id)"
        >
          <span class="title">{{ c.title }}</span>
          <span class="del" @click.stop="removeConversation(c)">×</span>
        </li>
      </ul>
      <p v-if="!conversations.length" class="muted empty">还没有会话，直接提问即可开始</p>
    </aside>

    <section class="card main">
      <div ref="bodyEl" class="body">
        <div v-if="!currentId" class="placeholder">
          <div class="ph-icon">💬</div>
          <p class="muted">直接输入问题，开始新对话</p>
        </div>

        <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
          <div v-if="m.role === 'ai'" class="avatar">🤖</div>
          <div v-if="m.role === 'user'" class="bubble">{{ m.content }}</div>
          <div v-else class="col">
            <div v-if="!m.content && sending && i === messages.length - 1" class="bubble waiting">
              <span class="dots"><i></i><i></i><i></i></span>
              <span>{{ status || '正在思考…' }}</span>
            </div>
            <div v-else class="bubble md" v-html="md.render(m.content || '')"></div>
            <details v-if="m.sqls && m.sqls.length" class="sqlbox">
              <summary>查看 SQL（{{ m.sqls.length }} 条）</summary>
              <pre><code>{{ m.sqls.join('\n\n') }}</code></pre>
            </details>
          </div>
        </div>
      </div>

      <p v-if="error" class="error pad">{{ error }}</p>

      <div class="composer">
        <input
          v-model="input"
          placeholder="问点什么..."
          :disabled="sending"
          @keyup.enter="send"
        />
        <button :disabled="sending || !input.trim()" @click="send">{{ sending ? '…' : '发送' }}</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.chat { display: grid; grid-template-columns: 250px 1fr; gap: 18px; height: 100%; }

.side { padding: 16px; display: flex; flex-direction: column; gap: 12px; overflow: hidden; }
.side-head { display: flex; align-items: center; justify-content: space-between; }
.side-title { font-weight: 600; font-size: 14px; }
.side ul { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; }
.side li {
  display: flex; justify-content: space-between; align-items: center; gap: 6px;
  padding: 9px 11px; border-radius: 9px; cursor: pointer; font-size: 14px;
  transition: background .15s;
}
.side li:hover { background: #f3f4f6; }
.side li.active { background: var(--brand-soft); color: var(--brand); font-weight: 500; }
.title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.del { color: #c4c9d4; font-size: 17px; line-height: 1; padding: 0 2px; }
.del:hover { color: var(--danger); }
.empty { padding: 12px 4px; }

.main { display: flex; flex-direction: column; overflow: hidden; }
.body { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }

.placeholder { margin: auto; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 10px; }
.ph-icon { font-size: 40px; opacity: .5; }

.msg { display: flex; gap: 10px; align-items: flex-start; }
.msg.user { flex-direction: row-reverse; }
.avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: var(--brand-soft); display: flex; align-items: center; justify-content: center; font-size: 16px;
}
.bubble {
  max-width: 76%; padding: 11px 15px; border-radius: 14px;
  line-height: 1.7; font-size: 14px; word-break: break-word;
}
.msg.user .bubble {
  background: linear-gradient(140deg, #4f46e5, #6366f1);
  color: #fff; border-top-right-radius: 4px; white-space: pre-wrap;
}
.msg.ai .bubble { background: #f7f8fb; border: 1px solid #eceef4; border-top-left-radius: 4px; }
.msg.ai .col {
  display: flex; flex-direction: column; align-items: flex-start;
  gap: 8px; min-width: 0; max-width: 76%;
}
.msg.ai .col .bubble { max-width: 100%; }

/* ---- 可折叠的 SQL 展示 ---- */
.sqlbox { width: 100%; border: 1px solid var(--border); border-radius: 10px; background: #fff; overflow: hidden; }
.sqlbox summary {
  cursor: pointer; padding: 8px 12px; font-size: 12.5px; color: var(--muted);
  user-select: none; list-style: none;
}
.sqlbox summary::before { content: '▸ '; }
.sqlbox[open] summary::before { content: '▾ '; }
.sqlbox summary:hover { color: var(--brand); }
.sqlbox pre {
  margin: 0; padding: 12px; background: #1f2937; color: #e5e7eb;
  font-size: 12.5px; line-height: 1.65; overflow-x: auto; white-space: pre-wrap;
  word-break: break-word; font-family: ui-monospace, Consolas, monospace;
}

/* ---- 等待回复的动态提示 ---- */
.waiting { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: 14px; }
.dots { display: inline-flex; gap: 4px; }
.dots i {
  width: 6px; height: 6px; border-radius: 50%; background: #9aa1b2;
  animation: dot-bounce 1.2s infinite ease-in-out both;
}
.dots i:nth-child(2) { animation-delay: .15s; }
.dots i:nth-child(3) { animation-delay: .3s; }
@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(.5); opacity: .35; }
  40% { transform: scale(1); opacity: 1; }
}

/* ---- AI 气泡里的 Markdown 排版 ---- */
.bubble.md :deep(>*:first-child) { margin-top: 0; }
.bubble.md :deep(>*:last-child) { margin-bottom: 0; }
.bubble.md :deep(p) { margin: 0 0 9px; }
.bubble.md :deep(h1), .bubble.md :deep(h2), .bubble.md :deep(h3), .bubble.md :deep(h4) {
  font-size: 15px; margin: 14px 0 7px;
}
.bubble.md :deep(ul), .bubble.md :deep(ol) { margin: 7px 0; padding-left: 22px; }
.bubble.md :deep(li) { margin: 3px 0; }
.bubble.md :deep(strong) { font-weight: 600; color: #111827; }
.bubble.md :deep(table) {
  border-collapse: collapse; margin: 10px 0; font-size: 13px; width: 100%;
}
.bubble.md :deep(th), .bubble.md :deep(td) {
  border: 1px solid #dfe3ec; padding: 6px 11px; text-align: left;
}
.bubble.md :deep(th) { background: #eef1f8; font-weight: 600; }
.bubble.md :deep(tbody tr:nth-child(even)) { background: #fbfcfe; }
.bubble.md :deep(code) {
  background: #eef0f5; padding: 1px 6px; border-radius: 5px;
  font-size: 13px; font-family: ui-monospace, Consolas, monospace;
}
.bubble.md :deep(pre) {
  background: #1f2937; color: #e5e7eb; padding: 13px; border-radius: 9px;
  overflow-x: auto; margin: 10px 0;
}
.bubble.md :deep(pre code) { background: none; padding: 0; color: inherit; }
.bubble.md :deep(blockquote) {
  margin: 8px 0; padding: 4px 12px; border-left: 3px solid #c7cbd8; color: #4b5563;
}
.bubble.md :deep(a) { color: var(--brand); }
.bubble.md :deep(hr) { border: none; border-top: 1px solid #e5e7eb; margin: 12px 0; }

.pad { padding: 0 24px 8px; }
.composer { display: flex; gap: 10px; padding: 16px 24px; border-top: 1px solid var(--border); }
.composer button { white-space: nowrap; padding: 9px 22px; }
</style>
