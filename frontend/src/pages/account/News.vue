<template>
  <div class="news-admin">
    <h1>📣 Управление новостями</h1>
    <p class="subtitle">Доступно только администратору.</p>

    <button class="btn-add" @click="showForm = true">➕ Добавить новость</button>

    <div v-if="showForm" class="news-form">
      <h2>{{ editing ? 'Редактировать' : 'Новая новость' }}</h2>
      <div class="field"><label>Заголовок</label><input v-model="form.title" type="text" /></div>
      <div class="field"><label>Тег</label><input v-model="form.tag" type="text" placeholder="Лагерь, Новость и т.&NoBreak;п." /></div>
      <div class="field"><label>Текст</label><textarea v-model="form.body" rows="6"></textarea></div>
      <div class="form-actions">
        <button class="btn-save" @click="saveNews">Сохранить</button>
        <button class="btn-cancel" @click="cancelForm">Отмена</button>
      </div>
    </div>

    <div class="news-list">
      <div class="news-row" v-for="n in newsList" :key="n.id">
        <div>
          <strong>{{ n.title }}</strong>
          <span class="tag">{{ n.tag }}</span>
          <span class="date">{{ n.date }}</span>
        </div>
        <div class="news-actions">
          <button @click="editNews(n)">✏️</button>
          <button @click="deleteNews(n.id)" class="btn-del">🗑️</button>
        </div>
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
  try { const r = await http.get('/admin/news'); newsList.value = r.data } catch {}
}

function cancelForm() { showForm.value = false; editing.value = null; form.value = { title: '', tag: '', body: '' } }

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
  } catch { alert('Ошибка сохранения') }
}

async function deleteNews(id: number) {
  if (!confirm('Удалить?')) return
  try { await http.delete(`/admin/news/${id}`); await load() } catch {}
}

onMounted(load)
</script>

<style scoped>
.news-admin h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 6px; }
.subtitle { font-size: 14px; color: #e44; margin-bottom: 20px; font-weight: 600; }
.btn-add { background: var(--brand-orange); color: #fff; border: none; padding: 10px 22px; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; margin-bottom: 24px; }
.news-form { background: #fff7f0; border-radius: 16px; padding: 20px; margin-bottom: 28px; }
.news-form h2 { font-size: 18px; font-weight: 700; color: var(--brand-purple); margin-bottom: 14px; }
.field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 14px; }
.field label { font-size: 14px; font-weight: 600; }
.field input, .field textarea { padding: 10px; border-radius: 8px; border: 1px solid #ddd; font-size: 14px; }
.form-actions { display: flex; gap: 12px; }
.btn-save { background: var(--brand-orange); color: #fff; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-cancel { background: #eee; color: #555; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; }
.news-list { display: flex; flex-direction: column; gap: 12px; }
.news-row { display: flex; justify-content: space-between; align-items: center; background: #fff7f0; border-radius: 12px; padding: 14px 18px; }
.news-row strong { font-size: 15px; color: #333; margin-right: 10px; }
.tag { background: var(--brand-orange); color: #fff; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 999px; margin-right: 8px; }
.date { font-size: 12px; color: #aaa; }
.news-actions { display: flex; gap: 8px; }
.news-actions button { padding: 5px 10px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; background: #eee; }
.btn-del { background: #ffeaea !important; }
</style>
