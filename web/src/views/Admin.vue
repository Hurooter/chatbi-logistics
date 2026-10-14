<script setup>
import { computed, onMounted, ref } from 'vue'
import { request } from '../api'

const SCHEMAS = {
  warehouses: {
    label: '仓库',
    idKey: 'warehouse_id',
    path: '/admin/warehouses',
    fields: [
      { key: 'warehouse_id', label: '编号', type: 'number', readonly: true },
      { key: 'warehouse_name', label: '名称', type: 'text' },
      { key: 'city', label: '城市', type: 'text' },
      { key: 'area_sqm', label: '面积(㎡)', type: 'number' },
      { key: 'manager', label: '负责人', type: 'text' },
    ],
  },
  products: {
    label: '商品',
    idKey: 'sku',
    path: '/admin/products',
    fields: [
      { key: 'sku', label: 'SKU', type: 'text', lockOnEdit: true },
      { key: 'product_name', label: '名称', type: 'text' },
      { key: 'category', label: '类目', type: 'text' },
      { key: 'unit_price', label: '单价', type: 'number' },
      { key: 'volume_l', label: '体积(L)', type: 'number' },
      { key: 'weight_kg', label: '重量(kg)', type: 'number' },
    ],
  },
}

const PAGE_SIZE = 15

const tab = ref('warehouses')
const rows = ref([])
const page = ref(1)
const form = ref({})
const editorOpen = ref(false)
const editing = ref(false)
const error = ref('')
const loading = ref(false)

const schema = computed(() => SCHEMAS[tab.value])

const totalPages = computed(() => Math.max(1, Math.ceil(rows.value.length / PAGE_SIZE)))
const pagedRows = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return rows.value.slice(start, start + PAGE_SIZE)
})

function blankForm() {
  const f = {}
  for (const field of schema.value.fields) {
    if (field.readonly) continue
    f[field.key] = field.type === 'number' ? 0 : ''
  }
  return f
}

async function load() {
  error.value = ''
  try {
    rows.value = await request(schema.value.path)
    if (page.value > totalPages.value) page.value = totalPages.value
  } catch (e) {
    error.value = e.message
  }
}

function switchTab(t) {
  tab.value = t
  page.value = 1
  editorOpen.value = false
  load()
}

function startAdd() {
  editing.value = false
  form.value = blankForm()
  editorOpen.value = true
}

function startEdit(row) {
  editing.value = true
  form.value = { ...row }
  editorOpen.value = true
}

function closeEditor() {
  editorOpen.value = false
  form.value = {}
}

async function save() {
  error.value = ''
  loading.value = true
  try {
    if (editing.value) {
      await request(`${schema.value.path}/${form.value[schema.value.idKey]}`, {
        method: 'PUT',
        body: form.value,
      })
    } else {
      await request(schema.value.path, { method: 'POST', body: form.value })
    }
    closeEditor()
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function remove(row) {
  if (!confirm(`确定删除「${row[schema.value.idKey]}」？`)) return
  error.value = ''
  try {
    await request(`${schema.value.path}/${row[schema.value.idKey]}`, { method: 'DELETE' })
    await load()
  } catch (e) {
    error.value = e.message
  }
}

onMounted(load)
</script>

<template>
  <div class="admin">
    <header class="head">
      <div>
        <h1>数据管理</h1>
        <p class="muted">仓库与商品主数据的增删改查</p>
      </div>
      <div class="tabs">
        <button
          v-for="(s, key) in SCHEMAS"
          :key="key"
          :class="{ ghost: tab !== key }"
          @click="switchTab(key)"
        >{{ s.label }}</button>
      </div>
    </header>

    <p v-if="error" class="error banner">{{ error }}</p>

    <section class="card table-card">
      <div class="table-head">
        <span class="count">共 {{ rows.length }} 条 · 第 {{ page }} / {{ totalPages }} 页</span>
        <button class="small" @click="startAdd">＋ 新增{{ schema.label }}</button>
      </div>

      <table>
        <thead>
          <tr>
            <th v-for="f in schema.fields" :key="f.key">{{ f.label }}</th>
            <th class="ops-col">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in pagedRows" :key="row[schema.idKey]">
            <td v-for="f in schema.fields" :key="f.key">{{ row[f.key] }}</td>
            <td class="ops">
              <button class="ghost small" @click="startEdit(row)">编辑</button>
              <button class="danger small" @click="remove(row)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pager">
        <button class="ghost small" :disabled="page <= 1" @click="page--">上一页</button>
        <span class="muted">{{ page }} / {{ totalPages }}</span>
        <button class="ghost small" :disabled="page >= totalPages" @click="page++">下一页</button>
      </div>
    </section>

    <!-- 弹窗编辑器 -->
    <div v-if="editorOpen" class="mask" @click.self="closeEditor">
      <div class="modal card">
        <h2>{{ editing ? '编辑' : '新增' }}{{ schema.label }}</h2>
        <div class="grid">
          <label v-for="f in schema.fields" :key="f.key" class="field">
            <span>{{ f.label }}</span>
            <input
              v-model="form[f.key]"
              :type="f.type === 'number' ? 'number' : 'text'"
              :disabled="editing && (f.readonly || f.lockOnEdit)"
            />
          </label>
        </div>
        <div class="actions">
          <button :disabled="loading" @click="save">{{ loading ? '保存中…' : '保存' }}</button>
          <button class="ghost" @click="closeEditor">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin { max-width: 1180px; margin: 0 auto; }

.head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 20px; gap: 20px; flex-wrap: wrap; }
.head h1 { margin: 0 0 4px; font-size: 24px; }
.tabs { display: flex; gap: 8px; }

.banner { background: #fef2f2; border: 1px solid #fbd5d5; padding: 10px 14px; border-radius: 10px; margin-bottom: 16px; }

.table-card { overflow: hidden; }
.table-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid var(--border);
}
.count { font-size: 13px; color: var(--muted); }

table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { text-align: left; padding: 11px 20px; }
thead th {
  background: #fafbfd; color: var(--muted); font-weight: 500;
  font-size: 13px; border-bottom: 1px solid var(--border);
}
tbody tr { border-bottom: 1px solid #f3f4f7; transition: background .12s; }
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: #fafbff; }
.ops-col { width: 140px; }
.ops { display: flex; gap: 8px; }

.pager {
  display: flex; align-items: center; justify-content: center; gap: 14px;
  padding: 14px; border-top: 1px solid var(--border); background: #fafbfd;
}

.mask {
  position: fixed; inset: 0; background: rgba(17, 24, 39, .45);
  display: flex; align-items: center; justify-content: center;
  padding: 24px; z-index: 50; backdrop-filter: blur(2px);
}
.modal { width: 100%; max-width: 620px; padding: 28px; box-shadow: var(--shadow-lg); }
.modal h2 { margin: 0 0 20px; font-size: 18px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
.field span { display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; }
.actions { margin-top: 24px; display: flex; gap: 10px; }
</style>
