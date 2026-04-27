<template>
  <div class="teachers-page">
    <div class="page-header">
      <h1>👩‍🏫 Преподаватели</h1>
      <div class="header-actions">
        <button v-if="auth.user?.role === 'admin'" @click="showAddForm = !showAddForm" class="btn-add">
          {{ showAddForm ? '✕' : '+' }}
        </button>
        <span class="total-badge">{{ teachers.length }} чел.</span>
      </div>
    </div>

    <div class="filters">
      <input v-model="search" type="text" placeholder="🔍 Поиск по имени, email или предмету" />
    </div>

    <!-- Форма добавления преподавателя (только для админа) -->
    <div v-if="showAddForm && auth.user?.role === 'admin'" class="add-form">
      <h3>➕ Добавить преподавателя</h3>
      <form @submit.prevent="addTeacher">
        <div class="form-row">
          <label>ФИО *</label>
          <input v-model="newTeacher.full_name" required />
        </div>
        <div class="form-row">
          <label>Email *</label>
          <input v-model="newTeacher.email" type="email" required />
        </div>
        <div class="form-row">
          <label>Телефон</label>
          <input v-model="newTeacher.phone" />
        </div>
        <div class="form-row">
          <label>Предмет</label>
          <input v-model="newTeacher.subject" placeholder="Английский язык" />
        </div>
        <div class="form-row">
          <label>Уровень языка</label>
          <input v-model="newTeacher.language_level" placeholder="C1" />
        </div>
        <div class="form-row">
          <label>Опыт (лет)</label>
          <input v-model.number="newTeacher.experience_years" type="number" min="0" />
        </div>
        <div class="form-row">
          <label>Биография</label>
          <textarea v-model="newTeacher.bio" rows="3"></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" :disabled="saving" class="btn-primary">
            {{ saving ? 'Сохранение...' : 'Добавить' }}
          </button>
          <button type="button" @click="cancelAdd" class="btn-secondary">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Форма редактирования преподавателя (только для админа) -->
    <div v-if="showEditForm && auth.user?.role === 'admin'" class="add-form">
      <h3>✏️ Редактировать преподавателя</h3>
      <form @submit.prevent="updateTeacher">
        <div class="form-row">
          <label>ФИО *</label>
          <input v-model="editTeacher.full_name" required />
        </div>
        <div class="form-row">
          <label>Email *</label>
          <input v-model="editTeacher.email" type="email" required />
        </div>
        <div class="form-row">
          <label>Телефон</label>
          <input v-model="editTeacher.phone" />
        </div>
        <div class="form-row">
          <label>Предмет</label>
          <input v-model="editTeacher.subject" placeholder="Английский язык" />
        </div>
        <div class="form-row">
          <label>Уровень языка</label>
          <input v-model="editTeacher.language_level" placeholder="C1" />
        </div>
        <div class="form-row">
          <label>Опыт (лет)</label>
          <input v-model.number="editTeacher.experience_years" type="number" min="0" />
        </div>
        <div class="form-row">
          <label>Биография</label>
          <textarea v-model="editTeacher.bio" rows="3"></textarea>
        </div>
        <div class="form-row checkbox-row">
          <label>
            <input v-model="editTeacher.is_active" type="checkbox" />
            Активный преподаватель
          </label>
        </div>
        <div class="form-actions">
          <button type="submit" :disabled="saving" class="btn-primary">
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
          <button type="button" @click="cancelEdit" class="btn-secondary">Отмена</button>
        </div>
      </form>

      <!-- Секция управления группами преподавателя -->
      <div v-if="editTeacherId" class="groups-section">
        <h4>📚 Группы преподавателя</h4>
        <div v-if="teacherGroupsLoading" class="groups-loading">Загрузка групп...</div>
        <div v-else>
          <div v-if="teacherGroups.length === 0" class="groups-empty">Нет назначенных групп</div>
          <ul v-else class="groups-list">
            <li v-for="tg in teacherGroups" :key="tg.id" class="group-item">
              <span class="group-name">{{ tg.group_name }}</span>
              <span v-if="tg.course_name" class="group-course">{{ tg.course_name }}</span>
              <button class="btn-remove-group" @click="removeTeacherGroup(tg.group_id)" title="Убрать из группы">×</button>
            </li>
          </ul>
          <div class="add-group-row">
            <select v-model.number="newGroupId" class="group-select">
              <option value="">— выбрать группу —</option>
              <option
                v-for="g in availableGroups"
                :key="g.id"
                :value="g.id"
              >{{ g.name }}</option>
            </select>
            <button class="btn-add-group" @click="addTeacherGroup" :disabled="!newGroupId">+ Добавить</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-row" v-for="n in 6" :key="n"></div>
    </div>

    <div v-else-if="filtered.length" class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>ФИО</th>
            <th>Предмет</th>
            <th>Уровень</th>
            <th>Опыт</th>
            <th>Телефон</th>
            <th>Email</th>
            <th v-if="auth.user?.role === 'admin'">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filtered" :key="t.id">
            <td class="col-id">{{ t.id }}</td>
            <td class="col-name">{{ t.full_name || '—' }}</td>
            <td>{{ t.subject || '—' }}</td>
            <td>{{ t.language_level || '—' }}</td>
            <td>{{ t.experience_years }} лет</td>
            <td>{{ t.phone || '—' }}</td>
            <td>{{ t.email || '—' }}</td>
            <td v-if="auth.user?.role === 'admin'" class="actions-col">
              <button class="btn-edit" @click="startEdit(t)">Редактировать</button>
              <button class="btn-delete" @click="deleteTeacher(t)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">👩‍🏫</div>
      <p>Преподаватели не найдены.</p>
      <p class="empty-hint">Проверьте, что преподаватели добавлены в базу данных.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const loading = ref(true)
const teachers = ref<any[]>([])
const search = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const saving = ref(false)
const editTeacherId = ref<number | null>(null)

// Groups section
const teacherGroups = ref<any[]>([])
const teacherGroupsLoading = ref(false)
const allGroups = ref<any[]>([])
const newGroupId = ref<number | ''>('')

const newTeacher = ref({
  full_name: '',
  email: '',
  phone: '',
  subject: '',
  language_level: '',
  experience_years: 0,
  bio: '',
})
const editTeacher = ref({
  full_name: '',
  email: '',
  phone: '',
  subject: '',
  language_level: '',
  experience_years: 0,
  bio: '',
  is_active: true,
})

const filtered = computed(() =>
  teachers.value.filter(t =>
    !search.value ||
    (t.full_name ?? '').toLowerCase().includes(search.value.toLowerCase()) ||
    (t.email ?? '').toLowerCase().includes(search.value.toLowerCase()) ||
    (t.subject ?? '').toLowerCase().includes(search.value.toLowerCase())
  )
)

// Groups already assigned to this teacher
const availableGroups = computed(() => {
  const assignedIds = new Set(teacherGroups.value.map((tg: any) => tg.group_id))
  return allGroups.value.filter((g: any) => !assignedIds.has(g.id))
})

async function load() {
  try {
    const url = auth.user?.role === 'admin' ? '/teachers/all' : '/teachers'
    const res = await http.get(url)
    teachers.value = res.data
  } catch {
    teachers.value = []
  } finally {
    loading.value = false
  }
}

async function loadTeacherGroups(teacherId: number) {
  teacherGroupsLoading.value = true
  try {
    const res = await http.get(`/teachers/${teacherId}/groups`)
    teacherGroups.value = res.data
  } catch {
    teacherGroups.value = []
  } finally {
    teacherGroupsLoading.value = false
  }
}

async function loadAllGroups() {
  try {
    const res = await http.get('/groups')
    allGroups.value = Array.isArray(res.data) ? res.data : []
  } catch {
    allGroups.value = []
  }
}

async function addTeacher() {
  saving.value = true
  try {
    const res = await http.post('/teachers', newTeacher.value)
    teachers.value.push(res.data)
    newTeacher.value = {
      full_name: '',
      email: '',
      phone: '',
      subject: '',
      language_level: '',
      experience_years: 0,
      bio: '',
    }
    showAddForm.value = false
  } catch (err: any) {
    alert('Ошибка: ' + (err.response?.data?.detail || 'Не удалось добавить преподавателя'))
  } finally {
    saving.value = false
  }
}

function startEdit(teacher: any) {
  editTeacherId.value = teacher.id
  editTeacher.value = {
    full_name: teacher.full_name || '',
    email: teacher.email || '',
    phone: teacher.phone || '',
    subject: teacher.subject || '',
    language_level: teacher.language_level || '',
    experience_years: teacher.experience_years ?? 0,
    bio: teacher.bio || '',
    is_active: teacher.is_active !== false,
  }
  showEditForm.value = true
  showAddForm.value = false
  newGroupId.value = ''
  loadTeacherGroups(teacher.id)
  loadAllGroups()
}

async function updateTeacher() {
  if (!editTeacherId.value) return
  saving.value = true
  try {
    const payload = {
      full_name: editTeacher.value.full_name,
      email: editTeacher.value.email,
      phone: editTeacher.value.phone || null,
      subject: editTeacher.value.subject || null,
      language_level: editTeacher.value.language_level || null,
      experience_years: Number(editTeacher.value.experience_years) || 0,
      bio: editTeacher.value.bio || null,
      is_active: !!editTeacher.value.is_active,
    }
    const res = await http.put(`/teachers/${editTeacherId.value}`, payload)
    const idx = teachers.value.findIndex((t) => t.id === editTeacherId.value)
    if (idx !== -1) teachers.value[idx] = res.data
    cancelEdit()
  } catch (err: any) {
    alert('Ошибка: ' + (err.response?.data?.detail || 'Не удалось обновить преподавателя'))
  } finally {
    saving.value = false
  }
}

async function addTeacherGroup() {
  if (!editTeacherId.value || !newGroupId.value) return
  try {
    const res = await http.post(`/teachers/${editTeacherId.value}/groups`, { group_id: newGroupId.value })
    teacherGroups.value.push(res.data)
    newGroupId.value = ''
  } catch (err: any) {
    alert('Ошибка: ' + (err.response?.data?.detail || 'Не удалось добавить группу'))
  }
}

async function removeTeacherGroup(groupId: number) {
  if (!editTeacherId.value) return
  if (!confirm('Убрать преподавателя из этой группы?')) return
  try {
    await http.delete(`/teachers/${editTeacherId.value}/groups/${groupId}`)
    teacherGroups.value = teacherGroups.value.filter((tg: any) => tg.group_id !== groupId)
  } catch (err: any) {
    alert('Ошибка: ' + (err.response?.data?.detail || 'Не удалось убрать группу'))
  }
}

async function deleteTeacher(teacher: any) {
  const ok = window.confirm(`Удалить преподавателя "${teacher.full_name}"?`)
  if (!ok) return
  try {
    await http.delete(`/teachers/${teacher.id}`)
    teachers.value = teachers.value.filter((t) => t.id !== teacher.id)
    if (editTeacherId.value === teacher.id) cancelEdit()
  } catch (err: any) {
    alert('Ошибка: ' + (err.response?.data?.detail || 'Не удалось удалить преподавателя'))
  }
}

function cancelAdd() {
  newTeacher.value = {
    full_name: '',
    email: '',
    phone: '',
    subject: '',
    language_level: '',
    experience_years: 0,
    bio: '',
  }
  showAddForm.value = false
}

function cancelEdit() {
  editTeacherId.value = null
  editTeacher.value = {
    full_name: '',
    email: '',
    phone: '',
    subject: '',
    language_level: '',
    experience_years: 0,
    bio: '',
    is_active: true,
  }
  teacherGroups.value = []
  newGroupId.value = ''
  showEditForm.value = false
}

onMounted(load)
</script>

<style scoped>
.teachers-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); }
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
.btn-add { background: var(--brand-orange); color: #fff; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 20px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-add:hover { background: #e55a00; transform: scale(1.05); }
.add-form { background: #fff7f0; border-radius: 14px; padding: 20px; margin-bottom: 20px; border: 2px solid #ffe3cf; }
.add-form h3 { margin: 0 0 16px 0; color: var(--brand-purple); font-size: 20px; }
.form-row { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.checkbox-row { display: block; }
.checkbox-row label { display: flex; align-items: center; gap: 8px; }
.form-row label { font-weight: 600; color: var(--brand-purple); font-size: 14px; }
.form-row input, .form-row textarea { padding: 10px 12px; border-radius: 8px; border: 1.5px solid #ffe3cf; font-size: 15px; outline: none; }
.form-row input:focus, .form-row textarea:focus { border-color: var(--brand-orange); }
.form-actions { display: flex; gap: 12px; margin-top: 20px; }
.btn-primary { background: var(--brand-orange); color: #fff; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-primary:hover:not(:disabled) { background: #e55a00; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #f5f5f5; color: var(--brand-purple); border: 1px solid #ddd; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-secondary:hover { background: #eee; }

.actions-col { white-space: nowrap; }
.btn-edit { background: #f5f0ff; color: var(--brand-purple); border: 1px solid #d8c7ff; padding: 6px 10px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 12px; margin-right: 8px; }
.btn-edit:hover { background: #ece3ff; }
.btn-delete { background: #fdeaea; color: #b91c1c; border: 1px solid #f6b7b7; padding: 6px 10px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 12px; }
.btn-delete:hover { background: #fbd8d8; }

.col-name { font-weight: 600; color: #333; }
.empty-state { text-align: center; padding: 48px; background: #fff7f0; border-radius: 14px; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { font-size: 16px; color: #888; margin-bottom: 6px; }
.empty-hint { font-size: 14px; color: #bbb; }

/* Groups section */
.groups-section { margin-top: 24px; padding-top: 20px; border-top: 2px solid #ffe3cf; }
.groups-section h4 { font-size: 16px; font-weight: 700; color: var(--brand-purple); margin: 0 0 12px; }
.groups-loading { font-size: 14px; color: #888; }
.groups-empty { font-size: 14px; color: #aaa; margin-bottom: 12px; }
.groups-list { list-style: none; padding: 0; margin: 0 0 12px; display: flex; flex-direction: column; gap: 6px; }
.group-item { display: flex; align-items: center; gap: 8px; background: #fff; border-radius: 8px; padding: 8px 12px; border: 1px solid #ffe3cf; }
.group-name { font-weight: 600; font-size: 14px; color: #333; flex: 1; }
.group-course { font-size: 12px; color: #888; }
.btn-remove-group { background: #fdeaea; color: #b91c1c; border: 1px solid #f6b7b7; border-radius: 6px; width: 24px; height: 24px; font-size: 16px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; padding: 0; line-height: 1; }
.btn-remove-group:hover { background: #fbd8d8; }
.add-group-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.group-select { padding: 8px 12px; border-radius: 8px; border: 1.5px solid #ffe3cf; font-size: 14px; outline: none; min-width: 200px; }
.group-select:focus { border-color: var(--brand-orange); }
.btn-add-group { background: var(--brand-orange); color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px; }
.btn-add-group:hover:not(:disabled) { background: #e55a00; }
.btn-add-group:disabled { opacity: 0.5; cursor: not-allowed; }
</style>

