<template>
  <div class="profile-page">
    <h1>👤 Профиль</h1>

    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-field" v-for="n in 4" :key="n"></div>
    </div>

    <div v-else class="profile-wrap">
      <!-- Аватар -->
      <div class="avatar-block">
        <div class="avatar">
          {{ initials }}
        </div>
        <div class="avatar-info">
          <div class="avatar-name">{{ auth.user?.full_name || auth.user?.email }}</div>
          <span class="role-badge" :class="'role-' + auth.user?.role">
            {{ roleLabel }}
          </span>
        </div>
      </div>

      <div v-if="auth.user?.role === 'admin'" class="admin-note">
        <strong>Важно:</strong> при регистрации сотрудника его аккаунт создаётся со статусом «ученик». Администратор вручную назначит роль после проверки.
      </div>

      <div v-if="auth.isStudent && studentProfile" class="student-card">
        <h2>Данные ученика</h2>
        <div class="student-grid">
          <div><strong>ФИО:</strong> {{ studentProfile.full_name || '—' }}</div>
          <div><strong>Телефон:</strong> {{ studentProfile.phone || '—' }}</div>
          <div><strong>Email:</strong> {{ studentProfile.email || auth.user?.email || '—' }}</div>
          <div><strong>Дата рождения:</strong> {{ studentProfile.birthdate ? String(studentProfile.birthdate).slice(0, 10) : '—' }}</div>
          <div><strong>Статус:</strong> {{ studentStatusLabel(studentProfile.status) }}</div>
          <div><strong>Тип:</strong> {{ studentTypeLabel(studentProfile.student_type) }}</div>
          <div><strong>Группа:</strong> {{ studentGroup?.name || 'Ожидает распределения' }}</div>
        </div>

        <h3 class="grades-title">Оценки</h3>
        <div class="grades-summary">
          <span>Средний за месяц: <strong>{{ gradeAverages.month }}</strong></span>
          <span>Средний за учебный год: <strong>{{ gradeAverages.academic_year }}</strong></span>
        </div>
        <div v-if="myGradeRows.length" class="grades-list">
          <div v-for="item in myGradeRows" :key="item.key" class="grade-row">
            <span class="grade-date">{{ item.date }}</span>
            <span v-if="item.group" class="grade-group">{{ item.group }}</span>
            <strong class="grade-value">{{ item.grade }}</strong>
          </div>
        </div>
        <p v-else class="field-hint">Оценок пока нет.</p>
      </div>

      <!-- Форма -->
      <div class="profile-form">
        <div class="form-section">
          <h2>Личные данные</h2>
          <div class="form-grid">
            <div class="field">
              <label>Полное имя</label>
              <input v-model="form.full_name" placeholder="Иванов Иван Иванович" :disabled="saving" />
            </div>
            <div class="field">
              <label>Email</label>
              <input :value="auth.user?.email" disabled placeholder="email@example.com" />
              <span class="field-hint">Email изменить нельзя — это ваш логин</span>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h2>Смена пароля</h2>
          <div class="form-grid">
            <div class="field">
              <label>Новый пароль</label>
              <input v-model="form.new_password" type="password" placeholder="Минимум 8 символов" :disabled="saving" />
            </div>
            <div class="field">
              <label>Повторите пароль</label>
              <input v-model="form.confirm_password" type="password" placeholder="Повторите пароль" :disabled="saving" />
              <span v-if="passwordMismatch" class="field-error">Пароли не совпадают</span>
            </div>
          </div>
        </div>

        <div v-if="successMsg" class="alert-success">✅ {{ successMsg }}</div>
        <div v-if="errorMsg" class="alert-error">❌ {{ errorMsg }}</div>

        <div class="form-actions">
          <button class="btn-save" :disabled="saving || passwordMismatch" @click="save">
            {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import http from '@/api/http'

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')
const studentProfile = ref<any | null>(null)
const studentGroup = ref<any | null>(null)
const myGradeRows = ref<Array<{ key: string; date: string; grade: string; slot_date: string; group: string }>>([])
const gradeAverages = ref({ month: '—', academic_year: '—' })

const form = ref({
  full_name: '',
  new_password: '',
  confirm_password: '',
})

const initials = computed(() => {
  const name = auth.user?.full_name || auth.user?.email || '?'
  return name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
})

const roleLabel = computed(() => {
  const r = auth.user?.role
  return r ? { admin: '🔑 Администратор', teacher: '👨‍🏫 Учитель', student: '🎓 Студент' }[r] ?? r : '—'
})

const passwordMismatch = computed(() =>
  !!form.value.confirm_password && form.value.new_password !== form.value.confirm_password
)

onMounted(() => {
  form.value.full_name = auth.user?.full_name || ''
  if (auth.isStudent) {
    loadStudentProfile()
    loadMyGrades()
  }
})

function studentStatusLabel(status: string) {
  return {
    waiting: 'Ожидает',
    active: 'Активный',
    inactive: 'Архивный',
    graduated: 'Выпущен',
    expelled: 'Отчислен',
  }[status] || status || '—'
}

function studentTypeLabel(type: string) {
  return {
    child: 'Школьник',
    adult: 'Взрослый',
    preschool: 'Дошкольник',
  }[type] || type || '—'
}

function lessonDateLabel(slotDate: string) {
  if (!slotDate) return '—'
  return new Date(`${slotDate}T00:00:00`).toLocaleDateString('ru-RU')
}

function formatAverage(value: number | null | undefined) {
  if (value == null) return '—'
  return Number(value).toFixed(2)
}

async function loadStudentProfile() {
  try {
    const res = await http.get('/students/me')
    studentProfile.value = res.data?.student || null
    studentGroup.value = res.data?.group || null
  } catch {
    studentProfile.value = null
    studentGroup.value = null
  }
}

async function loadMyGrades() {
  try {
    const res = await http.get('/progress/my')
    const lessons = Array.isArray(res.data?.lessons) ? res.data.lessons : []
    const records = res.data?.records || {}
    const groupName: string = res.data?.group?.name || ''
    const rows: Array<{ key: string; date: string; grade: string; slot_date: string; group: string }> = []
    for (const lesson of lessons) {
      const record = records[`${res.data?.student?.id}:${lesson.id}:${lesson.slot_date}`]
      if (!record || record.grade == null) continue
      rows.push({
        key: `${lesson.id}:${lesson.slot_date}`,
        date: lessonDateLabel(lesson.slot_date),
        grade: String(record.grade),
        slot_date: lesson.slot_date,
        group: groupName,
      })
    }
    myGradeRows.value = rows.sort((a, b) => (a.slot_date < b.slot_date ? 1 : a.slot_date > b.slot_date ? -1 : 0))
    gradeAverages.value = {
      month: formatAverage(res.data?.averages?.month),
      academic_year: formatAverage(res.data?.averages?.academic_year),
    }
  } catch {
    myGradeRows.value = []
    gradeAverages.value = { month: '—', academic_year: '—' }
  }
}

async function save() {
  if (passwordMismatch.value) return
  saving.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    const payload: any = { full_name: form.value.full_name }
    if (form.value.new_password) {
      payload.password = form.value.new_password
    }
    await http.patch('/users/me', payload)
    auth.user!.full_name = form.value.full_name
    form.value.new_password = ''
    form.value.confirm_password = ''
    successMsg.value = 'Данные успешно обновлены!'
    setTimeout(() => successMsg.value = '', 4000)
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || 'Ошибка при сохранении'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.profile-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 28px; }

/* Skeleton */
.skeleton-list { display: flex; flex-direction: column; gap: 14px; }
.skeleton-field { height: 52px; border-radius: 10px; background: linear-gradient(90deg,#fff0e8 25%,#ffe8d6 50%,#fff0e8 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; }
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }

.profile-wrap { display: flex; flex-direction: column; gap: 28px; max-width: 700px; }

/* Avatar */
.avatar-block { display: flex; align-items: center; gap: 20px; background: #fff7f0; border-radius: 16px; padding: 20px; border: 2px solid #ffe3cf; }
.avatar { width: 64px; height: 64px; border-radius: 50%; background: var(--brand-orange); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; flex-shrink: 0; }
.avatar-info { display: flex; flex-direction: column; gap: 6px; }
.avatar-name { font-size: 18px; font-weight: 700; color: var(--brand-purple); }
.role-badge { display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: 13px; font-weight: 700; }
.role-admin   { background: #ffeaea; color: var(--brand-red, #d63031); }
.role-teacher { background: #ffe3cf; color: var(--brand-orange); }
.role-student { background: #e8f4ff; color: #2a7bbf; }

/* Form */
.profile-form { background: #fff; border-radius: 16px; padding: 24px; border: 2px solid #ffe3cf; }
.form-section { margin-bottom: 24px; }
.form-section:last-of-type { margin-bottom: 0; }
.form-section h2 { font-size: 16px; font-weight: 700; color: var(--brand-purple); margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid #ffe3cf; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 13px; font-weight: 600; color: #555; }
.field input { padding: 10px 14px; border-radius: 10px; border: 1.5px solid #e0d5ff; font-size: 15px; outline: none; transition: border-color 0.2s; }
.field input:focus { border-color: var(--brand-orange); }
.field input:disabled { background: #f5f5f5; color: #aaa; cursor: not-allowed; }
.field-hint { font-size: 12px; color: #aaa; }
.field-error { font-size: 12px; color: #e03c3c; font-weight: 600; }

.alert-success { background: #e6f9ef; color: #22a55b; padding: 12px 16px; border-radius: 10px; font-weight: 600; font-size: 14px; margin-top: 16px; }
.alert-error   { background: #fdeaea; color: #e03c3c; padding: 12px 16px; border-radius: 10px; font-weight: 600; font-size: 14px; margin-top: 16px; }

.admin-note {
  background: #fff4db;
  border: 1px solid #ffe3af;
  color: #5f3e0b;
  border-radius: 14px;
  padding: 16px 18px;
  margin-top: 16px;
  line-height: 1.6;
}

.student-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px 24px;
  border: 2px solid #ffe3cf;
}
.student-card h2 {
  font-size: 18px;
  margin: 0 0 12px;
  color: var(--brand-purple);
}
.student-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px 16px;
  margin-bottom: 14px;
  font-size: 14px;
}
.grades-title {
  font-size: 16px;
  margin: 8px 0;
  color: var(--brand-purple);
}
.grades-summary {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 14px;
  margin-bottom: 10px;
}
.grades-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.grade-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff7f0;
  border: 1px solid #ffe3cf;
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 14px;
}
.grade-date { color: #888; white-space: nowrap; }
.grade-group { flex: 1; color: #555; font-size: 13px; }
.grade-value { margin-left: auto; font-size: 16px; color: var(--brand-purple); }

.form-actions { margin-top: 20px; }
.btn-save { background: var(--brand-orange); color: #fff; border: none; padding: 12px 28px; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.btn-save:hover:not(:disabled) { background: var(--brand-red, #d63031); }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
