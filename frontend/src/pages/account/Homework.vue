<template>
  <div class="homework-page">
    <h1>Домашнее задание</h1>

    <!-- Оранжевая панель фильтров -->
    <div class="filters-card report-filters">
      <div class="filter-grid">
        <div class="field filter-field">
          <label>Филиал</label>
          <select v-model.number="filters.branch_id" @change="onBranchChange">
            <option :value="null">Выберите филиал</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>
        <div class="field filter-field">
          <label>Преподаватель</label>
          <select v-model.number="filters.teacher_id" @change="onTeacherChange" :disabled="!filters.branch_id">
            <option :value="null">Выберите преподавателя</option>
            <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
          </select>
        </div>
        <div class="field filter-field">
          <label>Группа</label>
          <select v-model.number="filters.group_id" @change="loadHomeworks" :disabled="!filters.teacher_id">
            <option :value="null">Выберите группу</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="field filter-field date-field">
          <label>Дата с</label>
          <input type="date" v-model="filters.date_from" />
        </div>
        <div class="field filter-field date-field">
          <label>по</label>
          <input type="date" v-model="filters.date_to" />
        </div>
        <div class="field filter-field student-field">
          <label>Студент</label>
          <input type="text" v-model.trim="filters.student_name" placeholder="Поиск по имени..." />
        </div>
        <div class="field filter-field field-clear">
          <label>&nbsp;</label>
          <button class="btn-clear clear-btn" @click="clearFilters">Очистить</button>
        </div>
      </div>
    </div>

    <!-- Скелетон -->
    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-card" v-for="n in 4" :key="n"></div>
    </div>

    <!-- Журнал домашних заданий -->
    <template v-else-if="filters.group_id">

      <!-- Заголовок группы -->
      <div class="group-header">
        <h2 class="group-title">Группа {{ currentGroup?.name || '—' }}, {{ currentTeacher?.full_name || '—' }}</h2>
      </div>

      <!-- Расписание + ФИО преподавателя -->
      <div class="group-meta">
        <div v-if="scheduleSlots.length" class="schedule-block">
          <span class="schedule-label">Расписание занятий:</span>
          <span v-for="slot in scheduleSlots" :key="slot" class="schedule-chip">{{ slot }}</span>
        </div>
        <div v-if="currentTeacher" class="teacher-line">Преподаватель: {{ currentTeacher.full_name }}</div>
      </div>

      <!-- Таблица домашних заданий -->
      <div class="journal-wrap">
        <div class="journal-head">
          <div class="jh-date">На каком занятии задано</div>
          <div class="jh-task">Задание
            <button class="btn-plus" @click="openCreate" :disabled="!filters.group_id" title="Добавить задание">+</button>
          </div>
        </div>

        <template v-if="filteredHomeworks.length">
          <div v-for="hw in filteredHomeworks" :key="hw.id" class="journal-row">
            <div class="jr-date">{{ formatDateTime(hw.lesson_date) }}</div>
            <div class="jr-task">
              <span class="task-text">{{ hw.description || hw.title || '—' }}</span>
              <button class="btn-pencil" @click="openEdit(hw)" title="Редактировать">✏️</button>
            </div>
          </div>
        </template>
        <div v-else class="journal-empty">Заданий нет. Нажмите <strong>+</strong>, чтобы добавить.</div>
      </div>
    </template>

    <!-- Выбери группу -->
    <div v-else-if="!loading" class="empty-state">
      <p>Выберите группу для просмотра домашних заданий.</p>
    </div>

    <!-- Модалка -->
    <div v-if="modal" class="modal-backdrop" @click.self="modal = false">
      <div class="modal">
        <h2>{{ editingId ? 'Редактировать задание' : 'Добавить задание' }}</h2>

        <div class="form-grid">
          <label>На каком занятии задано
            <input v-model="form.lesson_date" type="date" />
          </label>
          <label class="full">Задание
            <textarea
              v-model="form.description"
              rows="5"
              placeholder="Опишите домашнее задание..."
              required
            ></textarea>
          </label>
        </div>

        <p v-if="formError" class="form-error">{{ formError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" @click="modal = false">Отмена</button>
          <button class="btn-save" @click="save" :disabled="saving">
            {{ saving ? 'Сохраняю...' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const loading = ref(false)
const saving = ref(false)
const modal = ref(false)
const editingId = ref<number | null>(null)
const formError = ref('')

const branches = ref<any[]>([])
const teachers = ref<any[]>([])
const groups = ref<any[]>([])
const homeworks = ref<any[]>([])
const scheduleItems = ref<any[]>([])

const myTeacherId = ref<number | null>(null)

const filters = reactive({
  branch_id: null as number | null,
  teacher_id: null as number | null,
  group_id: null as number | null,
  date_from: '',
  date_to: '',
  student_name: '',
})

const emptyForm = () => ({ lesson_date: '', description: '' })
const form = reactive(emptyForm())

const currentGroup = computed(() => groups.value.find((g: any) => g.id === filters.group_id) || null)
const currentTeacher = computed(() => teachers.value.find((t: any) => t.id === filters.teacher_id) || null)

const DAY_LABELS: Record<string, string> = {
  monday: 'Пн', tuesday: 'Вт', wednesday: 'Ср',
  thursday: 'Чт', friday: 'Пт', saturday: 'Сб', sunday: 'Вс',
}

const scheduleSlots = computed(() => {
  const seen = new Set<string>()
  const result: string[] = []
  for (const item of scheduleItems.value) {
    const day = DAY_LABELS[item.day_of_week] || item.day_of_week || ''
    const time = (item.time_start || '').slice(0, 5)
    const key = `${day} ${time}`.trim()
    if (key && !seen.has(key)) { seen.add(key); result.push(key) }
  }
  return result
})

const sortedHomeworks = computed(() =>
  homeworks.value.slice().sort((a, b) => {
    const aD = a.lesson_date ? new Date(a.lesson_date).getTime() : 0
    const bD = b.lesson_date ? new Date(b.lesson_date).getTime() : 0
    return bD - aD
  })
)

const filteredHomeworks = computed(() => {
  let list = sortedHomeworks.value
  if (filters.date_from) list = list.filter((h) => (h.lesson_date || '') >= filters.date_from)
  if (filters.date_to) list = list.filter((h) => (h.lesson_date || '').slice(0, 10) <= filters.date_to)
  if (filters.student_name) {
    const q = filters.student_name.toLowerCase()
    list = list.filter((h) => ((h.description || '') + (h.title || '')).toLowerCase().includes(q))
  }
  return list
})

function formatDateTime(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  const datePart = d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
  // попробуем взять время из связанного занятия
  const timeStr = iso.includes('T') ? iso.slice(11, 16) : ''
  return timeStr && timeStr !== '00:00' ? `${datePart} ${timeStr}` : datePart
}

function clearFilters() {
  filters.date_from = ''
  filters.date_to = ''
  filters.student_name = ''
}

onMounted(async () => {
  await Promise.all([loadBranches()])
  if (auth.isTeacher) await resolveMyTeacherId()
})

async function resolveMyTeacherId() {
  try {
    const res = await http.get('/teachers/')
    const me = res.data.find((t: any) => t.email === auth.user?.email)
    myTeacherId.value = me?.id ?? null
  } catch { myTeacherId.value = null }
}

async function loadBranches() {
  try { branches.value = (await http.get('/branches/')).data } catch { branches.value = [] }
}

async function onBranchChange() {
  filters.teacher_id = null
  filters.group_id = null
  teachers.value = []
  groups.value = []
  homeworks.value = []
  scheduleItems.value = []
  if (!filters.branch_id) return
  try { teachers.value = (await http.get('/teachers/', { params: { branch_id: filters.branch_id } })).data } catch { teachers.value = [] }
}

async function onTeacherChange() {
  filters.group_id = null
  groups.value = []
  homeworks.value = []
  scheduleItems.value = []
  if (!filters.teacher_id) return
  try {
    const params: any = {}
    if (filters.branch_id) params.branch_id = filters.branch_id
    if (filters.teacher_id) params.teacher_id = filters.teacher_id
    groups.value = (await http.get('/groups', { params })).data
  } catch { groups.value = [] }
}

async function loadHomeworks() {
  if (!filters.group_id) { homeworks.value = []; scheduleItems.value = []; return }
  loading.value = true
  try {
    const [hwRes, schedRes] = await Promise.all([
      http.get('/homeworks/', { params: { group_id: filters.group_id } }),
      http.get('/schedule', { params: { group_id: filters.group_id } }),
    ])
    homeworks.value = hwRes.data
    scheduleItems.value = schedRes.data
  } catch { homeworks.value = []; scheduleItems.value = [] }
  finally { loading.value = false }
}

function openCreate() {
  if (!filters.group_id) return
  Object.assign(form, emptyForm())
  editingId.value = null
  formError.value = ''
  modal.value = true
}

function openEdit(hw: any) {
  form.lesson_date = hw.lesson_date ? hw.lesson_date.slice(0, 10) : ''
  form.description = hw.description || hw.title || ''
  editingId.value = hw.id
  formError.value = ''
  modal.value = true
}

async function save() {
  if (!form.description.trim()) { formError.value = 'Введите текст задания'; return }
  if (!filters.group_id) { formError.value = 'Сначала выберите группу'; return }

  saving.value = true
  formError.value = ''
  try {
    const lessonDateIso = form.lesson_date ? `${form.lesson_date}T00:00:00` : null

    if (editingId.value) {
      await http.put(`/homeworks/${editingId.value}`, {
        title: form.description.slice(0, 200),
        description: form.description,
        lesson_date: lessonDateIso,
        due_date: lessonDateIso ?? new Date().toISOString(),
      })
    } else {
      const teacherId = auth.isAdmin
        ? (filters.teacher_id ?? myTeacherId.value)
        : myTeacherId.value
      if (!teacherId) {
        formError.value = 'Не удалось определить преподавателя. Выберите преподавателя в фильтре или проверьте профиль.'
        saving.value = false
        return
      }
      await http.post('/homeworks/', {
        title: form.description.slice(0, 200),
        description: form.description,
        lesson_date: lessonDateIso,
        due_date: lessonDateIso ?? new Date().toISOString(),
        group_id: filters.group_id,
        teacher_id: teacherId,
        status: 'assigned',
      })
    }

    modal.value = false
    await loadHomeworks()
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    formError.value = typeof detail === 'string' ? detail : 'Ошибка при сохранении'
  } finally { saving.value = false }
}
</script>

<style scoped>
.homework-page {
  max-width: 1100px;
}

.homework-page h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 24px;
}

/* Оранжевая панель */
.filters-card,
.report-filters {
  background: #fff7f0;
  border: 1px solid #ffe3cf;
  border-radius: 14px;
  padding: 18px 20px;
  margin-bottom: 16px;
}

.filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 14px 20px;
  align-items: flex-end;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 180px;
}

.field label,
.filter-field label {
  font-size: 12px;
  font-weight: 700;
  color: var(--brand-orange);
  text-transform: uppercase;
  letter-spacing: .05em;
}

.date-field label {
  text-transform: none;
  font-size: 13px;
  font-weight: 600;
  color: #555;
  letter-spacing: 0;
}

.date-field {
  flex-direction: row;
  align-items: center;
  gap: 8px;
  min-width: unset;
}

.date-field label {
  white-space: nowrap;
}

.student-field {
  flex-direction: row;
  align-items: flex-end;
  gap: 8px;
  flex: 1;
  min-width: 240px;
}

.student-field label {
  display: none;
}

.student-field input {
  flex: 1;
}

.field select,
.field input[type="date"],
.field input[type="text"],
.filter-field select,
.filter-field input[type="date"],
.filter-field input[type="text"] {
  border: 1.5px solid #ffe3cf;
  border-radius: 8px;
  padding: 8px 12px;
  background: #fff;
  color: #444;
  font-size: 14px;
  font-family: inherit;
  outline: none;
}

.field select:focus,
.field input:focus {
  border-color: var(--brand-orange);
}

.field-clear { min-width: unset; }

.btn-clear {
  padding: 8px 4px;
  border: none;
  border-radius: 0;
  background: none;
  color: var(--brand-orange);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}
.btn-clear:hover { text-decoration: underline; }

/* Заголовок группы */
.group-header { margin: 16px 0 6px; }

.group-title {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #f59e0b;
}

/* Мета-строки */
.group-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}

.schedule-block {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.schedule-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.schedule-chip {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  color: #c2410c;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 13px;
  font-weight: 600;
}

.teacher-line {
  font-size: 14px;
  color: #6b7280;
}

/* Таблица */
.journal-wrap {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  overflow: hidden;
}

.journal-head {
  display: grid;
  grid-template-columns: 200px 1fr;
  background: #f7e2c8;
  border-bottom: 1px solid #d1d5db;
}

.jh-date {
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 700;
  color: #111;
  border-right: 1px solid #d1d5db;
}

.jh-task {
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 700;
  color: #111;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-plus {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 999px;
  background: #f59e0b;
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.btn-plus:hover { background: #d97706; }
.btn-plus:disabled { opacity: 0.6; cursor: not-allowed; }

.journal-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}
.journal-row:last-child { border-bottom: none; }
.journal-row:nth-child(even) { background: #fafafa; }

.jr-date {
  border-right: 1px solid #e5e7eb;
  padding: 12px 14px;
  font-size: 14px;
  font-weight: 700;
  color: #111;
  display: flex;
  align-items: flex-start;
}

.jr-task {
  padding: 12px 14px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.task-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
  flex: 1;
  white-space: pre-wrap;
}

.btn-pencil {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 2px;
  line-height: 1;
  opacity: 0.7;
  flex-shrink: 0;
}
.btn-pencil:hover { opacity: 1; }

.journal-empty {
  padding: 20px 16px;
  color: #6b7280;
  font-size: 14px;
}

/* Скелетон */
.skeleton-list { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
.skeleton-card {
  height: 52px;
  border-radius: 12px;
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Пустое */
.empty-state {
  text-align: center;
  padding: 32px;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  color: #64748b;
}

/* Модалка */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  display: grid;
  place-items: center;
  z-index: 30;
}

.modal {
  width: min(620px, calc(100vw - 24px));
  background: #fff;
  border-radius: 14px;
  padding: 24px;
}

.modal h2 { font-size: 20px; font-weight: 700; margin-bottom: 8px; }

.form-grid { display: flex; flex-direction: column; gap: 14px; margin-top: 12px; }
.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
}
.form-grid input,
.form-grid textarea {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 10px;
  font: inherit;
  font-weight: 400;
}
.form-grid textarea { resize: vertical; }

.form-error { color: #b91c1c; margin-top: 10px; font-size: 14px; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}
.btn-cancel, .btn-save {
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 600;
}
.btn-cancel { background: #e5e7eb; }
.btn-save { background: #0f766e; color: #fff; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

@media (max-width: 768px) {
  .filter-grid { flex-direction: column; }
  .field { min-width: 100%; }
  .journal-head,
  .journal-row { grid-template-columns: 130px 1fr; }
}
</style>
