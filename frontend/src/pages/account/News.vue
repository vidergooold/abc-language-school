<template>
  <div class="news-admin">
    <h1>📣 Управление новостями</h1>
    <p class="subtitle">Доступно только администратору.</p>

    <button class="btn-add" @click="showForm = true">➕ Добавить новость</button>

    <!-- Форма добавления/редактирования -->
    <div v-if="showForm" class="news-form">
      <h2>{{ editing ? 'Редактировать' : 'Новая новость' }}</h2>
      <div class="field"><label>Заголовок</label><input v-model="form.title" type="text" /></div>
      <div class="field"><label>Тег</label><input v-model="form.tag" type="text" placeholder="Лагерь, Новость и т.⁠п." /></div>
      <div class="field"><label>Текст</label><textarea v-model="form.body" rows="8"></textarea></div>
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
          </div>
          <div class="news-actions">
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

const showForm = ref(false)
const editing = ref<number | null>(null)
const form = ref({ title: '', tag: '', body: '' })
const newsList = ref<any[]>([])

async function load() {
  try {
    const r = await http.get('/admin/news')
    newsList.value = r.data
  } catch {}
}

function cancelForm() {
  showForm.value = false
  editing.value = null
  form.value = { title: '', tag: '', body: '' }
}

function editNews(n: any) {
  editing.value = n.id
  form.value = { title: n.title, tag: n.tag, body: n.body }
  showForm.value = true
}

async function saveNews() {
  try {
    if (editing.value) {
      await http.put(`/admin/news/${editing.value}`, form.value)
    } else {
      await http.post('/admin/news', form.value)
    }
    await load()
    cancelForm()
  } catch {
    alert('Ошибка сохранения')
  }
}

async function deleteNews(id: number) {
  if (!confirm('Удалить?')) return
  try {
    await http.delete(`/admin/news/${id}`)
    await load()
  } catch {}
}

function getPreview(html: string): string {
  // Удаляем HTML-теги и берём первые 100 символов
  const text = html.replace(/<[^>]*>/g, '')
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}

onMounted(load)
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
  align-items: center;
  margin-bottom: 10px;
}
.news-meta {
  display: flex;
  align-items: center;
  gap: 10px;
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
.news-actions {
  display: flex;
  gap: 8px;
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
.news-card-title {
  font-size: 17px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px;
}
.news-card-preview {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin: 0;
}
</style>
