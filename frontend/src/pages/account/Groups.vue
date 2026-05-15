<template>
  <div class="groups-page">
    <div class="page-header">
      <h1>📚 Группы</h1>
      <div class="header-actions">
        <button @click="toggleCreateForm" class="btn-add">
          {{ showCreateForm ? '✕' : '+' }}
        </button>
        <span class="total-badge">{{ groups.length }} гр.</span>
      </div>
    </div>

    <!-- Форма создания группы -->
    <div v-if="showCreateForm" class="add-form">
      <h3>➕ Создать группу</h3>
      <form @submit.prevent="createGroup">
        <div class="form-row">
          <label>Название группы *</label>
          <input v-model="newGroup.name" required placeholder="Например: Группа А1 2025" />
        </div>
        <div class="form-row">
          <label>Курс *</label>
          <select v-model.number="newGroup.course_id" required>
            <option value="">— выберите курс —</option>
            <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="form-row">
          <label>Преподаватель</label>
          <select v-model.number="newGroup.teacher_id">
            <option :value="null">— не назначен —</option>
            <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
          </select>
        </div>
        <div class="form-row">
          <label>Дата начала</label>
          <input v-model="newGroup.start_date" type="date" />
        </div>
        <div class="form-row">
          <label>Дата окончания</label>
          <input v-model="newGroup.end_date" type="date" />
        </div>
        <div v-if="createError" class="form-error">{{ createError }}</div>
        <div class="form-actions">
          <button type="submit" :disabled="saving" class="btn-primary">
            {{ saving ? 'Создание...' : 'Создать группу' }}
          </button>
          <button type="button" @click="cancelCreate" class="btn-secondary">Отмена</button>
        </div>
      </form>
    </div>

    <div class="filters">
      <input v-model="search" type="text" placeholder="🔍 Поиск по названию группы" />
    </div>

    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-row" v-for="n in 6" :key="n"></div>
    </div>

    <div v-else-if="filtered.length" class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Курс</th>
            <th>Язык</th>
            <th>Преподаватель</th>
            <th>Статус</th>
            <th>Дата начала</th>
            <th>Дата окончания</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in filtered" :key="g.id">
            <td class="col-name">{{ g.name }}</td>
            <td>{{ g.program_name || '—' }}</td>
            <td>{{ g.language || '—' }}</td>
            <td>{{ teacherName(g.teacher_id) }}</td>
            <td><span class="status-badge" :class="g.status">{{ statusLabel(g.status) }}</span></td>
            <td>{{ formatDate(g.start_date) }}</td>
            <td>{{ formatDate(g.end_date) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">📚</div>
      <p>Группы не найдены.</p>
      <p class="empty-hint">Нажмите «+» чтобы создать первую группу.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

const loading = ref(true)
const groups = ref<any[]>([])
const courses = ref<any[]>([])
const teachers = ref<any[]>([])
const search = ref('')
const showCreateForm = ref(false)
const saving = ref(false)
const createError = ref('')

const newGroup = ref({
  name: '',
  course_id: '' as number | '',
  teacher_id: null as number | null,
  start_date: '',
  end_date: '',
})

const filtered = computed(() =>
  groups.value.filter(g =>
    !search.value ||
    (g.name ?? '').toLowerCase().includes(search.value.toLowerCase())
  )
)

function teacherName(teacherId: number | null) {
  if (!teacherId) return '—'
  const t = teachers.value.find((t: any) => t.id === teacherId)
  return t ? t.full_name : '—'
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    recruiting: 'Набор',
    active: 'Активна',
    completed: 'Завершена',
    suspended: 'Приостановлена',
  }
  return labels[status] || status
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('ru-RU')
}

async function load() {
  try {
    const [groupsRes, coursesRes, teachersRes] = await Promise.all([
      http.get('/groups', { params: { active_only: false } }),
      http.get('/courses'),
      http.get('/teachers'),
    ])
    groups.value = Array.isArray(groupsRes.data) ? groupsRes.data : []
    courses.value = Array.isArray(coursesRes.data) ? coursesRes.data : []
    teachers.value = Array.isArray(teachersRes.data) ? teachersRes.data : []
  } catch {
    groups.value = []
  } finally {
    loading.value = false
  }
}

function toggleCreateForm() {
  showCreateForm.value = !showCreateForm.value
  if (!showCreateForm.value) cancelCreate()
}

function cancelCreate() {
  newGroup.value = { name: '', course_id: '', teacher_id: null, start_date: '', end_date: '' }
  createError.value = ''
  showCreateForm.value = false
}

async function createGroup() {
  if (!newGroup.value.name || !newGroup.value.course_id) return
  saving.value = true
  createError.value = ''
  try {
    const payload: any = {
      name: newGroup.value.name,
      course_id: Number(newGroup.value.course_id),
      teacher_id: newGroup.value.teacher_id || null,
      start_date: newGroup.value.start_date || null,
      end_date: newGroup.value.end_date || null,
    }
    const res = await http.post('/groups', payload)
    groups.value.unshift(res.data)
    cancelCreate()
  } catch (err: any) {
    createError.value = err.response?.data?.detail || 'Не удалось создать группу'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.groups-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.total-badge { background: var(--brand-orange); color: #fff; padding: 4px 14px; border-radius: 999px; font-size: 14px; font-weight: 700; }
.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters input { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 240px; outline: none; }
.filters input:focus { border-color: var(--brand-orange); }
.skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.skeleton-row { height: 46px; border-radius: 10px; background: linear-gradient(90deg,#fff0e8 25%,#ffe8d6 50%,#fff0e8 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; }
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }
.table-wrap { overflow-x: auto; border-radius: 14px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { background: var(--brand-orange); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #ffe3cf; }
.data-table tr:hover td { background: #fff7f0; }
.col-name { font-weight: 600; color: #333; }
.btn-add { background: var(--brand-orange); color: #fff; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 20px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-add:hover { background: #e55a00; transform: scale(1.05); }
.add-form { background: #fff7f0; border-radius: 14px; padding: 20px; margin-bottom: 20px; border: 2px solid #ffe3cf; }
.add-form h3 { margin: 0 0 16px 0; color: var(--brand-purple); font-size: 20px; }
.form-row { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.form-row label { font-weight: 600; color: var(--brand-purple); font-size: 14px; }
.form-row input, .form-row select { padding: 10px 12px; border-radius: 8px; border: 1.5px solid #ffe3cf; font-size: 15px; outline: none; font-family: inherit; }
.form-row input:focus, .form-row select:focus { border-color: var(--brand-orange); }
.form-error { color: #b91c1c; font-size: 14px; margin-bottom: 10px; background: #fdeaea; padding: 8px 12px; border-radius: 8px; }
.form-actions { display: flex; gap: 12px; margin-top: 20px; }
.btn-primary { background: var(--brand-orange); color: #fff; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-primary:hover:not(:disabled) { background: #e55a00; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #f5f5f5; color: var(--brand-purple); border: 1px solid #ddd; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-secondary:hover { background: #eee; }
.empty-state { text-align: center; padding: 48px; background: #fff7f0; border-radius: 14px; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { font-size: 16px; color: #888; margin-bottom: 6px; }
.empty-hint { font-size: 14px; color: #bbb; }

.status-badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status-badge.active { background: #d1fae5; color: #065f46; }
.status-badge.recruiting { background: #dbeafe; color: #1e40af; }
.status-badge.completed { background: #f3f4f6; color: #6b7280; }
.status-badge.suspended { background: #fef3c7; color: #92400e; }
</style>
