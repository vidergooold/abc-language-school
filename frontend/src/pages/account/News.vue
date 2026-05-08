<template>
  <div class="news-admin">
    <h1>📣 Управление новостями</h1>
    <p class="subtitle">Доступно только администратору.</p>

    <button class="btn-add" @click="addNews">+ Добавить новость</button>

    <!-- Форма добавления/редактирования -->
    <div v-if="showForm" class="news-form">
      <h2>{{ editing ? 'Редактировать' : 'Новая новость' }}</h2>
      <div class="field"><label>Заголовок</label><input v-model="form.title" type="text" /></div>
      <div class="field"><label>Тег</label><input v-model="form.tag" type="text" placeholder="Лагерь, Новость и т.п." /></div>
      <div class="field"><label>Текст</label><textarea v-model="form.body" rows="8"></textarea></div>

      <!-- Параметры публикации -->
      <div class="field">
        <label>Публикация</label>
        <div class="publish-options">
          <label class="radio-option">
            <input type="radio" v-model="publishMode" value="now" />
            <span>Опубликовать сейчас</span>
          </label>
          <label class="radio-option">
            <input type="radio" v-model="publishMode" value="scheduled" />
            <span>Запланировать</span>
          </label>
          <label class="radio-option">
            <input type="radio" v-model="publishMode" value="archive" />
            <span>В архив</span>
          </label>
        </div>
      </div>

      <div v-if="publishMode === 'scheduled'" class="field">
        <label>Дата и время публикации</label>
        <input v-model="form.publish_at" type="datetime-local" />
      </div>

      <div class="form-actions">
        <button class="btn-save" @click="saveNews">Сохранить</button>
        <button class="btn-cancel" @click="cancelForm">Отмена</button>
      </div>
    </div>

    <!-- Список новостей -->
    <div v-if="newsList.length === 0" class="news-empty">Новостей пока нет. Добавьте первую!</div>

    <div v-else class="news-list">
      <div v-for="n in newsList" :key="n.id" class="news-card">
        <div class="news-card-header">
          <div class="news-meta">
            <span class="tag">{{ n.tag }}</span>
            <span class="date">{{ n.date }}</span>
            <span class="status-badge" :class="'status-' + n.status">{{ statusLabel(n.status) }}</span>
          </div>
          <div class="news-actions">
            <button @click="editNews(n)">✏️ Ред.</button>
            <button v-if="n.status !== 'published'" @click="publishNews(n.id)" class="btn-publish">✅ Опубл.</button>
            <button v-if="n.status !== 'archived'" @click="archiveNews(n.id)" class="btn-archive">📦 Архив</button>
            <button @click="deleteNews(n.id)" class="btn-del">🗑️ Удал.</button>
          </div>
        </div>
        <h3 class="news-card-title">{{ n.title }}</h3>
        <p v-if="n.publish_at && n.status === 'scheduled'" class="scheduled-info">
          🕐 Запланировано: {{ formatDateTime(n.publish_at) }}
        </p>
        <p class="news-card-preview">{{ getPreview(n.body) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '@/api/http'

const showForm = ref(false)
const editing = ref<number | null>(null)
const publishMode = ref<'now' | 'scheduled' | 'archive'>('now')
const form = ref({ title: '', tag: '', body: '', publish_at: '' })
const newsList = ref<any[]>([])

const STATUS_LABELS: Record<string, string> = {
  draft: 'Черновик',
  review: 'На модерации',
  scheduled: 'Запланировано',
  published: 'Опубликовано',
  archived: 'Архив',
}

function statusLabel(s: string): string {
  return STATUS_LABELS[s] ?? s
}

function formatDateTime(dt: string): string {
  if (!dt) return ''
  return new Date(dt).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' })
}

async function load() {
  try {
    const r = await http.get('/admin/news')
    newsList.value = r.data
  } catch (e) {
    console.error('Error loading news:', e)
  }
}

function addNews() {
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editing.value = null
  publishMode.value = 'now'
  form.value = { title: '', tag: '', body: '', publish_at: '' }
}

function editNews(n: any) {
  editing.value = n.id
  form.value = { title: n.title, tag: n.tag ?? '', body: n.body, publish_at: n.publish_at ? n.publish_at.slice(0, 16) : '' }
  if (n.status === 'scheduled') {
    publishMode.value = 'scheduled'
  } else if (n.status === 'archived') {
    publishMode.value = 'archive'
  } else {
    publishMode.value = 'now'
  }
  showForm.value = true
}

async function saveNews() {
  try {
    let status = 'draft'
    let publish_at: string | null = null

    if (publishMode.value === 'now') {
      status = 'published'
    } else if (publishMode.value === 'scheduled') {
      status = 'scheduled'
      publish_at = form.value.publish_at ? new Date(form.value.publish_at).toISOString() : null
    } else if (publishMode.value === 'archive') {
      status = 'draft'  // will be archived after save
    }

    const payload: any = {
      title: form.value.title,
      tag: form.value.tag || null,
      body: form.value.body,
      status,
      publish_at,
    }

    let savedId: number
    if (editing.value) {
      const res = await http.put(`/admin/news/${editing.value}`, payload)
      savedId = res.data.id
    } else {
      const res = await http.post('/admin/news', payload)
      savedId = res.data.id
    }

    // If archive mode, call archive endpoint after saving
    if (publishMode.value === 'archive') {
      try {
        await http.post(`/admin/news/${savedId}/archive`)
      } catch (archErr: any) {
        console.warn('Archive call failed:', archErr?.response?.data?.detail)
      }
    }

    await load()
    cancelForm()
  } catch (e: any) {
    console.error('Error saving news:', e)
    alert('Ошибка сохранения: ' + (e?.response?.data?.detail || 'неизвестная ошибка'))
  }
}

async function publishNews(id: number) {
  try {
    await http.post(`/admin/news/${id}/publish`)
    await load()
  } catch (e: any) {
    alert('Ошибка публикации: ' + (e.response?.data?.detail || 'неизвестная ошибка'))
  }
}

async function archiveNews(id: number) {
  if (!confirm('Переместить в архив?')) return
  try {
    await http.post(`/admin/news/${id}/archive`)
    await load()
  } catch (e: any) {
    alert('Ошибка архивирования: ' + (e.response?.data?.detail || 'неизвестная ошибка'))
  }
}

async function deleteNews(id: number) {
  if (!confirm('Удалить?')) return
  try {
    await http.delete(`/admin/news/${id}`)
    await load()
  } catch (e) {
    console.error('Error deleting news:', e)
  }
}

function getPreview(html: string): string {
  const text = html.replace(/<[^>]*>/g, '')
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}

onMounted(() => {
  load()
})
</script>



<style scoped>
.news-admin h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 6px;
}
.subtitle {
  font-size: 14px;
  color: #e44;
  margin-bottom: 20px;
  font-weight: 600;
}
.btn-add {
  background: var(--brand-orange);
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 24px;
}
.btn-add:hover {
  background: #e55a10;
}
.news-form {
  background: #fff7f0;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 28px;
}
.news-form h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 16px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}
.field label {
  font-size: 14px;
  font-weight: 600;
}
.field input,
.field textarea {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
  font-family: inherit;
}
.publish-options {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}
.radio-option input[type="radio"] {
  width: 16px;
  height: 16px;
  accent-color: var(--brand-orange);
}
.form-actions {
  display: flex;
  gap: 12px;
}
.btn-save {
  background: var(--brand-orange);
  color: #fff;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.btn-save:hover {
  background: #e55a10;
}
.btn-cancel {
  background: #eee;
  color: #555;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
}
.btn-cancel:hover {
  background: #ddd;
}
.news-empty {
  font-size: 15px;
  color: #888;
  padding: 20px 0;
}
.news-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.news-card {
  background: #fff7f0;
  border-radius: 12px;
  padding: 18px 20px;
  border-left: 4px solid var(--brand-orange);
}
.news-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.news-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.tag {
  background: var(--brand-orange);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
}
.date {
  font-size: 13px;
  color: #888;
}
.status-badge {
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
}
.status-draft      { background: #f0f0f0; color: #666; }
.status-review     { background: #fff3dc; color: #d9860a; }
.status-scheduled  { background: #e8f4ff; color: #2a7bbf; }
.status-published  { background: #e6f9ef; color: #22a55b; }
.status-archived   { background: #fdeaea; color: #e03c3c; }
.news-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.news-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  background: #fff;
  font-weight: 600;
}
.news-actions button:hover {
  background: #f0f0f0;
}
.btn-del {
  background: #ffeaea !important;
  color: #c33;
}
.btn-del:hover {
  background: #ffcccc !important;
}
.btn-publish {
  background: #e6f9ef !important;
  color: #22a55b;
}
.btn-publish:hover {
  background: #c8f5dc !important;
}
.btn-archive {
  background: #fff3dc !important;
  color: #d9860a;
}
.btn-archive:hover {
  background: #ffe8b0 !important;
}
.news-card-title {
  font-size: 17px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px;
}
.scheduled-info {
  font-size: 13px;
  color: #2a7bbf;
  margin: 0 0 6px;
  font-style: italic;
}
.news-card-preview {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin: 0;
}
</style>

