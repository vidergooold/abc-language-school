<template>
  <div class="news-page">
    <div class="news-page-header">
      <h1>📣 Новости</h1>
      <!-- Кнопка «Добавить» — только для staff -->
      <button v-if="auth.isStaff" class="btn-add" @click="addNews">+ Добавить новость</button>
    </div>

    <!-- Форма добавления/редактирования — только для staff -->
    <div v-if="auth.isStaff && showForm" class="news-form">
      <h2>{{ editing ? 'Редактировать новость' : 'Новая новость' }}</h2>

      <div class="field">
        <label>Заголовок *</label>
        <input v-model="form.title" type="text" placeholder="Введите заголовок" />
      </div>

      <div class="field">
        <label>Тег</label>
        <input v-model="form.tag" type="text" placeholder="Лагерь, Акция, Событие..." />
      </div>

      <div class="field">
        <label>Статус публикации</label>
        <select v-model="form.status">
          <option value="draft">Черновик</option>
          <option value="published">Опубликовать сразу</option>
          <option value="scheduled">Запланировать</option>
        </select>
      </div>

      <div v-if="form.status === 'scheduled'" class="field">
        <label>Дата публикации</label>
        <input v-model="form.publish_at" type="datetime-local" />
      </div>

      <div class="field">
        <label>Текст новости *</label>
        <textarea v-model="form.body" rows="8" placeholder="Текст новости..."></textarea>
      </div>

      <p v-if="formError" class="form-error">{{ formError }}</p>

      <div class="form-actions">
        <button class="btn-save" @click="saveNews" :disabled="saving">
          {{ saving ? 'Сохраняю...' : 'Сохранить' }}
        </button>
        <button class="btn-cancel" @click="cancelForm">Отмена</button>
      </div>
    </div>

    <!-- Список новостей -->
    <div v-if="loading" class="news-empty">Загрузка...</div>
    <div v-else-if="newsList.length === 0" class="news-empty">Новостей пока нет.</div>

    <div v-else class="news-list">
      <div v-for="n in newsList" :key="n.id" class="news-card">
        <div class="news-card-header">
          <div class="news-meta">
            <span v-if="n.is_pinned" class="pinned-badge">📌 Закреплено</span>
            <span class="tag" v-if="n.tag">{{ n.tag }}</span>
            <!-- Бейдж статуса — только для staff -->
            <span v-if="auth.isStaff" :class="['status-badge', n.status]">{{ statusLabel(n.status) }}</span>
            <span class="date">{{ n.date }}</span>
          </div>
          <!-- Кнопки управления — только для staff -->
          <div v-if="auth.isStaff" class="news-actions">
            <button v-if="n.status !== 'published'" @click="publishNews(n.id)" class="btn-publish">✅ Опубл.</button>
            <button @click="editNews(n)">✏️ Ред.</button>
            <button @click="deleteNews(n.id)" class="btn-del">🗑️ Удал.</button>
          </div>
        </div>
        <h3 class="news-card-title">{{ n.title }}</h3>
        <p class="news-card-preview">{{ getPreview(n.body) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const showForm = ref(false)
const editing = ref<number | null>(null)
const saving  = ref(false)
const loading = ref(false)
const formError = ref('')

const form = ref({
  title: '',
  tag: '',
  body: '',
  status: 'draft',
  publish_at: null as string | null,
})

const newsList = ref<any[]>([])

async function load() {
  loading.value = true
  try {
    // staff загружает все статусы через /admin/news,
    // обычный пользователь — только опубликованные через /news
    const url = auth.isStaff ? '/admin/news' : '/news'
    const r = await http.get(url)
    // публичный /news возвращает { items: [] }, /admin/news — массив
    newsList.value = Array.isArray(r.data) ? r.data : (r.data.items ?? [])
  } catch (e) {
    console.error('Ошибка загрузки новостей:', e)
  } finally {
    loading.value = false
  }
}

function addNews() {
  editing.value = null
  form.value = { title: '', tag: '', body: '', status: 'draft', publish_at: null }
  formError.value = ''
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editing.value = null
  formError.value = ''
  form.value = { title: '', tag: '', body: '', status: 'draft', publish_at: null }
}

function editNews(n: any) {
  editing.value = n.id
  form.value = {
    title:      n.title,
    tag:        n.tag || '',
    body:       n.body,
    status:     n.status,
    publish_at: n.publish_at || null,
  }
  formError.value = ''
  showForm.value = true
}

async function saveNews() {
  formError.value = ''
  if (!form.value.title.trim()) { formError.value = 'Введите заголовок'; return }
  if (!form.value.body.trim())  { formError.value = 'Введите текст новости'; return }

  saving.value = true
  try {
    const payload: any = {
      title:  form.value.title,
      tag:    form.value.tag,
      body:   form.value.body,
      status: form.value.status,
    }
    if (form.value.publish_at) {
      payload.publish_at = new Date(form.value.publish_at).toISOString()
    }

    if (editing.value) {
      await http.put(`/admin/news/${editing.value}`, payload)
    } else {
      await http.post('/admin/news', payload)
    }
    await load()
    cancelForm()
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    formError.value = typeof detail === 'string' ? detail : 'Ошибка сохранения. Попробуйте снова.'
  } finally {
    saving.value = false
  }
}

async function publishNews(id: number) {
  try {
    await http.post(`/admin/news/${id}/publish`)
    await load()
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    alert(typeof detail === 'string' ? detail : 'Не удалось опубликовать')
  }
}

async function deleteNews(id: number) {
  if (!confirm('Удалить новость?')) return
  try {
    await http.delete(`/admin/news/${id}`)
    await load()
  } catch {
    alert('Ошибка удаления')
  }
}

function getPreview(html: string): string {
  const text = (html || '').replace(/<[^>]*>/g, '')
  return text.length > 150 ? text.substring(0, 150) + '...' : text
}

function statusLabel(s: string): string {
  const map: Record<string, string> = {
    draft:     'Черновик',
    review:    'На проверке',
    scheduled: 'Запланировано',
    published: 'Опубликовано',
    archived:  'Архив',
  }
  return map[s] || s
}

onMounted(() => load())
</script>

<style scoped>
.news-page { max-width: 860px; }

.news-page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.news-page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-purple);
  margin: 0;
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
}
.btn-add:hover { background: #e55a10; }

.news-form {
  background: #fff7f0;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 28px;
  border: 1px solid #ffd5b0;
}
.news-form h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 16px;
}
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.field label { font-size: 14px; font-weight: 600; }
.field input,
.field textarea,
.field select {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
  font-family: inherit;
}
.field select { background: #fff; cursor: pointer; }

.form-error { color: #c33; font-size: 14px; margin-bottom: 10px; font-weight: 600; }
.form-actions { display: flex; gap: 12px; }
.btn-save {
  background: var(--brand-orange); color: #fff; border: none;
  padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer;
}
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-save:not(:disabled):hover { background: #e55a10; }
.btn-cancel {
  background: #eee; color: #555; border: none;
  padding: 10px 24px; border-radius: 8px; cursor: pointer;
}
.btn-cancel:hover { background: #ddd; }

.news-empty { font-size: 15px; color: #888; padding: 20px 0; }
.news-list { display: flex; flex-direction: column; gap: 14px; }

.news-card {
  background: #fff7f0;
  border-radius: 12px;
  padding: 18px 20px;
  border-left: 4px solid var(--brand-orange);
}
.news-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.news-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

.pinned-badge {
  font-size: 12px;
  font-weight: 700;
  color: #7c5a00;
  background: #fff3cd;
  padding: 3px 10px;
  border-radius: 999px;
}
.tag {
  background: var(--brand-orange); color: #fff;
  font-size: 12px; font-weight: 700;
  padding: 3px 10px; border-radius: 999px;
}
.date { font-size: 13px; color: #888; }

.status-badge {
  font-size: 11px; font-weight: 700;
  padding: 3px 9px; border-radius: 999px;
  text-transform: uppercase; letter-spacing: 0.03em;
}
.status-badge.draft     { background: #f0f0f0; color: #666; }
.status-badge.review    { background: #fff3cd; color: #856404; }
.status-badge.scheduled { background: #cfe2ff; color: #084298; }
.status-badge.published { background: #d1e7dd; color: #0a3622; }
.status-badge.archived  { background: #e2e3e5; color: #41464b; }

.news-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.news-actions button {
  padding: 6px 12px; border: none; border-radius: 8px;
  cursor: pointer; font-size: 13px; background: #fff; font-weight: 600;
}
.news-actions button:hover { background: #f0f0f0; }
.btn-publish { background: #d1e7dd !important; color: #0a3622; }
.btn-publish:hover { background: #b8dccb !important; }
.btn-del { background: #ffeaea !important; color: #c33; }
.btn-del:hover { background: #ffcccc !important; }

.news-card-title { font-size: 17px; font-weight: 700; color: #333; margin: 0 0 8px; }
.news-card-preview { font-size: 14px; color: #666; line-height: 1.5; margin: 0; }
</style>
