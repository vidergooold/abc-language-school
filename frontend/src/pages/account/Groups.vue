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
        <div class="form-grid">
          <div class="form-row">
            <label>Тип занятия *</label>
            <select v-model="newGroup.lesson_type" required>
              <option value="group">Групповое занятие</option>
              <option value="individual">Индивидуальное занятие</option>
            </select>
          </div>

          <div class="form-row">
            <label>Язык *</label>
            <select v-model="newGroup.language" @change="onLanguageChange" required>
              <option value="">— выберите язык —</option>
              <option v-for="language in languageOptions" :key="language" :value="language">{{ language }}</option>
            </select>
          </div>

          <div class="form-row">
            <label>Программа *</label>
            <select v-model.number="newGroup.program_id" :disabled="!newGroup.language" required>
              <option :value="''">{{ newGroup.language ? '— выберите программу —' : 'Сначала выберите язык' }}</option>
              <option v-for="program in filteredPrograms" :key="program.id" :value="program.id">{{ program.name }}</option>
            </select>
          </div>

          <div class="form-row">
            <label>Преподаватель *</label>
            <select v-model.number="newGroup.teacher_id" required>
              <option :value="''">— выберите преподавателя —</option>
              <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
            </select>
          </div>

          <div class="form-row">
            <label>Филиал *</label>
            <select v-model.number="newGroup.branch_id" @change="onBranchChange" required>
              <option :value="''">— выберите филиал —</option>
              <option v-for="branch in branches" :key="branch.id" :value="branch.id">{{ branch.name }}</option>
            </select>
          </div>

          <div class="form-row">
            <label>Кабинет *</label>
            <select v-model.number="newGroup.classroom_id" :disabled="!newGroup.branch_id" required>
              <option :value="''">{{ newGroup.branch_id ? '— выберите кабинет —' : 'Сначала выберите филиал' }}</option>
              <option v-for="classroom in availableClassrooms" :key="classroom.id" :value="classroom.id">{{ classroom.name }}</option>
            </select>
          </div>

          <div class="form-row">
            <label>Начало занятия *</label>
            <input v-model="newGroup.time_start" type="time" required />
          </div>

          <div class="form-row">
            <label>Конец занятия</label>
            <input :value="autoTimeEnd || '—'" type="text" readonly class="input-readonly" :title="autoTimeEndHint" />
          </div>

          <div class="form-row full">
            <label>Дни занятий *</label>
            <div class="days-checkboxes">
              <label v-for="day in dayOptions" :key="day.value">
                <input v-model="newGroup.lesson_days" type="checkbox" :value="day.value" />
                {{ day.label }}
              </label>
            </div>
          </div>
        </div>
        <div v-if="createError" class="form-error">{{ createError }}</div>
        <div class="form-actions">
          <button type="submit" :disabled="saving" class="btn-primary">
            {{ saving ? 'Создание...' : (newGroup.lesson_type === 'individual' ? 'Создать индивидуальное занятие' : 'Создать группу') }}
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
            <th>Тип</th>
            <th>Язык</th>
            <th>Программа</th>
            <th>Преподаватель</th>
            <th>Филиал</th>
            <th>Кабинет</th>
            <th>Время</th>
            <th>Дни</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in filtered" :key="g.id">
            <td class="col-name">{{ g.name }}</td>
            <td><span class="type-badge" :class="g.is_individual ? 'individual' : 'group'">{{ g.is_individual ? 'Инд.' : 'Гр.' }}</span></td>
            <td>{{ g.language || '—' }}</td>
            <td>{{ g.program_name || '—' }}</td>
            <td>{{ teacherName(g.teacher_id) }}</td>
            <td>{{ branchLabel(g.id) }}</td>
            <td>{{ classroomLabel(g.id) }}</td>
            <td>{{ lessonTimeLabel(g.id) }}</td>
            <td>{{ lessonDaysLabel(g.id) }}</td>
            <td><span class="status-badge" :class="g.status">{{ statusLabel(g.status) }}</span></td>
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
const teachers = ref<any[]>([])
const programs = ref<any[]>([])
const branches = ref<any[]>([])
const classrooms = ref<any[]>([])
const schedule = ref<any[]>([])
const search = ref('')
const showCreateForm = ref(false)
const saving = ref(false)
const createError = ref('')

const dayOptions = [
  { value: 'monday', label: 'Пн' },
  { value: 'tuesday', label: 'Вт' },
  { value: 'wednesday', label: 'Ср' },
  { value: 'thursday', label: 'Чт' },
  { value: 'friday', label: 'Пт' },
  { value: 'saturday', label: 'Сб' },
  { value: 'sunday', label: 'Вс' },
]
const DAY_ORDER = dayOptions.map((day) => day.value)
const DAY_LABELS = dayOptions.reduce((acc, day) => {
  acc[day.value] = day.label
  return acc
}, {} as Record<string, string>)

const emptyGroup = () => ({
  lesson_type: 'group' as 'group' | 'individual',
  language: '',
  program_id: '' as number | '',
  teacher_id: '' as number | '',
  branch_id: '' as number | '',
  classroom_id: '' as number | '',
  time_start: '',
  lesson_days: [] as string[],
})
const newGroup = ref(emptyGroup())

const filtered = computed(() =>
  groups.value.filter(g =>
    !search.value ||
    (g.name ?? '').toLowerCase().includes(search.value.toLowerCase())
  )
)

const languageOptions = computed(() =>
  [...new Set(programs.value.map((program: any) => program.language).filter(Boolean))]
    .sort((a, b) => String(a).localeCompare(String(b), 'ru'))
)

const filteredPrograms = computed(() => {
  if (!newGroup.value.language) return []
  return programs.value.filter(
    (program: any) => normalizeText(program.language) === normalizeText(newGroup.value.language)
  )
})

const availableClassrooms = computed(() => {
  if (!newGroup.value.branch_id) return []
  return classrooms.value.filter((classroom: any) => classroom.branch_id === newGroup.value.branch_id)
})

const selectedProgram = computed(() => {
  if (!newGroup.value.program_id) return null
  return programs.value.find((p: any) => p.id === newGroup.value.program_id) ?? null
})

const autoTimeEnd = computed((): string => {
  if (!newGroup.value.time_start || !selectedProgram.value) return ''
  const duration: number | null = selectedProgram.value.lesson_duration_minutes ?? null
  if (!duration) return ''
  const parts = newGroup.value.time_start.split(':')
  if (parts.length < 2) return ''
  const totalMinutes = parseInt(parts[0] as string, 10) * 60 + parseInt(parts[1] as string, 10) + duration
  const endH = Math.floor(totalMinutes / 60) % 24
  const endM = totalMinutes % 60
  return `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`
})

const autoTimeEndHint = computed((): string => {
  if (!selectedProgram.value) return 'Выберите программу для автоматического расчёта'
  const duration: number | null = selectedProgram.value.lesson_duration_minutes ?? null
  if (!duration) return 'Длительность программы не определена'
  return `Продолжительность занятия: ${duration} мин.`
})

const groupScheduleMeta = computed(() => {
  const meta = new Map<number, any>()
  for (const lesson of schedule.value) {
    const existing = meta.get(lesson.group_id)
    if (!existing) {
      meta.set(lesson.group_id, {
        branch_name: lesson.branch_name || '—',
        classroom_name: lesson.classroom_name || '—',
        time_start: lesson.time_start || '',
        time_end: lesson.time_end || '',
        days: lesson.day_of_week ? [lesson.day_of_week] : [],
      })
      continue
    }
    if (lesson.branch_name && existing.branch_name === '—') existing.branch_name = lesson.branch_name
    if (lesson.classroom_name && existing.classroom_name === '—') existing.classroom_name = lesson.classroom_name
    if (!existing.time_start && lesson.time_start) existing.time_start = lesson.time_start
    if (!existing.time_end && lesson.time_end) existing.time_end = lesson.time_end
    if (lesson.day_of_week && !existing.days.includes(lesson.day_of_week)) {
      existing.days.push(lesson.day_of_week)
    }
  }

  for (const value of meta.values()) {
    value.days.sort((a: string, b: string) => DAY_ORDER.indexOf(a) - DAY_ORDER.indexOf(b))
  }

  return meta
})

function normalizeText(value: string | null | undefined) {
  return (value || '').trim().toLowerCase()
}

function teacherName(teacherId: number | null) {
  if (!teacherId) return '—'
  const t = teachers.value.find((t: any) => t.id === teacherId)
  return t ? t.full_name : '—'
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    recruiting: 'Набор',
    active: 'Активна',
    finished: 'Завершена',
    completed: 'Завершена',
    suspended: 'Приостановлена',
  }
  return labels[status] || status
}

function groupMeta(groupId: number) {
  return groupScheduleMeta.value.get(groupId) || {
    branch_name: '—',
    classroom_name: '—',
    time_start: '',
    time_end: '',
    days: [],
  }
}

function branchLabel(groupId: number) {
  return groupMeta(groupId).branch_name || '—'
}

function classroomLabel(groupId: number) {
  return groupMeta(groupId).classroom_name || '—'
}

function lessonTimeLabel(groupId: number) {
  const meta = groupMeta(groupId)
  if (!meta.time_start || !meta.time_end) return '—'
  return `${fmtTime(meta.time_start)}–${fmtTime(meta.time_end)}`
}

function lessonDaysLabel(groupId: number) {
  const days = groupMeta(groupId).days
  if (!days.length) return '—'
  return days.map((day: string) => DAY_LABELS[day] || day).join('/')
}

function fmtTime(value: string | null) {
  return value ? value.slice(0, 5) : ''
}

function onLanguageChange() {
  if (!filteredPrograms.value.some((program: any) => program.id === newGroup.value.program_id)) {
    newGroup.value.program_id = ''
  }
}

function onBranchChange() {
  if (!availableClassrooms.value.some((classroom: any) => classroom.id === newGroup.value.classroom_id)) {
    newGroup.value.classroom_id = ''
  }
}

function formatCreateError(detail: any) {
  if (typeof detail === 'string') return detail
  if (detail?.message && Array.isArray(detail.conflicts)) {
    return [detail.message, ...detail.conflicts.map((item: any) => item.message)].join(' ')
  }
  return 'Не удалось создать группу'
}

async function load() {
  try {
    const [groupsRes, teachersRes, programsRes, branchesRes, classroomsRes, scheduleRes] = await Promise.all([
      http.get('/groups', { params: { active_only: false } }).catch(() => ({ data: [] })),
      http.get('/teachers').catch(() => ({ data: [] })),
      http.get('/programs').catch(() => ({ data: [] })),
      http.get('/branches', { params: { for_schedule: true } }).catch(() => ({ data: [] })),
      http.get('/classrooms').catch(() => ({ data: [] })),
      http.get('/schedule').catch(() => ({ data: [] })),
    ])
    groups.value = Array.isArray(groupsRes.data) ? groupsRes.data : []
    teachers.value = Array.isArray(teachersRes.data) ? teachersRes.data : []
    programs.value = Array.isArray(programsRes.data) ? programsRes.data : []
    branches.value = Array.isArray(branchesRes.data) ? branchesRes.data : []
    classrooms.value = Array.isArray(classroomsRes.data) ? classroomsRes.data : []
    schedule.value = Array.isArray(scheduleRes.data) ? scheduleRes.data : []
  } finally {
    loading.value = false
  }
}

function toggleCreateForm() {
  showCreateForm.value = !showCreateForm.value
  if (!showCreateForm.value) cancelCreate()
}

function cancelCreate() {
  newGroup.value = emptyGroup()
  createError.value = ''
  showCreateForm.value = false
}

async function createGroup() {
  if (
    !newGroup.value.language ||
    !newGroup.value.program_id ||
    !newGroup.value.teacher_id ||
    !newGroup.value.branch_id ||
    !newGroup.value.classroom_id ||
    !newGroup.value.time_start ||
    !newGroup.value.lesson_days.length
  ) {
    createError.value = 'Заполните все обязательные поля'
    return
  }
  saving.value = true
  createError.value = ''
  try {
    await http.post('/groups', {
      language: newGroup.value.language,
      program_id: newGroup.value.program_id,
      teacher_id: newGroup.value.teacher_id,
      branch_id: newGroup.value.branch_id,
      classroom_id: newGroup.value.classroom_id,
      time_start: newGroup.value.time_start,
      lesson_days: newGroup.value.lesson_days,
      is_individual: newGroup.value.lesson_type === 'individual',
    })
    window.dispatchEvent(new CustomEvent('group-created', {
      detail: {
        teacher_id: newGroup.value.teacher_id,
      },
    }))
    await load()
    cancelCreate()
  } catch (err: any) {
    createError.value = formatCreateError(err.response?.data?.detail)
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
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.form-row { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.form-row.full { grid-column: 1 / -1; }
.form-row label { font-weight: 600; color: var(--brand-purple); font-size: 14px; }
.form-row input, .form-row select { padding: 10px 12px; border-radius: 8px; border: 1.5px solid #ffe3cf; font-size: 15px; outline: none; font-family: inherit; }
.form-row input:focus, .form-row select:focus { border-color: var(--brand-orange); }
.input-readonly { background: #f5f5f5; color: #666; cursor: default; }
.days-checkboxes { display: flex; flex-wrap: wrap; gap: 12px; padding: 10px 12px; border: 1.5px solid #ffe3cf; border-radius: 8px; background: #fff; }
.days-checkboxes label { display: inline-flex; align-items: center; gap: 6px; color: #444; font-weight: 500; }
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
.status-badge.finished { background: #f3f4f6; color: #6b7280; }
.status-badge.completed { background: #f3f4f6; color: #6b7280; }
.status-badge.suspended { background: #fef3c7; color: #92400e; }

.type-badge { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; }
.type-badge.group { background: #dbeafe; color: #1e40af; }
.type-badge.individual { background: #fce7f3; color: #9d174d; }

@media (max-width: 720px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>
