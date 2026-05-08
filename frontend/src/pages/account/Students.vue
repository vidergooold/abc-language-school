<template>
  <div class="students-page">
    <div class="page-header">
      <h1>👥 Ученики</h1>
      <div class="header-actions">
        <button v-if="auth.user?.role === 'admin'" @click="showAddForm = !showAddForm" class="btn-add">
          {{ showAddForm ? '✕' : '+' }}
        </button>
        <span class="total-badge">{{ students.length }} чел.</span>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filters">
      <input v-model="search" type="text" placeholder="🔍 Поиск по имени или телефону" />
      <select v-model="filterType">
        <option value="">Все типы</option>
        <option value="child">Школьники</option>
        <option value="adult">Взрослые</option>
        <option value="preschool">Дошкольники</option>
      </select>
      <select v-model="filterStatus">
        <option value="">Все статусы</option>
        <option value="active">Активные</option>
        <option value="inactive">Неактивные</option>
        <option value="graduated">Выпуск</option>
        <option value="expelled">Отчислены</option>
      </select>
    </div>

    <!-- Форма добавления ученика (только для админа) -->
    <div v-if="showAddForm && auth.user?.role === 'admin'" class="add-form">
      <h3>➕ Добавить ученика</h3>
      <form @submit.prevent="addStudent">
        <div class="form-row">
          <label>ФИО *</label>
          <input v-model="newStudent.full_name" required />
        </div>
        <div class="form-row">
          <label>Email</label>
          <input v-model="newStudent.email" type="email" />
        </div>
        <div class="form-row">
          <label>Телефон</label>
          <input v-model="newStudent.phone" />
        </div>
        <div class="form-row">
          <label>Дата рождения</label>
          <input v-model="newStudent.birthdate" type="date" />
        </div>
        <div class="form-row">
          <label>Тип ученика *</label>
          <select v-model="newStudent.student_type" required>
            <option value="">Выберите тип</option>
            <option value="child">Школьник</option>
            <option value="adult">Взрослый</option>
            <option value="preschool">Дошкольник</option>
          </select>
        </div>
        <div class="form-row">
          <label>Статус</label>
          <select v-model="newStudent.status">
            <option value="active">Активен</option>
            <option value="inactive">Не активен</option>
            <option value="graduated">Выпущен</option>
            <option value="expelled">Отчислен</option>
          </select>
        </div>

        <div class="form-row">
          <label>Группа для привязки</label>
          <select v-model.number="newStudent.group_id">
            <option :value="null">Без привязки</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>

        <div class="form-row checkbox-row">
          <label>
            <input v-model="newStudent.create_account" type="checkbox" />
            Создать общий аккаунт родителя/ученика
          </label>
        </div>

        <div v-if="newStudent.create_account" class="form-row">
          <label>Пароль для аккаунта *</label>
          <input v-model="newStudent.password" type="password" minlength="8" required />
        </div>
        <div class="form-actions">
          <button type="submit" :disabled="saving" class="btn-primary">
            {{ saving ? 'Сохранение...' : 'Добавить' }}
          </button>
          <button type="button" @click="cancelAdd" class="btn-secondary">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Форма редактирования ученика (только для админа) -->
    <div v-if="showEditForm && auth.user?.role === 'admin'" class="add-form">
      <h3>✏️ Редактировать ученика</h3>
      <form @submit.prevent="updateStudent">
        <div class="form-row">
          <label>ФИО *</label>
          <input v-model="editStudent.full_name" required />
        </div>
        <div class="form-row">
          <label>Email</label>
          <input v-model="editStudent.email" type="email" />
        </div>
        <div class="form-row">
          <label>Телефон</label>
          <input v-model="editStudent.phone" />
        </div>
        <div class="form-row">
          <label>Дата рождения</label>
          <input v-model="editStudent.birthdate" type="date" />
        </div>
        <div class="form-row">
          <label>Тип ученика *</label>
          <select v-model="editStudent.student_type" required>
            <option value="child">Школьник</option>
            <option value="adult">Взрослый</option>
            <option value="preschool">Дошкольник</option>
          </select>
        </div>
        <div class="form-row">
          <label>Статус</label>
          <select v-model="editStudent.status">
            <option value="active">Активен</option>
            <option value="inactive">Не активен</option>
            <option value="graduated">Выпущен</option>
            <option value="expelled">Отчислен</option>
          </select>
        </div>
        <div class="form-row">
          <label>Группа</label>
          <select v-model.number="editStudentGroupId">
            <option :value="null">Без привязки</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="form-actions">
          <button type="submit" :disabled="saving" class="btn-primary">
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
          <button type="button" @click="cancelEdit" class="btn-secondary">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Скелетон -->
    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-row" v-for="n in 6" :key="n"></div>
    </div>

    <div v-else-if="filtered.length" class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>ФИО</th>
            <th>Группа</th>
            <th>Тип</th>
            <th>Возраст</th>
            <th>Телефон</th>
            <th>Email</th>
            <th>Статус</th>
            <th v-if="auth.user?.role === 'admin'">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filtered" :key="s.id">
            <td class="col-name">{{ s.full_name || '—' }}</td>
            <td>{{ studentNameToGroupId[s.full_name] ? groupName(studentNameToGroupId[s.full_name]!) : '—' }}</td>
            <td><span class="type-badge" :class="'type-' + s.student_type">{{ typeLabel(s.student_type) }}</span></td>
            <td>{{ s.birthdate ? getAge(s.birthdate) + ' л.' : '—' }}</td>
            <td>{{ s.phone || '—' }}</td>
            <td>{{ s.email || '—' }}</td>
            <td><span class="status-badge" :class="'status-' + (s.status || 'active')">{{ statusLabel(s.status) }}</span></td>
            <td v-if="auth.user?.role === 'admin'" class="actions-col">
              <button class="btn-edit" @click="startEdit(s)">Редактировать</button>
              <button class="btn-delete" @click="deleteStudent(s)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">👥</div>
      <p>Ученики не найдены.</p>
      <p class="empty-hint">Они появятся здесь автоматически, когда кто-то заполнит анкету на сайте.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const loading = ref(true)
const students = ref<any[]>([])
const search = ref('')
const filterType = ref('')
const filterStatus = ref('')
const showAddForm = ref(false)
const showEditForm = ref(false)
const saving = ref(false)
const groups = ref<any[]>([])
const editStudentId = ref<number | null>(null)
const newStudent = ref({
  full_name: '',
  email: '',
  phone: '',
  birthdate: '',
  student_type: '',
  status: 'active',
  group_id: null as number | null,
  create_account: true,
  password: 'student123',
})
const editStudent = ref({
  full_name: '',
  email: '',
  phone: '',
  birthdate: '',
  student_type: 'adult',
  status: 'active',
})
const editStudentGroupId = ref<number | null>(null)
const originalGroupId = ref<number | null>(null)
const studentNameToGroupId = ref<Record<string, number>>({})

function groupName(groupId: number): string {
  return groups.value.find(g => g.id === groupId)?.name?.split(' — ')[0] || '—'
}

const filtered = computed(() =>
  students.value
    .filter(s => !search.value ||
      (s.full_name ?? '').toLowerCase().includes(search.value.toLowerCase()) ||
      (s.phone ?? '').includes(search.value) ||
      (s.email ?? '').toLowerCase().includes(search.value.toLowerCase())
    )
    .filter(s => !filterType.value || s.student_type === filterType.value)
    .filter(s => !filterStatus.value || s.status === filterStatus.value)
)

function typeLabel(t: string): string {
  return { child: 'Школьник', adult: 'Взрослый', preschool: 'Дошкольник' }[t] ?? t
}
function getAge(birthdate: string): number {
  const birth = new Date(birthdate)
  const now = new Date()
  let age = now.getFullYear() - birth.getFullYear()
  const monthDiff = now.getMonth() - birth.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birth.getDate())) {
    age--
  }
  return age
}
function statusLabel(s: string): string {
  return {
    active: 'Активен',
    inactive: 'Не активен',
    graduated: 'Выпущен',
    expelled: 'Отчислен',
  }[s] ?? (s || '—')
}

async function load() {
  try {
    const [studentsRes, groupsRes] = await Promise.all([
      http.get('/students'),
      http.get('/groups'),
    ])
    students.value = studentsRes.data
    groups.value = Array.isArray(groupsRes.data) ? groupsRes.data : []

    const nameMap: Record<string, number> = {}
    await Promise.all(
      groups.value.map(async (g) => {
        try {
          const sgRes = await http.get(`/groups/${g.id}/students`)
          for (const sg of sgRes.data) {
            nameMap[sg.student_name] = g.id
          }
        } catch {
          // ignore errors for individual groups
        }
      })
    )
    studentNameToGroupId.value = nameMap
  } catch {
    students.value = []
    groups.value = []
  } finally {
    loading.value = false
  }
}

async function addStudent() {
  if (newStudent.value.create_account && !newStudent.value.password) {
    alert('Укажите пароль для создаваемого аккаунта')
    return
  }

  saving.value = true
  try {
    const payload = {
      full_name: newStudent.value.full_name,
      email: newStudent.value.email || null,
      phone: newStudent.value.phone || null,
      birthdate: newStudent.value.birthdate || null,
      student_type: newStudent.value.student_type,
      status: newStudent.value.status,
    }

    const res = await http.post('/students', payload)
    students.value.push(res.data)

    if (newStudent.value.group_id) {
      await http.post(`/groups/${newStudent.value.group_id}/students`, {
        group_id: newStudent.value.group_id,
        student_name: payload.full_name,
        student_phone: payload.phone,
        student_email: payload.email,
        student_type: payload.student_type,
      })
    }

    if (newStudent.value.create_account && payload.email) {
      await http.post('/admin/users', {
        email: payload.email,
        full_name: payload.full_name,
        password: newStudent.value.password,
        role: 'student',
      })
    }

    // Сброс формы
    newStudent.value = {
      full_name: '',
      email: '',
      phone: '',
      birthdate: '',
      student_type: '',
      status: 'active',
      group_id: null,
      create_account: true,
      password: 'student123',
    }
    showAddForm.value = false
  } catch (err: any) {
    alert('Ошибка: ' + (err.response?.data?.detail || 'Не удалось добавить ученика'))
  } finally {
    saving.value = false
  }
}

function cancelAdd() {
  newStudent.value = {
    full_name: '',
    email: '',
    phone: '',
    birthdate: '',
    student_type: '',
    status: 'active',
    group_id: null,
    create_account: true,
    password: 'student123',
  }
  showAddForm.value = false
}

function startEdit(student: any) {
  editStudentId.value = student.id
  editStudent.value = {
    full_name: student.full_name || '',
    email: student.email || '',
    phone: student.phone || '',
    birthdate: student.birthdate ? String(student.birthdate).slice(0, 10) : '',
    student_type: student.student_type || 'adult',
    status: student.status || 'active',
  }
  editStudentGroupId.value = studentNameToGroupId.value[student.full_name] ?? null
  originalGroupId.value = studentNameToGroupId.value[student.full_name] ?? null
  showEditForm.value = true
  showAddForm.value = false
}

async function updateStudent() {
  if (!editStudentId.value) return
  saving.value = true
  try {
    const payload = {
      full_name: editStudent.value.full_name,
      email: editStudent.value.email || null,
      phone: editStudent.value.phone || null,
      birthdate: editStudent.value.birthdate || null,
      student_type: editStudent.value.student_type,
      status: editStudent.value.status,
    }
    const res = await http.put(`/students/${editStudentId.value}`, payload)
    const idx = students.value.findIndex((s) => s.id === editStudentId.value)
    if (idx !== -1) students.value[idx] = res.data

    // Handle group change
    const newGroupId = editStudentGroupId.value
    const oldGroupId = originalGroupId.value

    // Remove from old group if it existed and is being changed
    if (oldGroupId && oldGroupId !== newGroupId) {
      try {
        await http.delete(`/groups/${oldGroupId}/students/${editStudentId.value}`)
      } catch (err) {
        // Ignore if not in group
      }
    }

    // Add to new group if selected
    if (newGroupId && newGroupId !== oldGroupId) {
      try {
        await http.post(`/groups/${newGroupId}/students`, {
          group_id: newGroupId,
          student_name: editStudent.value.full_name,
          student_phone: editStudent.value.phone,
          student_email: editStudent.value.email,
          student_type: editStudent.value.student_type,
        })
      } catch (err: any) {
        console.error('Error adding student to group:', err)
      }
    }

    cancelEdit()
  } catch (err: any) {
    alert('Ошибка: ' + (err.response?.data?.detail || 'Не удалось обновить ученика'))
  } finally {
    saving.value = false
  }
}

async function deleteStudent(student: any) {
  const ok = window.confirm(`Удалить ученика "${student.full_name}"?`)
  if (!ok) return
  try {
    await http.delete(`/students/${student.id}`)
    students.value = students.value.filter((s) => s.id !== student.id)
    if (editStudentId.value === student.id) {
      cancelEdit()
    }
  } catch (err: any) {
    alert('Ошибка: ' + (err.response?.data?.detail || 'Не удалось удалить ученика'))
  }
}

function cancelEdit() {
  editStudentId.value = null
  editStudent.value = {
    full_name: '',
    email: '',
    phone: '',
    birthdate: '',
    student_type: 'adult',
    status: 'active',
  }
  editStudentGroupId.value = null
  originalGroupId.value = null
  showEditForm.value = false
}

onMounted(load)
</script>

<style scoped>
.students-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.total-badge { background: var(--brand-orange); color: #fff; padding: 4px 14px; border-radius: 999px; font-size: 14px; font-weight: 700; }

.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 160px; outline: none; }
.filters input:focus, .filters select:focus { border-color: var(--brand-orange); }

/* Skeleton */
.skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.skeleton-row { height: 46px; border-radius: 10px; background: linear-gradient(90deg,#fff0e8 25%,#ffe8d6 50%,#fff0e8 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; }
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }

.table-wrap { overflow-x: auto; border-radius: 14px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { background: var(--brand-orange); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #ffe3cf; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #fff7f0; }
.col-id { color: #bbb; font-size: 13px; }
.col-name { font-weight: 600; color: #333; }
.col-date { font-size: 13px; color: #aaa; white-space: nowrap; }

.type-badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }
.type-child     { background: #e8f4ff; color: #2a7bbf; }
.type-adult     { background: #fff0e8; color: var(--brand-orange); }
.type-preschool { background: #f0ffe8; color: #3a9a22; }

.status-badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }
.status-active     { background: #e6f9ef; color: #22a55b; }
.status-inactive   { background: #fdeaea; color: #e03c3c; }
.status-graduated  { background: #fff4cc; color: #b76b00; }
.status-expelled   { background: #ffe3eb; color: #b91c1c; }

.empty-state { text-align: center; padding: 48px; background: #fff7f0; border-radius: 14px; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { font-size: 16px; color: #888; margin-bottom: 6px; }
.empty-hint { font-size: 14px; color: #bbb; }

/* Add form styles */
.btn-add { background: var(--brand-orange); color: #fff; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 20px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-add:hover { background: #e55a00; transform: scale(1.05); }
.add-form { background: #fff7f0; border-radius: 14px; padding: 20px; margin-bottom: 20px; border: 2px solid #ffe3cf; }
.add-form h3 { margin: 0 0 16px 0; color: var(--brand-purple); font-size: 20px; }
.form-row { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.checkbox-row { display: block; }
.checkbox-row label { display: flex; align-items: center; gap: 8px; }
.form-row label { font-weight: 600; color: var(--brand-purple); font-size: 14px; }
.form-row input, .form-row select { padding: 10px 12px; border-radius: 8px; border: 1.5px solid #ffe3cf; font-size: 15px; outline: none; }
.form-row input:focus, .form-row select:focus { border-color: var(--brand-orange); }
.form-actions { display: flex; gap: 12px; margin-top: 20px; }
.btn-primary { background: var(--brand-orange); color: #fff; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-primary:hover:not(:disabled) { background: #e55a00; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #f5f5f5; color: var(--brand-purple); border: 1px solid #ddd; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-secondary:hover { background: #eee; }
.actions-col { white-space: nowrap; }
.btn-edit { background: #f5f0ff; color: var(--brand-purple); border: 1px solid #d8c7ff; padding: 6px 10px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 12px; }
.btn-edit:hover { background: #ece3ff; }
.btn-delete { background: #fdeaea; color: #b91c1c; border: 1px solid #f6b7b7; padding: 6px 10px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 12px; margin-left: 8px; }
.btn-delete:hover { background: #fbd8d8; }
</style>
