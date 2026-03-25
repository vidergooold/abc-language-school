<template>
  <div class="news-admin">
    <h1>📣 Управление новостями</h1>
    <p class="subtitle">Доступно только администратору.</p>

    <button class="btn-add" @click="addNews">+ Добавить новость</button>
        <!-- Форма добавления/редактирования --><div v-if="showForm" class="news-form">
      <h2>{{ editing ? 'Редактировать' : 'Новая новость' }}</h2>
      <div class="field"><label>Заголовок</label><input v-model="form.title" type="text" /></div>
      <div class="field"><label>Тег</label><input v-model="form.tag" type="text" placeholder="Лагерь, Новость и т.⁠п." /></div>
                <div class="field"><label>Дата</label><input v-model="form.date" type="date" /></div>
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
const form = ref({ title: '', tag: '', date: '', body: '' })
  const newsList = ref<any[]>([])
async function load() {
  try {
    const r = await http.get('/admin/news')
    newsList.value = r.data
  } catch {}
}

  function addNews() {
        showForm.value = true
      }
  
