<template>
  <div class="students-page">
    <div class="page-header">
      <h1>👥 Ученики</h1>
      <button class="btn-add" @click="openAdd">➕ Добавить ученика</button>
    </div>

    <!-- Форма добавления/редактирования -->
    <div v-if="showForm" class="student-form">
      <h2>{{ editingId ? 'Редактировать' : 'Новый ученик' }}</h2>
      <div class="form-grid">
        <div class="field">
          <label>ФИО ученика *</label>
          <input v-model="form.fio" placeholder="Иванов Иван Иванович" />
        </div>
        <div class="field">
          <label>Возраст</label>
          <input v-model="form.age" type="number" placeholder="10" />
        </div>
        <div class="field">
          <label>Класс</label>
          <input v-model="form.grade" placeholder="4" />
        </div>
        <div class="field">
          <label>Школа</label>
          <input v-model="form.school" placeholder="СОШ №6" />
        </div>
        <div class="field">
          <label>Уровень</label>
          <input v-model="form.level" placeholder="AS1" />
        </div>
        <div class="field">
          <label>Телефон родителя</label>
          <input v-model="form.phone" placeholder="+7 (913) 000-00-00" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn-save" @click="saveStudent">Сохранить</button>
        <button class="btn-cancel" @click="cancelForm">Отмена</button>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filters">
      <input v-model="search" type="text" placeholder="Поиск по имени, школе" />
      <select v-model="filterSchool">
        <option value="">Все школы</option>
        <option v-for="s in schools" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="filtered.length" class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>ФИО ученика</th>
            <th>Возраст / класс</th>
            <th>Школа</th>
            <th>Уровень</th>
            <th>Телефон родителя</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filtered" :key="s.id">
            <td>{{ s.id }}</td>
            <td>{{ s.fio }}</td>
            <td>{{ s.age }} л. / {{ s.grade }}кл.</td>
            <td>{{ s.school }}</td>
            <td><span class="level-badge">{{ s.level || '—' }}</span></td>
            <td>{{ s.phone }}</td>
            <td class="actions">
              <button class="btn-icon" @click="editStudent(s)">✏️</button>
              <button class="btn-icon btn-icon--del" @click="deleteStudent(s.id)">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="empty">Ученики не найдены.</p>

    <div class="hint-box">
      <strong>💡 Как добавить ученика?</strong>
      <p>Нажмите «➕ Добавить ученика» вверху страницы — заполните данные вручную.<br/>
      Также ученики появляются автоматически после заполнения анкеты «Запись на занятие» через сайт.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

const loading = ref(true)
const students = ref<any[]>([])
const search = ref('')
const filterSchool = ref('')
const showForm = ref(false)
const editingId = ref<number | null>(null)

const form = ref({ fio: '', age: '', grade: '', school: '', level: '', phone: '' })

const schools = computed(() => [...new Set(students.value.map((s: any) => s.school).filter(Boolean))])
const filtered = computed(() =>
  students.value
    .filter(s => !search.value || s.fio?.toLowerCase().includes(search.value.toLowerCase()) || s.school?.toLowerCase().includes(search.value.toLowerCase()))
    .filter(s => !filterSchool.value || s.school === filterSchool.value)
)

async function load() {
  try {
    const res = await http.get('/admin/students')
    students.value = res.data
  } catch {} finally { loading.value = false }
}

function openAdd() {
  editingId.value = null
  form.value = { fio: '', age: '', grade: '', school: '', level: '', phone: '' }
  showForm.value = true
}

function editStudent(s: any) {
  editingId.value = s.id
  form.value = { fio: s.fio, age: s.age, grade: s.grade, school: s.school, level: s.level, phone: s.phone }
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
}

async function saveStudent() {
  if (!form.value.fio) return alert('Введите ФИО ученика')
  try {
    if (editingId.value) {
      await http.put(`/admin/students/${editingId.value}`, form.value)
    } else {
      await http.post('/admin/students', form.value)
    }
    await load()
    cancelForm()
  } catch { alert('Ошибка сохранения') }
}

async function deleteStudent(id: number) {
  if (!confirm('Удалить ученика?')) return
  try { await http.delete(`/admin/students/${id}`); await load() } catch {}
}

onMounted(load)
</script>

<style scoped>
.students-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.btn-add { background: var(--brand-orange); color: #fff; border: none; padding: 10px 22px; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.btn-add:hover { background: var(--brand-red); }

.student-form { background: #fff7f0; border-radius: 16px; padding: 24px; margin-bottom: 28px; border: 2px solid #ffe3cf; }
.student-form h2 { font-size: 18px; font-weight: 700; color: var(--brand-purple); margin-bottom: 16px; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 16px; }
.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: 13px; font-weight: 600; color: var(--brand-purple); }
.field input { padding: 9px 12px; border-radius: 8px; border: 1.5px solid #e0d5ff; font-size: 14px; outline: none; }
.field input:focus { border-color: var(--brand-orange); }
.form-actions { display: flex; gap: 12px; }
.btn-save { background: var(--brand-orange); color: #fff; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-cancel { background: #eee; color: #555; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; }

.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 180px; }
.table-wrap { overflow-x: auto; border-radius: 14px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { background: var(--brand-orange); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #ffe3cf; }
.data-table tr:hover td { background: #fff7f0; }
.level-badge { background: var(--brand-orange); color: #fff; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.actions { display: flex; gap: 6px; }
.btn-icon { padding: 5px 8px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; background: #f0f0f0; }
.btn-icon--del { background: #ffeaea; }
.empty, .loading { color: #aaa; padding: 24px 0; font-size: 15px; }

.hint-box { margin-top: 28px; background: #f5f0ff; border-radius: 14px; padding: 18px 20px; border-left: 4px solid var(--brand-purple); }
.hint-box strong { font-size: 15px; color: var(--brand-purple); display: block; margin-bottom: 6px; }
.hint-box p { font-size: 14px; color: #555; margin: 0; line-height: 1.5; }
</style>
