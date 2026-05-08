<template>
  <div class="lesson-material-page">
    <h1>Материал урока</h1>

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
          <select v-model.number="filters.group_id" @change="loadLessons" :disabled="!filters.teacher_id">
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

    <!-- Журнал занятий -->
    <template v-else-if="filteredLessons.length">

      <!-- Заголовок группы -->
      <div class="group-header">
        <h2 class="group-title">Группа {{ currentGroup?.name || '—' }}, {{ currentTeacher?.full_name || '—' }}</h2>
      </div>

      <!-- Расписание занятий -->
      <div v-if="scheduleSlots.length" class="schedule-block">
        <span class="schedule-label">Расписание занятий:</span>
        <span v-for="slot in scheduleSlots" :key="slot" class="schedule-chip">{{ slot }}</span>
      </div>

      <!-- Таблица журнала -->
      <div class="journal-wrap">
        <div class="journal-head">
          <div class="jh-date">Дата занятия</div>
          <div class="jh-topic">Тема занятия</div>
          <div class="jh-action">
            <button class="btn-plus" @click="openCreate" :disabled="!filters.group_id" title="Добавить новое занятие">+</button>
          </div>
        </div>

        <div v-for="lesson in filteredLessons" :key="lesson.id" class="journal-row">
          <div class="jr-date">{{ formatDateTime(lesson.lesson_date, lesson.time_start) }}</div>
          <div class="jr-topic">
            <ul v-if="topicLines(lesson.topic).length > 1" class="topic-list">
              <li v-for="(line, i) in topicLines(lesson.topic)" :key="i">{{ line }}</li>
            </ul>
            <span v-else class="topic-plain">{{ lesson.topic || 'Тема не заполнена' }}</span>
          </div>
          <div class="jr-action">
            <button class="btn-pencil" @click="openEdit(lesson)" title="Редактировать">✏️</button>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="!loading" class="empty-state">
      <p>{{ filters.group_id ? 'Для выбранной группы пока нет занятий с датой.' : 'Выберите группу для просмотра материалов урока.' }}</p>
      <button v-if="filters.group_id" class="btn-add" @click="openCreate">+ Добавить материал</button>
    </div>

    <div v-if="modal" class="modal-backdrop" @click.self="modal = false">
      <div class="modal">
        <h2>{{ editingId ? 'Редактировать материал' : 'Добавить материал' }}</h2>

        <div class="form-grid">
          <label>Дата занятия
            <input v-model="form.lesson_date" type="date" required />
          </label>

          <label class="full">Тема занятия
            <textarea
              v-model="form.topic"
              rows="6"
              placeholder="Каждая активность с новой строки:&#10;игра&#10;проверка домашнего задания&#10;повторение слов"
              required
            ></textarea>
          </label>
        </div>

        <p v-if="formError" class="form-error">{{ formError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" @click="modal = false">Отмена</button>
          <button class="btn-save" @click="saveLesson" :disabled="saving">
            {{ saving ? 'Сохраняю...' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import http from '@/api/http'

const loading = ref(false)
const saving = ref(false)
const modal = ref(false)
const editingId = ref<number | null>(null)
const formError = ref('')

const branches = ref<any[]>([])
const teachers = ref<any[]>([])
const groups = ref<any[]>([])
const lessons = ref<any[]>([])
const editingLesson = ref<any | null>(null)

const filters = reactive({
  branch_id: null as number | null,
  teacher_id: null as number | null,
  group_id: null as number | null,
  date_from: '',
  date_to: '',
  student_name: '',
})

const emptyForm = () => ({ lesson_date: '', topic: '' })
const form = reactive(emptyForm())

// Текущая группа и преподаватель для заголовка
const currentGroup = computed(() => groups.value.find((g: any) => g.id === filters.group_id) || null)
const currentTeacher = computed(() => teachers.value.find((t: any) => t.id === filters.teacher_id) || null)

// Уникальные слоты расписания (день + время) из загруженных занятий
const DAY_LABELS: Record<string, string> = {
  monday: 'Пн', tuesday: 'Вт', wednesday: 'Ср',
  thursday: 'Чт', friday: 'Пт', saturday: 'Сб', sunday: 'Вс',
}

const scheduleSlots = computed(() => {
  const seen = new Set<string>()
  const result: string[] = []
  for (const lesson of lessons.value) {
    if (filters.group_id != null && lesson.group_id != null && lesson.group_id !== filters.group_id) continue
    const day = DAY_LABELS[lesson.day_of_week] || lesson.day_of_week || ''
    const time = (lesson.time_start || '').slice(0, 5)
    const key = `${day} ${time}`.trim()
    if (key && !seen.has(key)) {
      seen.add(key)
      result.push(key)
    }
  }
  return result
})

const sortedLessons = computed(() => {
  return lessons.value
    .filter((l) => Boolean(l.lesson_date))
    .slice()
    .sort((a, b) => new Date(b.lesson_date).getTime() - new Date(a.lesson_date).getTime())
})

const filteredLessons = computed(() => {
  let list = sortedLessons.value
  if (filters.date_from) list = list.filter((l) => l.lesson_date >= filters.date_from)
  if (filters.date_to) list = list.filter((l) => l.lesson_date.slice(0, 10) <= filters.date_to)
  if (filters.student_name) {
    const q = filters.student_name.toLowerCase()
    list = list.filter((l) => (l.topic || '').toLowerCase().includes(q))
  }
  return list
})

function topicLines(topic: string | null): string[] {
  if (!topic) return []
  return topic.split('\n').map((s) => s.trim()).filter(Boolean)
}

function formatDateTime(isoDate: string, timeStart?: string | null): string {
  if (!isoDate) return '—'
  const datePart = new Date(isoDate).toLocaleDateString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
  })
  const timePart = timeStart ? timeStart.slice(0, 5) : ''
  return timePart ? `${datePart} ${timePart}` : datePart
}

function toIsoDate(dateStr: string): string {
  return `${dateStr}T00:00:00`
}

function clearFilters() {
  filters.date_from = ''
  filters.date_to = ''
  filters.student_name = ''
}

async function loadBranches() {
  try { branches.value = (await http.get('/branches/')).data } catch { branches.value = [] }
}

async function onBranchChange() {
  filters.teacher_id = null
  filters.group_id = null
  teachers.value = []
  groups.value = []
  lessons.value = []
  if (filters.branch_id) {
    try { teachers.value = (await http.get('/teachers/', { params: { branch_id: filters.branch_id } })).data } catch { teachers.value = [] }
  }
}

async function onTeacherChange() {
  filters.group_id = null
  groups.value = []
  lessons.value = []
  if (filters.teacher_id) {
    try {
      const params: any = {}
      if (filters.branch_id) params.branch_id = filters.branch_id
      if (filters.teacher_id) params.teacher_id = filters.teacher_id
      groups.value = (await http.get('/groups', { params })).data
    } catch { groups.value = [] }
  }
}

async function loadLessons() {
  if (!filters.group_id) { lessons.value = []; return }
  loading.value = true
  try {
    lessons.value = (await http.get('/schedule', { params: { group_id: filters.group_id } })).data
  } catch { lessons.value = [] }
  finally { loading.value = false }
}

function openCreate() {
  if (!filters.group_id) return
  Object.assign(form, emptyForm())
  editingId.value = null
  editingLesson.value = null
  formError.value = ''
  modal.value = true
}

function openEdit(lesson: any) {
  Object.assign(form, {
    lesson_date: lesson.lesson_date ? lesson.lesson_date.slice(0, 10) : '',
    topic: lesson.topic || '',
  })
  editingLesson.value = lesson
  editingId.value = lesson.id
  formError.value = ''
  modal.value = true
}

function dayOfWeekFromDate(dateStr: string) {
  const day = new Date(`${dateStr}T12:00:00`).getDay()
  return ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'][day]
}

function getTemplateLesson() {
  return editingLesson.value || lessons.value.find((l) => l.group_id === filters.group_id) || null
}

async function saveLesson() {
  if (!filters.group_id) { formError.value = 'Сначала выберите группу'; return }
  if (!form.lesson_date || !form.topic.trim()) { formError.value = 'Заполните дату и тему занятия'; return }
  const template = getTemplateLesson()
  if (!template) { formError.value = 'Не удалось определить параметры занятия. Сначала добавьте расписание для группы.'; return }

  saving.value = true
  formError.value = ''
  try {
    const payload = {
      group_id: filters.group_id,
      teacher_id: template.teacher_id,
      classroom_id: template.classroom_id,
      branch_id: template.branch_id,
      program_id: template.program_id,
      day_of_week: dayOfWeekFromDate(form.lesson_date),
      time_start: template.time_start?.slice(0, 8),
      time_end: template.time_end?.slice(0, 8),
      topic: form.topic.trim(),
      is_recurring: false,
      lesson_date: toIsoDate(form.lesson_date),
    }
    if (editingId.value) {
      await http.put(`/schedule/${editingId.value}`, payload)
    } else {
      await http.post('/schedule', payload)
    }
    modal.value = false
    await loadLessons()
  } catch (e: any) {
    formError.value = e?.response?.data?.detail || 'Ошибка при сохранении'
  } finally { saving.value = false }
}

onMounted(loadBranches)
</script>

<style scoped>
.lesson-material-page {
  max-width: 1100px;
}

.lesson-material-page h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 24px;
}

/* Оранжевая панель фильтров */
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
  height: 36px;
  padding: 8px 4px;
  border: none;
  border-radius: 0;
  background: none;
  color: var(--brand-orange);
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  cursor: pointer;
  white-space: nowrap;
}
.btn-clear:hover {
  text-decoration: underline;
}

/* Заголовок группы */
.group-header {
  margin: 16px 0 8px;
}

.group-title {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #f59e0b;
}

/* Расписание */
.schedule-block {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
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

/* Таблица журнала */
.journal-wrap {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  overflow: hidden;
}

.journal-head {
  display: grid;
  grid-template-columns: 180px 1fr 54px;
  background: #f7e2c8;
  border-bottom: 1px solid #d1d5db;
}

.jh-date, .jh-topic {
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 700;
  color: #111;
}

.jh-date {
  border-right: 1px solid #d1d5db;
}

.jh-action {
  display: flex;
  align-items: center;
  justify-content: center;
  border-left: 1px solid #d1d5db;
}

.journal-row {
  display: grid;
  grid-template-columns: 180px 1fr 54px;
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

.jr-topic {
  padding: 10px 14px;
  display: flex;
  align-items: flex-start;
}

.topic-list {
  margin: 0;
  padding-left: 18px;
  list-style: disc;
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
}

.topic-plain {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
}

.jr-action {
  border-left: 1px solid #e5e7eb;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 10px;
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
}

.btn-plus:hover { background: #d97706; }
.btn-plus:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-pencil {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 2px;
  line-height: 1;
  opacity: 0.75;
}
.btn-pencil:hover { opacity: 1; }

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

/* Пустое состояние */
.empty-state {
  text-align: center;
  padding: 32px;
  color: #64748b;
}

.empty-state p {
  margin: 0;
  text-align: center;
}

.btn-add {
  border: none;
  border-radius: 10px;
  background: var(--brand-orange, #f59e0b);
  color: #fff;
  font-weight: 700;
  padding: 10px 16px;
  cursor: pointer;
  margin-top: 10px;
}
.btn-add:disabled { opacity: 0.6; cursor: not-allowed; }

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
  padding: 22px;
}

.modal h2 {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 700;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 4px;
}

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
  margin-top: 14px;
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
  .journal-row { grid-template-columns: 140px 1fr 46px; }
}
</style>
