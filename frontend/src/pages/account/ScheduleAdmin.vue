<template>
  <div class="schedule-admin">
    <div class="page-header">
      <h1>🗓 Расписание (управление)</h1>
      <button class="btn-add" @click="openCreate">+ Добавить занятие</button>
    </div>

    <div class="filters">
      <input v-model="search" type="text" placeholder="🔍 Поиск по теме / кабинету" />
      <select v-model="filterDay">
        <option value="">Все дни</option>
        <option v-for="d in days" :key="d.key" :value="d.key">{{ d.label }}</option>
      </select>
    </div>

    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-row" v-for="n in 8" :key="n"></div>
    </div>

    <template v-else-if="filtered.length">
      <div class="count-label">Показано: {{ filtered.length }} из {{ schedule.length }}</div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Группа</th>
              <th>Преподаватель</th>
              <th>День</th>
              <th>Время</th>
              <th>Кабинет</th>
              <th>Филиал</th>
              <th>Программа</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filtered" :key="item.id">
              <td class="col-group">{{ shortGroupName(groupName(item.group_id)) }}</td>
              <td>{{ teacherName(item.teacher_id) }}</td>
              <td class="col-days">{{ dayLabel(item.day_of_week) }}</td>
              <td class="col-time">{{ fmt(item.time_start) }}–{{ fmt(item.time_end) }}</td>
              <td>{{ classroomName(item.classroom_id) }}</td>
              <td>{{ branchName(item.branch_id) }}</td>
              <td>{{ programName(item.program_id) }}</td>
              <td class="col-actions">
                <button class="btn-icon edit" @click="openEdit(item)" title="Редактировать">✏️</button>
                <button
                  v-if="item.status !== 'cancelled'"
                  class="btn-icon cancel"
                  @click="confirmCancel(item)"
                  title="Отменить"
                >❌</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon">🗓</div>
      <p>{{ schedule.length ? 'Ничего не найдено по фильтру.' : 'Занятия пока не добавлены.' }}</p>
      <button class="btn-add" @click="openCreate">+ Добавить первое занятие</button>
    </div>

    <!-- ===== МОДАЛКА ===== -->
    <div v-if="modal" class="modal-backdrop" @click.self="modal = false">
      <div class="modal">
        <h2>{{ editingId ? 'Редактировать занятие' : 'Новое занятие' }}</h2>

        <div class="form-grid">
          <label>Группа
            <select v-model.number="form.group_id" @change="onGroupSelect" required>
              <option value="">— выберите —</option>
              <option v-for="g in availableGroups" :key="g.id" :value="g.id">{{ shortGroupName(g.name) }}</option>
            </select>
          </label>

          <label>Преподаватель
            <select v-model.number="form.teacher_id" @change="onTeacherSelect" required>
              <option value="">— выберите —</option>
              <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.full_name || t.email }}</option>
            </select>
          </label>

          <label>Аудитория
            <select v-model.number="form.classroom_id" required>
              <option value="">— выберите —</option>
              <option v-for="c in classrooms" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </label>

          <label>Филиал
            <select v-model.number="form.branch_id">
              <option value="">— выберите —</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </label>

          <label>Программа
            <select v-model.number="form.program_id">
              <option value="">— выберите —</option>
              <option v-for="p in programs" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </label>

          <label class="full">День недели
            <div class="days-checkboxes">
              <label v-for="d in dayOptions" :key="d.value">
                <input type="checkbox" :value="d.value" v-model="form.day_of_week" />
                {{ d.label }}
              </label>
            </div>
          </label>

          <label>Начало
            <input v-model="form.time_start" type="time" required />
          </label>

          <label>Окончание
            <input v-model="form.time_end" type="time" required />
          </label>

          <label class="full">Тема (необязательно)
            <input v-model="form.topic" type="text" placeholder="Например: Grammar, Speaking..." />
          </label>

          <label class="full checkbox-row">
            <input v-model="form.is_recurring" type="checkbox" />
            <span>Повторяющееся занятие</span>
          </label>
        </div>

        <div v-if="conflicts.length" class="conflict-box">
          <strong>⚠️ Конфликты:</strong>
          <ul>
            <li v-for="(c, i) in conflicts" :key="i">{{ c.message }}</li>
          </ul>
        </div>

        <p v-if="formError" class="form-error">⚠️ {{ formError }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" @click="modal = false">Отмена</button>
          <button class="btn-save" @click="saveLesson" :disabled="saving">
            <span v-if="saving" class="spinner"></span>
            {{ saving ? 'Сохраняю...' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===== ПОДТВЕРЖДЕНИЕ ОТМЕНЫ ===== -->
    <div v-if="cancelTarget" class="modal-backdrop" @click.self="cancelTarget = null">
      <div class="modal modal--sm">
        <h2>Отменить занятие?</h2>
        <p>Группа: <strong>{{ groupName(cancelTarget.group_id) }}</strong><br/>
           {{ dayLabel(cancelTarget.day_of_week) }}, {{ fmt(cancelTarget.time_start) }}–{{ fmt(cancelTarget.time_end) }}</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="cancelTarget = null">Назад</button>
          <button class="btn-danger" @click="doCancel" :disabled="saving">
            <span v-if="saving" class="spinner"></span>
            Отменить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import http from '@/api/http'

const loading = ref(true)
const saving = ref(false)
const schedule = ref<any[]>([])
const groups = ref<any[]>([])
const teachers = ref<any[]>([])
const classrooms = ref<any[]>([])
const branches = ref<any[]>([])
const programs = ref<any[]>([])
const search = ref('')
const filterDay = ref('')
const modal = ref(false)
const editingId = ref<number | null>(null)
const cancelTarget = ref<any>(null)
const conflicts = ref<any[]>([])
const formError = ref('')

const days = [
  { key: 'monday',    label: 'Понедельник' },
  { key: 'tuesday',   label: 'Вторник' },
  { key: 'wednesday', label: 'Среда' },
  { key: 'thursday',  label: 'Четверг' },
  { key: 'friday',    label: 'Пятница' },
  { key: 'saturday',  label: 'Суббота' },
]

const dayOptions = [
  { value: 'monday',    label: 'Пн' },
  { value: 'tuesday',   label: 'Вт' },
  { value: 'wednesday', label: 'Ср' },
  { value: 'thursday',  label: 'Чт' },
  { value: 'friday',    label: 'Пт' },
  { value: 'saturday',  label: 'Сб' },
  { value: 'sunday',    label: 'Вс' },
]

const emptyForm = () => ({
  group_id: '' as number | '',
  teacher_id: '' as number | '',
  classroom_id: '' as number | '',
  branch_id: '' as number | '',
  program_id: '' as number | '',
  day_of_week: [] as string[],
  time_start: '',
  time_end: '',
  topic: '',
  is_recurring: true,
})

const form = reactive(emptyForm())

const filtered = computed(() =>
  schedule.value
    .filter(i => !search.value ||
      (i.topic || '').toLowerCase().includes(search.value.toLowerCase()) ||
      classroomName(i.classroom_id).toLowerCase().includes(search.value.toLowerCase()) ||
      groupName(i.group_id).toLowerCase().includes(search.value.toLowerCase())
    )
    .filter(i => !filterDay.value || i.day_of_week === filterDay.value)
)

const availableGroups = computed(() => {
  if (!form.teacher_id) return groups.value
  return groups.value.filter((group: any) => !group.teacher_id || group.teacher_id === form.teacher_id)
})

function shortGroupName(name: string) {
  return name.split(' — ')[0].trim()
}
function groupName(id: number) {
  return groups.value.find(g => g.id === id)?.name || `Группа #${id}`
}
function teacherName(id: number) {
  const t = teachers.value.find(t => t.id === id)
  return t ? (t.full_name || t.email) : `Преп. #${id}`
}
function classroomName(id: number) {
  return classrooms.value.find(c => c.id === id)?.name || `Каб. #${id}`
}
function branchName(id: number) {
  return branches.value.find(b => b.id === id)?.name || '—'
}
function programName(id: number) {
  return programs.value.find(p => p.id === id)?.name || '—'
}
function dayLabel(key: string) {
  return days.find(d => d.key === key)?.label || key
}
function fmt(t: string) {
  return t ? t.slice(0, 5) : ''
}
function statusLabel(s: string) {
  return { scheduled: 'По расписанию', completed: 'Проведено', cancelled: 'Отменено', rescheduled: 'Перенесено' }[s] ?? s
}

function openCreate() {
  Object.assign(form, emptyForm())
  editingId.value = null
  conflicts.value = []
  formError.value = ''
  modal.value = true
}

async function openEdit(item: any) {
  let groupDays: string[] = []
  try {
    const res = await http.get('/schedule', { params: { group_id: item.group_id } })
    const groupLessons = Array.isArray(res.data) ? res.data : []
    groupDays = [...new Set(groupLessons.map((l: any) => l.day_of_week as string))]
  } catch {
    groupDays = [item.day_of_week]
  }
  Object.assign(form, {
    group_id: item.group_id,
    teacher_id: item.teacher_id,
    classroom_id: item.classroom_id,
    branch_id: item.branch_id || '',
    program_id: item.program_id || '',
    day_of_week: groupDays,
    time_start: item.time_start.slice(0, 5),
    time_end: item.time_end.slice(0, 5),
    topic: item.topic || '',
    is_recurring: item.is_recurring,
  })
  editingId.value = item.id
  conflicts.value = []
  formError.value = ''
  modal.value = true
}

function onTeacherSelect() {
  if (!form.teacher_id) return
  const currentGroup = groups.value.find((group: any) => group.id === form.group_id)
  if (currentGroup && currentGroup.teacher_id && currentGroup.teacher_id !== form.teacher_id) {
    form.group_id = ''
  }
}

function onGroupSelect() {
  const selectedGroup = groups.value.find((group: any) => group.id === form.group_id)
  if (selectedGroup?.teacher_id) {
    form.teacher_id = selectedGroup.teacher_id
  }
}

function confirmCancel(item: any) {
  cancelTarget.value = item
}

async function saveLesson() {
  if (!form.group_id || !form.teacher_id || !form.classroom_id || !form.day_of_week.length || !form.time_start || !form.time_end) {
    formError.value = 'Заполните все обязательные поля'
    return
  }
  saving.value = true
  formError.value = ''
  conflicts.value = []
  try {
    if (editingId.value) {
      const payload = { ...form, day_of_week: form.day_of_week[0] }
      await http.put(`/schedule/${editingId.value}`, payload)
    } else {
      for (const day of form.day_of_week) {
        const payload = { ...form, day_of_week: day }
        await http.post('/schedule', payload)
      }
    }
    modal.value = false
    await loadSchedule()
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    if (detail?.conflicts) {
      conflicts.value = detail.conflicts
      formError.value = detail.message
    } else {
      formError.value = detail || 'Ошибка при сохранении'
    }
  } finally {
    saving.value = false
  }
}

async function doCancel() {
  if (!cancelTarget.value) return
  saving.value = true
  try {
    await http.delete(`/schedule/${cancelTarget.value.id}`)
    cancelTarget.value = null
    await loadSchedule()
  } catch {
    cancelTarget.value = null
  } finally {
    saving.value = false
  }
}

async function loadSchedule() {
  try {
    const res = await http.get('/schedule')
    schedule.value = Array.isArray(res.data) ? res.data : []
  } catch {
    schedule.value = []
  }
}

onMounted(async () => {
  try {
    const [sRes, gRes, tRes, cRes, bRes, pRes] = await Promise.all([
      http.get('/schedule'),
      http.get('/groups'),
      http.get('/teachers'),
      http.get('/classrooms'),
      http.get('/branches'),
      http.get('/programs'),
    ])
    schedule.value = Array.isArray(sRes.data) ? sRes.data : []
    groups.value = Array.isArray(gRes.data) ? gRes.data : []
    teachers.value = Array.isArray(tRes.data) ? tRes.data : []
    classrooms.value = Array.isArray(cRes.data) ? cRes.data : []
    branches.value = Array.isArray(bRes.data) ? bRes.data : []
    programs.value = Array.isArray(pRes.data) ? pRes.data : []
  } catch {
    schedule.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.schedule-admin h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }

.btn-add { background: var(--brand-orange); color: #fff; border: none; border-radius: 10px; padding: 10px 20px; font-size: 15px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.btn-add:hover { background: var(--brand-red); }

.filters { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 180px; outline: none; }
.filters input:focus, .filters select:focus { border-color: var(--brand-orange); }

.count-label { font-size: 13px; color: #aaa; margin-bottom: 12px; }

.skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.skeleton-row { height: 46px; border-radius: 10px; background: linear-gradient(90deg,#fff0e8 25%,#ffe8d6 50%,#fff0e8 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; }
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }

.table-wrap { overflow-x: auto; border-radius: 14px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { background: var(--brand-orange); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #ffe3cf; vertical-align: middle; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #fff7f0; }
.col-group { font-weight: 600; color: #333; }
.col-days { color: var(--brand-orange); font-weight: 600; white-space: nowrap; }
.col-time { white-space: nowrap; }
.col-topic { color: #888; font-style: italic; }
.col-actions { display: flex; gap: 6px; }

.btn-icon { background: none; border: none; font-size: 16px; cursor: pointer; padding: 4px 6px; border-radius: 6px; transition: background 0.15s; }
.btn-icon.edit:hover { background: #f0e8ff; }
.btn-icon.cancel:hover { background: #ffeaea; }

.status-badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }
.s-scheduled   { background: #e8f4ff; color: #2a7bbf; }
.s-completed   { background: #e6f9ef; color: #22a55b; }
.s-cancelled   { background: #fdeaea; color: #e03c3c; }
.s-rescheduled { background: #fff3dc; color: #d9860a; }

.empty-state { text-align: center; padding: 48px; background: #fff7f0; border-radius: 14px; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { font-size: 16px; color: #888; margin-bottom: 20px; }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 999; display: flex; align-items: center; justify-content: center; padding: 16px; }
.modal { background: #fff; border-radius: 20px; padding: 32px; width: 100%; max-width: 560px; box-shadow: 0 12px 48px rgba(0,0,0,0.18); max-height: 90vh; overflow-y: auto; }
.modal--sm { max-width: 400px; }
.modal h2 { font-size: 22px; font-weight: 700; color: var(--brand-purple); margin-bottom: 20px; }
.modal p { font-size: 15px; color: #555; margin-bottom: 20px; line-height: 1.6; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px; }
.form-grid label { display: flex; flex-direction: column; font-size: 13px; font-weight: 600; color: var(--brand-purple); gap: 5px; }
.form-grid label.full { grid-column: 1 / -1; }
.form-grid input, .form-grid select { padding: 10px 12px; border-radius: 9px; border: 1.5px solid #e0d5ff; font-size: 14px; outline: none; }
.form-grid input:focus, .form-grid select:focus { border-color: var(--brand-orange); }
.checkbox-row { flex-direction: row !important; align-items: center; gap: 10px; }
.checkbox-row input { width: 18px; height: 18px; }

.days-checkboxes { display: flex; flex-wrap: wrap; gap: 10px; padding: 6px 0; }
.days-checkboxes label { display: flex; align-items: center; gap: 5px; font-size: 14px; font-weight: 500; cursor: pointer; }
.days-checkboxes input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; }

.conflict-box { background: #fff3dc; border-left: 4px solid #d9860a; border-radius: 10px; padding: 12px 16px; margin-bottom: 14px; font-size: 14px; }
.conflict-box ul { margin: 6px 0 0 16px; }
.conflict-box li { margin-bottom: 4px; color: #7a4a00; }

.form-error { color: #e03c3c; font-size: 14px; background: #fff0f0; padding: 10px 12px; border-radius: 8px; border-left: 3px solid #e03c3c; margin-bottom: 12px; }

.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
.btn-cancel { background: #f3f0ff; color: var(--brand-purple); border: none; border-radius: 10px; padding: 10px 20px; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn-save { background: var(--brand-orange); color: #fff; border: none; border-radius: 10px; padding: 10px 24px; font-size: 15px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-danger { background: #e03c3c; color: #fff; border: none; border-radius: 10px; padding: 10px 24px; font-size: 15px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
