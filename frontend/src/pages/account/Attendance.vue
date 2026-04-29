<template>
  <div class="attendance-page">
    <h1>Посещаемость</h1>

    <!-- ══════════════════════════════════════
         РЕЖИМ СТУДЕНТА — своя посещаемость
    ══════════════════════════════════════ -->
    <template v-if="auth.isStudent">
      <div v-if="loading" class="skeleton-list">
        <div class="skeleton-card" v-for="n in 5" :key="n"></div>
      </div>

      <template v-else-if="records.length">
        <div class="stats-bar">
          <div class="stat" v-for="s in statCards" :key="s.label">
            <span class="stat-value" :style="{ color: s.color }">{{ s.value }}</span>
            <span class="stat-label">{{ s.label }}</span>
          </div>
          <div class="stat">
            <span class="stat-value" style="color: var(--brand-orange)">{{ attendanceRate }}%</span>
            <span class="stat-label">Посещаемость</span>
          </div>
        </div>

        <div class="progress-wrap">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: attendanceRate + '%' }"></div>
          </div>
          <span class="progress-label">{{ attendanceRate }}% занятий посещено</span>
        </div>

        <div class="filter-row">
          <button
            v-for="f in filters" :key="f.key"
            class="filter-btn" :class="{ active: activeFilter === f.key }"
            @click="activeFilter = f.key"
          >{{ f.label }} <span class="filter-count">{{ f.count }}</span></button>
        </div>

        <div class="records-list">
          <div
            class="record-card" v-for="r in filteredRecords" :key="r.id"
            :class="'status-' + r.status"
          >
            <div class="record-status-dot"></div>
            <div class="record-info">
              <span class="record-date">{{ formatDate(r.lesson_date) }}</span>
              <span v-if="r.note" class="record-note">{{ r.note }}</span>
            </div>
            <span class="record-badge">{{ statusLabel(r.status) }}</span>
          </div>
          <p v-if="!filteredRecords.length" class="no-filter">Нет записей с таким статусом</p>
        </div>
      </template>

      <div v-else class="no-records">
        <div class="no-records-icon no-icon"></div>
        <p>Записей о посещаемости пока нет.</p>
        <p class="no-records-hint">Они появятся здесь, когда преподаватель начнёт отмечать занятия.</p>
      </div>
    </template>

    <!-- ══════════════════════════════════════
         РЕЖИМ УЧИТЕЛЯ / АДМИНА
    ══════════════════════════════════════ -->
    <template v-else-if="auth.isStaff">
      <div class="report-filters">
        <div class="filter-field">
          <label>Филиал</label>
          <select v-model="rf.branch_id" @change="onBranchChange()">
            <option :value="null">-- Выберите филиал --</option>
            <option v-for="b in reportBranches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>

        <div class="filter-field">
          <label>Преподаватель</label>
          <select v-model="rf.teacher_id" @change="onTeacherChange()">
            <option :value="null">-- Выберите преподавателя --</option>
            <option v-for="t in reportTeachers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
          </select>
        </div>

        <div class="filter-field">
          <label>Группа</label>
          <select v-model="rf.group_id" @change="loadReport()" :disabled="!rf.teacher_id">
            <option :value="null">-- Выберите группу --</option>
            <option v-for="g in reportGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
          <span v-if="rf.teacher_id && reportGroups.length === 0" class="no-groups-hint">У преподавателя нет групп</span>
        </div>

        <div class="filter-field filter-dates">
          <label>Дата с</label>
          <input type="date" v-model="rf.date_from" @change="loadReport()" />
          <label>по</label>
          <input type="date" v-model="rf.date_to" @change="loadReport()" />
        </div>

        <div class="filter-field filter-check">
          <label>
            <input type="checkbox" v-model="rf.missed_consecutive" @change="loadReport()" />
            только пропустившие 2 занятия подряд
          </label>
        </div>

        <div class="filter-field filter-student">
          <label>Студент</label>
          <input type="text" v-model="rf.student_name" @input="loadReport()" placeholder="Поиск по имени..." />
          <button class="clear-btn" @click="clearFilters">ОЧИСТИТЬ</button>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════════════ -->
      <!-- ВКЛАДКА: Посещаемость ─────────────────────────────────────────────── -->
      <!-- ════════════════════════════════════════════════════════════════════ -->
      <template v-if="activeTab === 'attendance'">
        <div v-if="reportLoading" class="skeleton-list">
          <div class="skeleton-card" v-for="n in 6" :key="n"></div>
        </div>

        <div v-if="rf.group_id" class="matrix-wrap">
          <div class="matrix-title-row">
            <h3>Матрица посещаемости по группе</h3>
            <button class="add-date-btn" @click="addMatrixDate">+</button>
          </div>

          <div v-if="matrixLoading" class="loading-hint">Загрузка студентов и дат занятий...</div>
          <div v-else-if="!matrixStudents.length" class="empty-hint">В выбранной группе пока нет активных студентов.</div>
          <div v-else-if="!matrixLessons.length" class="empty-hint">Для выбранного периода нет дат занятий.</div>

          <div v-else class="matrix-table-wrap">
            <div class="matrix-table">
              <div class="matrix-header attendance-matrix-header" :style="matrixGridStyle">
                <div class="matrix-cell header-cell student-col">Студент</div>
                <div v-for="lesson in matrixLessons" :key="`${lesson.id}-${lesson.slot_date}`" class="matrix-cell header-cell lesson-col">
                  <div>{{ formatDateShort(lesson.slot_date) }}</div>
                  <div class="header-time">{{ formatTimeShort(lesson.time_start) }}</div>
                  <div v-if="lesson.is_custom_date" class="header-actions">
                    <button
                      class="header-icon-btn"
                      title="Редактировать дату"
                      @click.stop="editMatrixDate(lesson)"
                      :disabled="isColumnSaving(lesson.id, lesson.slot_date)"
                    >✎</button>
                    <button
                      class="header-icon-btn danger"
                      title="Удалить дату"
                      @click.stop="deleteMatrixDate(lesson)"
                      :disabled="isColumnSaving(lesson.id, lesson.slot_date)"
                    >×</button>
                  </div>
                </div>
              </div>

              <div v-for="student in filteredMatrixStudents" :key="student.id" class="matrix-row attendance-matrix-row" :style="matrixGridStyle">
                <div class="matrix-cell student-cell student-col">{{ student.student_name }}</div>
                <button
                  v-for="lesson in matrixLessons"
                  :key="`${student.id}-${lesson.id}-${lesson.slot_date}`"
                  class="matrix-cell status-cell lesson-col"
                  :class="statusClass(getMatrixStatus(student.id, lesson.id, lesson.slot_date))"
                  @click="toggleAttendanceCell(student.id, lesson.id, lesson.slot_date)"
                  :disabled="isSavingCell(student.id, lesson.id, lesson.slot_date)"
                >
                  <span v-if="isSavingCell(student.id, lesson.id, lesson.slot_date)">...</span>
                  <span v-else>{{ getStatusSymbol(getMatrixStatus(student.id, lesson.id, lesson.slot_date)) }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="reportSearched" class="no-records">
          <div class="no-records-icon">🔍</div>
          <p>Записей по выбранным фильтрам не найдено.</p>
        </div>

        <div v-else-if="!reportSearched" class="no-records">
          <div class="no-records-icon no-icon"></div>
          <p class="empty-hint">Выберите филиал, преподавателя и/или группу, чтобы увидеть посещаемость ниже.</p>
        </div>
      </template>

      <!-- ════════════════════════════════════════════════════════════════════ -->
      <!-- ВКЛАДКА: Материал урока ───────────────────────────────────────────── -->
      <!-- ════════════════════════════════════════════════════════════════════ -->
      <template v-else-if="activeTab === 'materials'">
        <div v-if="materialsLoading" class="skeleton-list">
          <div class="skeleton-card" v-for="n in 6" :key="n"></div>
        </div>
        <template v-else>
        <div v-if="rf.group_id" class="materials-toolbar">
          <h3 class="materials-group-title">Группа {{ selectedGroupName }}</h3>
        </div>

        <div v-if="sortedMaterialSlots.length" class="materials-table-wrap">
          <div class="materials-table-head">
            <div class="materials-head-date">Дата занятия</div>
            <div class="materials-head-topic">Тема занятия</div>
            <div class="materials-head-action"></div>
          </div>

          <div v-for="slot in sortedMaterialSlots" :key="`${slot.id}-${slot.slot_date}`" class="materials-row">
            <div class="materials-date-cell">{{ formatDateTimeMaterial(slot.slot_date, slot.time_start) }}</div>
            <div class="materials-topic-cell">
              <span v-if="isMaterialSaving(slot.id)">...</span>
              <span v-else>{{ slot.topic || 'Тема не заполнена' }}</span>
            </div>
            <div class="materials-action-cell">
              <button class="header-icon-btn" title="Редактировать тему" @click.stop="editMaterialTopic(slot)" :disabled="isMaterialSaving(slot.id)">✎</button>
            </div>
          </div>
        </div>
        <div v-else class="no-records">
          <div class="no-records-icon">📖</div>
          <p>Материалы уроков для выбранного периода не найдены.</p>
        </div>
        </template>
      </template>

      <!-- ════════════════════════════════════════════════════════════════════ -->
      <!-- ВКЛАДКА: Домашнее задание ─────────────────────────────────────────── -->
      <!-- ════════════════════════════════════════════════════════════════════ -->
      <template v-else-if="activeTab === 'homework'">
        <div v-if="homeworkLoading" class="skeleton-list">
          <div class="skeleton-card" v-for="n in 6" :key="n"></div>
        </div>
        <div v-else-if="homeworks.length" class="homework-list">
          <div v-for="h in homeworks" :key="h.id" class="homework-card">
            <div class="homework-date">{{ formatDate(h.created_at) }}</div>
            <div class="homework-content">
              <div class="homework-title">{{ h.description }}</div>
              <div v-if="h.deadline" class="homework-deadline">Срок: {{ formatDate(h.deadline) }}</div>
            </div>
          </div>
        </div>
        <div v-else class="no-records">
          <div class="no-records-icon">📝</div>
          <p>Домашние задания для выбранного периода не найдены.</p>
        </div>
      </template>

      <!-- ════════════════════════════════════════════════════════════════════ -->
      <!-- ВКЛАДКА: Оплата обучения ──────────────────────────────────────────── -->
      <!-- ════════════════════════════════════════════════════════════════════ -->
      <template v-else-if="activeTab === 'payments'">
        <div v-if="paymentsLoading" class="loading-hint">Загрузка...</div>
        <div v-else-if="paymentStudents.length" class="matrix-table-wrap">
          <div class="matrix-table">
            <div class="matrix-header">
              <div class="matrix-cell header-cell student-col">Студент</div>
              <div v-for="month in paymentMonths" :key="month" class="matrix-cell header-cell month-col">
                {{ month }}
              </div>
            </div>
            <div v-for="student in paymentStudents" :key="student.id" class="matrix-row">
              <div class="matrix-cell student-cell student-col">{{ student.student_name }}</div>
              <button
                v-for="month in paymentMonths"
                :key="`${student.id}-${month}`"
                class="matrix-cell payment-cell month-col"
                :class="getPaymentStatusClass(student.id, month)"
                @click="togglePaymentStatus(student.id, month)"
              >
                {{ getPaymentStatusIcon(student.id, month) }}
              </button>
            </div>
          </div>
        </div>
        <div v-else class="no-records">
          <div class="no-records-icon">💳</div>
          <p>Данные об оплате не найдены.</p>
        </div>
      </template>

      <!-- ════════════════════════════════════════════════════════════════════ -->
      <!-- ВКЛАДКА: Промежуточная успеваемость ───────────────────────────────── -->
      <!-- ════════════════════════════════════════════════════════════════════ -->
      <template v-else-if="activeTab === 'grades'">
        <div v-if="gradesLoading" class="loading-hint">Загрузка...</div>
        <div v-else-if="gradeStudents.length && gradeLessons.length" class="matrix-table-wrap">
          <div class="matrix-table">
            <div class="matrix-header">
              <div class="matrix-cell header-cell student-col">Студент</div>
              <div v-for="lesson in gradeLessons" :key="`${lesson.id}-${lesson.slot_date}`" class="matrix-cell header-cell lesson-col">
                <div>{{ formatDateShort(lesson.slot_date) }}</div>
                <div class="header-time">{{ formatTimeShort(lesson.time_start) }}</div>
              </div>
            </div>
            <div v-for="student in gradeStudents" :key="student.id" class="matrix-row">
              <div class="matrix-cell student-cell student-col">{{ student.student_name }}</div>
              <div
                v-for="lesson in gradeLessons"
                :key="`${student.id}-${lesson.id}-${lesson.slot_date}`"
                class="matrix-cell grade-cell lesson-col"
              >
                {{ getGrade(student.id, lesson.id, lesson.slot_date) || '—' }}
              </div>
            </div>
          </div>
        </div>
        <div v-else class="no-records">
          <div class="no-records-icon">⭐</div>
          <p>Данные об оценках не найдены.</p>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// ── УТИЛИТЫ ──────────────────────────────────────────────────────────────────
function formatDate(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: '2-digit', month: 'long', year: 'numeric', weekday: 'short',
  })
}
function statusLabel(s: string) {
  return ({ present: 'Был', absent: 'Не был', late: 'Опоздал', excused: 'Уваж. прич.' } as any)[s] ?? s
}
const todayStr = new Date().toISOString().slice(0, 10)
const defaultDateFrom = new Date(Date.now() - 60 * 24 * 3600 * 1000).toISOString().slice(0, 10)

// ── СТУДЕНТ: своя посещаемость ────────────────────────────────────────────────
const loading      = ref(true)
const records      = ref<any[]>([])
const activeFilter = ref('all')

const counts = computed(() => ({
  present: records.value.filter(r => r.status === 'present').length,
  absent:  records.value.filter(r => r.status === 'absent').length,
  late:    records.value.filter(r => r.status === 'late').length,
  excused: records.value.filter(r => r.status === 'excused').length,
}))
const attendanceRate = computed(() => {
  const t = records.value.length
  if (!t) return 0
  return Math.round((counts.value.present + counts.value.late) / t * 100)
})
const statCards = computed(() => [
  { label: 'Был на занятии',   value: counts.value.present, color: '#22a55b' },
  { label: 'Отсутствовал',     value: counts.value.absent,  color: '#e03c3c' },
  { label: 'Опоздал',         value: counts.value.late,    color: '#d9860a' },
  { label: 'Уважит. причина', value: counts.value.excused, color: '#5b8dd9' },
])
const filters = computed(() => [
  { key: 'all',     label: 'Все',            count: records.value.length },
  { key: 'present', label: 'Присутствовал', count: counts.value.present },
  { key: 'absent',  label: 'Отсутствовал',  count: counts.value.absent  },
  { key: 'late',    label: 'Опоздал',         count: counts.value.late    },
  { key: 'excused', label: 'Уваж. прич.',   count: counts.value.excused },
])
const filteredRecords = computed(() =>
  activeFilter.value === 'all'
    ? records.value
    : records.value.filter(r => r.status === activeFilter.value)
)

// ── ВКЛАДКИ ──────────────────────────────────────────────────────────────────
const activeTab = ref('attendance')

// ── ОТЧЁТ: фильтрованный просмотр ────────────────────────────────────────────
const rf = reactive({
  branch_id:         null as number | null,
  teacher_id:        null as number | null,
  group_id:          null as number | null,
  date_from:         defaultDateFrom,
  date_to:           todayStr,
  student_name:      '',
  missed_consecutive: false,
})

const reportBranches = ref<any[]>([])
const reportTeachers = ref<any[]>([])
const reportGroups   = ref<any[]>([])
const reportRows     = ref<any[]>([])
const reportLoading  = ref(false)
const reportSearched = ref(false)

const matrixLoading = ref(false)
const matrixStudents = ref<any[]>([])
const matrixLessons = ref<any[]>([])
const matrixRecords = ref<Record<string, string>>({})
const matrixSaving = ref<Record<string, boolean>>({})
const matrixColumnSaving = ref<Record<string, boolean>>({})

// ── ДЛЯ ВСЕХ ВКЛАДОК ──────────────────────────────────────────────────────
const materialsLoading = ref(false)
const materialSlots = ref<any[]>([])
const materialSaving = ref<Record<string, boolean>>({})
const materialScheduleLines = ref<string[]>([])
const materialTeacherNames = ref<string[]>([])

const homeworkLoading = ref(false)
const homeworks = ref<any[]>([])

const paymentsLoading = ref(false)
const paymentStudents = ref<any[]>([])
const paymentMonths = ref<any[]>([])
const paymentRecords = ref<Record<string, string>>({})

const gradesLoading = ref(false)
const gradeStudents = ref<any[]>([])
const gradeLessons = ref<any[]>([])
const gradeRecords = ref<Record<string, string>>({})

const filteredMatrixStudents = computed(() => {
  const q = rf.student_name.trim().toLowerCase()
  let students = matrixStudents.value

  if (rf.missed_consecutive) {
    const allowedIds = new Set(
      reportRows.value
        .map((r) => Number(r.student_group_id))
        .filter((id) => Number.isFinite(id))
    )
    students = students.filter((s) => allowedIds.has(Number(s.id)))
  }

  if (!q) return students
  return students.filter((s) => String(s.student_name || '').toLowerCase().includes(q))
})

const selectedGroupName = computed(() => {
  const gid = Number(rf.group_id)
  if (!Number.isFinite(gid)) return '—'
  const grp = reportGroups.value.find((g: any) => Number(g.id) === gid)
  return grp?.name || `#${gid}`
})

const sortedMaterialSlots = computed(() => {
  return [...materialSlots.value].sort((a: any, b: any) => {
    const ad = `${a.slot_date || ''}T${a.time_start || '00:00:00'}`
    const bd = `${b.slot_date || ''}T${b.time_start || '00:00:00'}`
    return new Date(bd).getTime() - new Date(ad).getTime()
  })
})

const matrixGridStyle = computed(() => ({
  gridTemplateColumns: `280px repeat(${matrixLessons.value.length}, 72px)`,
}))

// Slot key includes the date to distinguish recurring-lesson occurrences
function matrixSlotKey(studentGroupId: number, lessonId: number, slotDate: string) {
  return `${studentGroupId}:${lessonId}:${slotDate}`
}

function getMatrixStatus(studentGroupId: number, lessonId: number, slotDate: string) {
  return matrixRecords.value[matrixSlotKey(studentGroupId, lessonId, slotDate)] || null
}

function isSavingCell(studentGroupId: number, lessonId: number, slotDate: string) {
  return !!matrixSaving.value[matrixSlotKey(studentGroupId, lessonId, slotDate)]
}

function matrixColumnKey(lessonId: number, slotDate: string) {
  return `${lessonId}:${slotDate}`
}

function isColumnSaving(lessonId: number, slotDate: string) {
  return !!matrixColumnSaving.value[matrixColumnKey(lessonId, slotDate)]
}

function isMaterialSaving(lessonId: number) {
  return !!materialSaving.value[String(lessonId)]
}

async function refreshCurrentMatrixView() {
  if (activeTab.value === 'materials') {
    await loadMaterialsMatrix()
    return
  }
  await loadGroupMatrix()
}

function getStatusSymbol(status: string | null) {
  if (!status) return '○'
  return { present: '+', absent: '-', late: 'Л', excused: 'У' }[status] || '○'
}

function statusClass(status: string | null) {
  if (!status) return 'mstatus-empty'
  return `mstatus-${status}`
}

function formatDateShort(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
}

function formatTimeShort(timeRaw: string) {
  if (!timeRaw) return ''
  return String(timeRaw).slice(0, 5)
}

function formatDateTimeMaterial(slotDate: string, timeRaw: string) {
  if (!slotDate) return ''
  const datePart = new Date(slotDate).toLocaleDateString('ru-RU')
  const timePart = formatTimeShort(timeRaw)
  return timePart ? `${datePart} ${timePart}` : datePart
}

function formatDayShort(dayRaw: any) {
  const day = String(dayRaw || '').toLowerCase()
  const map: Record<string, string> = {
    monday: 'Пн',
    tuesday: 'Вт',
    wednesday: 'Ср',
    thursday: 'Чт',
    friday: 'Пт',
    saturday: 'Сб',
    sunday: 'Вс',
  }
  return map[day] || dayRaw || ''
}

function daySortKey(dayRaw: any) {
  const day = String(dayRaw || '').toLowerCase()
  const order: Record<string, number> = {
    monday: 1,
    tuesday: 2,
    wednesday: 3,
    thursday: 4,
    friday: 5,
    saturday: 6,
    sunday: 7,
  }
  return order[day] || 99
}

async function loadGroupMatrix() {
  if (!rf.group_id) {
    matrixStudents.value = []
    matrixLessons.value = []
    matrixRecords.value = {}
    return
  }

  matrixLoading.value = true
  try {
    const params: any = {}
    if (rf.date_from) params.date_from = rf.date_from
    if (rf.date_to) params.date_to = rf.date_to

    const res = await http.get(`/attendance/group/${rf.group_id}/matrix`, { params })
    const data = res.data || {}
    matrixStudents.value = Array.isArray(data.students) ? data.students : []
    matrixLessons.value = Array.isArray(data.lessons) ? data.lessons : []

    const nextMap: Record<string, string> = {}
    for (const rec of (Array.isArray(data.records) ? data.records : [])) {
      const key = matrixSlotKey(rec.student_group_id, rec.lesson_id, rec.lesson_date || '')
      nextMap[key] = rec.status
    }
    matrixRecords.value = nextMap
  } catch {
    matrixStudents.value = []
    matrixLessons.value = []
    matrixRecords.value = {}
  } finally {
    matrixLoading.value = false
  }
}

async function toggleAttendanceCell(studentGroupId: number, lessonId: number, slotDate: string) {
  const current = getMatrixStatus(studentGroupId, lessonId, slotDate)
  const nextStatus = current === 'present' ? 'absent' : 'present'
  const key = matrixSlotKey(studentGroupId, lessonId, slotDate)

  matrixSaving.value = { ...matrixSaving.value, [key]: true }

  try {
    await http.put('/attendance/upsert', {
      lesson_id: lessonId,
      student_group_id: studentGroupId,
      status: nextStatus,
      note: null,
      lesson_date: slotDate,
    })
    matrixRecords.value = { ...matrixRecords.value, [key]: nextStatus }
  } catch {
    // Не меняем локальное состояние при ошибке сохранения.
  } finally {
    const nextSaving = { ...matrixSaving.value }
    delete nextSaving[key]
    matrixSaving.value = nextSaving
  }
}

async function addMatrixDate() {
  if (!rf.group_id) return

  const suggestedDate = rf.date_to || new Date().toISOString().slice(0, 10)
  const raw = window.prompt('Введите дату занятия в формате YYYY-MM-DD', suggestedDate)
  if (!raw) return

  const newDate = raw.trim()
  if (!/^\d{4}-\d{2}-\d{2}$/.test(newDate)) {
    window.alert('Неверный формат даты. Используйте YYYY-MM-DD')
    return
  }

  try {
    await http.post(`/attendance/group/${rf.group_id}/matrix/add-date`, {
      lesson_date: newDate,
    })

    if (!rf.date_from || newDate < rf.date_from) rf.date_from = newDate
    if (!rf.date_to || newDate > rf.date_to) rf.date_to = newDate

    await refreshCurrentMatrixView()
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    window.alert(typeof detail === 'string' ? detail : 'Не удалось добавить дату')
  }
}

async function editMatrixDate(lesson: any) {
  if (!rf.group_id) return
  const currentDate = String(lesson.slot_date || '')
  const raw = window.prompt('Новая дата занятия (YYYY-MM-DD)', currentDate)
  if (!raw) return
  const nextDate = raw.trim()
  if (!/^\d{4}-\d{2}-\d{2}$/.test(nextDate)) {
    window.alert('Неверный формат даты. Используйте YYYY-MM-DD')
    return
  }
  if (nextDate === currentDate) return

  const colKey = matrixColumnKey(Number(lesson.id), currentDate)
  matrixColumnSaving.value = { ...matrixColumnSaving.value, [colKey]: true }
  try {
    await http.put(`/attendance/group/${rf.group_id}/matrix/update-date`, {
      lesson_id: Number(lesson.id),
      old_date: currentDate,
      new_date: nextDate,
    })

    if (!rf.date_from || nextDate < rf.date_from) rf.date_from = nextDate
    if (!rf.date_to || nextDate > rf.date_to) rf.date_to = nextDate

    await refreshCurrentMatrixView()
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    window.alert(typeof detail === 'string' ? detail : 'Не удалось изменить дату')
  } finally {
    const next = { ...matrixColumnSaving.value }
    delete next[colKey]
    matrixColumnSaving.value = next
  }
}

async function deleteMatrixDate(lesson: any) {
  if (!rf.group_id) return
  const slotDate = String(lesson.slot_date || '')
  if (!window.confirm(`Удалить дату ${slotDate}?`)) return

  const colKey = matrixColumnKey(Number(lesson.id), slotDate)
  matrixColumnSaving.value = { ...matrixColumnSaving.value, [colKey]: true }
  try {
    await http.delete(`/attendance/group/${rf.group_id}/matrix/delete-date`, {
      data: {
        lesson_id: Number(lesson.id),
        slot_date: slotDate,
      },
    })

    await refreshCurrentMatrixView()
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    window.alert(typeof detail === 'string' ? detail : 'Не удалось удалить дату')
  } finally {
    const next = { ...matrixColumnSaving.value }
    delete next[colKey]
    matrixColumnSaving.value = next
  }
}

async function loadReportBranches() {
  try { const r = await http.get('/branches/'); reportBranches.value = r.data }
  catch { reportBranches.value = [] }
}

async function loadReportTeachers() {
  try {
    const params: any = {}
    if (rf.branch_id) params.branch_id = rf.branch_id
    const r = await http.get('/teachers/', { params })
    reportTeachers.value = r.data.map((u: any) => ({
      id: u.id,
      full_name: u.full_name,
    }))
  } catch { reportTeachers.value = [] }
}

async function loadReportGroups() {
  try {
    const params: any = {}
    if (rf.branch_id)  params.branch_id  = rf.branch_id
    if (rf.teacher_id) params.teacher_id = rf.teacher_id
    const r = await http.get('/groups', { params })
    reportGroups.value = r.data
    // Если для выбранного преподавателя только одна группа — выбираем её автоматически
    if (rf.teacher_id && r.data.length === 1 && !rf.group_id) {
      rf.group_id = r.data[0].id
      loadReport()
    }
  } catch { reportGroups.value = [] }
}

function clearFilters() {
  rf.branch_id = null
  rf.teacher_id = null
  rf.group_id = null
  rf.date_from = defaultDateFrom
  rf.date_to = todayStr
  rf.student_name = ''
  rf.missed_consecutive = false
  reportTeachers.value = []
  reportGroups.value = []
  loadReportBranches()
  loadReport()
}

function onBranchChange() {
  rf.teacher_id = null
  rf.group_id = null
  reportTeachers.value = []
  reportGroups.value = []
  loadReportTeachers()
  loadReportGroups()
  loadReport()
}

function onTeacherChange() {
  applyBranchByTeacher().then(() => {
    rf.group_id = null
    reportGroups.value = []
    loadReportGroups()
    loadReport()
  })
}

async function applyBranchByTeacher() {
  if (!rf.teacher_id) return
  try {
    const res = await http.get('/schedule', { params: { teacher_id: rf.teacher_id } })
    const lessons = Array.isArray(res.data) ? res.data : []
    const teacherBranchIds = [...new Set(
      lessons
        .map((l: any) => l.branch_id)
        .filter((id: any) => typeof id === 'number' && Number.isFinite(id))
    )]

    if (!teacherBranchIds.length) return

    // Если текущий филиал не относится к выбранному преподавателю, подставляем первый подходящий.
    if (!rf.branch_id || !teacherBranchIds.includes(rf.branch_id)) {
      rf.branch_id = teacherBranchIds[0]
      await loadReportTeachers()
    }
  } catch {
    // Не блокируем UX, если расписание недоступно.
  }
}

async function loadReport() {
  reportLoading.value  = true
  reportSearched.value = false
  try {
    const params: any = {}
    if (rf.branch_id)           params.branch_id           = rf.branch_id
    if (rf.teacher_id)          params.teacher_id          = rf.teacher_id
    if (rf.group_id)            params.group_id            = rf.group_id
    if (rf.date_from)           params.date_from           = rf.date_from
    if (rf.date_to)             params.date_to             = rf.date_to
    if (rf.student_name.trim()) params.student_name        = rf.student_name.trim()
    if (rf.missed_consecutive)  params.missed_consecutive  = true
    const r = await http.get('/attendance/report', { params })
    reportRows.value = r.data
  } catch {
    reportRows.value = []
  } finally {
    reportLoading.value = false
    reportSearched.value = true
    await loadGroupMatrix()
  }
}

// ── ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ НОВЫХ ВКЛАДОК ───────────────────────────────
async function loadMaterialsMatrix() {
  if (!rf.group_id) {
    materialSlots.value = []
    materialScheduleLines.value = []
    materialTeacherNames.value = []
    return
  }
  materialsLoading.value = true
  try {
    const scheduleParams: any = { group_id: rf.group_id }
    if (rf.teacher_id) scheduleParams.teacher_id = rf.teacher_id

    const res = await http.get('/attendance/group/' + rf.group_id + '/materials-matrix')
    const slots = Array.isArray(res.data?.slots) ? res.data.slots : []
    materialSlots.value = slots

    const schRes = await http.get('/schedule', { params: scheduleParams })
    const lessons = Array.isArray(schRes.data) ? schRes.data : []
    const sortedLessons = [...lessons].sort((a: any, b: any) => {
      const dk = daySortKey(a.day_of_week) - daySortKey(b.day_of_week)
      if (dk !== 0) return dk
      return String(a.time_start || '').localeCompare(String(b.time_start || ''))
    })

    const lineSet = new Set<string>()
    for (const l of sortedLessons) {
      const dayShort = formatDayShort(l.day_of_week)
      const time = formatTimeShort(l.time_start)
      if (dayShort && time) lineSet.add(`${dayShort}: ${time}`)
    }
    materialScheduleLines.value = [...lineSet]

    const teacherSet = new Set<string>()
    for (const l of lessons) {
      if (l.teacher_name) teacherSet.add(String(l.teacher_name))
    }
    if (teacherSet.size === 0 && rf.teacher_id) {
      const t = reportTeachers.value.find((x: any) => Number(x.id) === Number(rf.teacher_id))
      if (t?.full_name) teacherSet.add(String(t.full_name))
    }
    materialTeacherNames.value = [...teacherSet]
  } catch {
    materialSlots.value = []
    materialScheduleLines.value = []
    materialTeacherNames.value = []
  } finally {
    materialsLoading.value = false
  }
}

async function editMaterialTopic(slot: any) {
  if (!rf.group_id) return
  const current = String(slot.topic || '')
  const next = window.prompt('Тема занятия', current)
  if (next === null) return

  const lessonId = Number(slot.id)
  const key = String(lessonId)
  materialSaving.value = { ...materialSaving.value, [key]: true }
  try {
    await http.put(`/attendance/group/${rf.group_id}/materials/update-topic`, {
      lesson_id: lessonId,
      topic: next,
    })
    await loadMaterialsMatrix()
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    window.alert(typeof detail === 'string' ? detail : 'Не удалось сохранить тему')
  } finally {
    const nextSaving = { ...materialSaving.value }
    delete nextSaving[key]
    materialSaving.value = nextSaving
  }
}

async function loadHomework() {
  if (!rf.group_id) {
    homeworks.value = []
    return
  }
  homeworkLoading.value = true
  try {
    const params: any = {}
    if (rf.date_from) params.date_from = rf.date_from
    if (rf.date_to) params.date_to = rf.date_to
    const res = await http.get('/attendance/group/' + rf.group_id + '/homeworks', { params })
    homeworks.value = res.data || []
  } catch {
    homeworks.value = []
  } finally {
    homeworkLoading.value = false
  }
}

async function loadPayments() {
  if (!rf.group_id) {
    paymentStudents.value = []
    paymentMonths.value = []
    paymentRecords.value = {}
    return
  }
  paymentsLoading.value = true
  try {
    const params: any = {}
    if (rf.date_from) params.date_from = rf.date_from
    if (rf.date_to) params.date_to = rf.date_to
    const res = await http.get('/attendance/group/' + rf.group_id + '/payments', { params })
    paymentStudents.value = res.data.students || []
    paymentMonths.value = res.data.months || []
    paymentRecords.value = res.data.records || {}
  } catch {
    paymentStudents.value = []
    paymentMonths.value = []
    paymentRecords.value = {}
  } finally {
    paymentsLoading.value = false
  }
}

async function loadGrades() {
  if (!rf.group_id) {
    gradeStudents.value = []
    gradeLessons.value = []
    gradeRecords.value = {}
    return
  }
  gradesLoading.value = true
  try {
    const params: any = {}
    if (rf.date_from) params.date_from = rf.date_from
    if (rf.date_to) params.date_to = rf.date_to
    const res = await http.get('/attendance/group/' + rf.group_id + '/grades', { params })
    gradeStudents.value = res.data.students || []
    gradeLessons.value = res.data.lessons || []
    gradeRecords.value = res.data.records || {}
  } catch {
    gradeStudents.value = []
    gradeLessons.value = []
    gradeRecords.value = {}
  } finally {
    gradesLoading.value = false
  }
}

function getPaymentStatusIcon(studentId: number, month: string): string {
  const status = paymentRecords.value[`${studentId}:${month}`]
  return status === 'paid' ? '✓' : '✗'
}

function getPaymentStatusClass(studentId: number, month: string): string {
  const status = paymentRecords.value[`${studentId}:${month}`]
  return status === 'paid' ? 'payment-paid' : 'payment-unpaid'
}

function togglePaymentStatus(studentId: number, month: string) {
  const key = `${studentId}:${month}`
  const current = paymentRecords.value[key]
  const next = current === 'paid' ? 'unpaid' : 'paid'
  paymentRecords.value = { ...paymentRecords.value, [key]: next }
}

function getGrade(studentId: number, lessonId: number, slotDate: string): string {
  return gradeRecords.value[`${studentId}:${lessonId}:${slotDate}`] || ''
}

// ── INIT ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  if (auth.isStudent) {
    try { const res = await http.get('/attendance/my'); records.value = res.data }
    catch { records.value = [] }
    finally { loading.value = false }
  } else if (auth.isStaff) {
    await Promise.all([
      loadReportBranches(),
      loadReportTeachers(),
      loadReportGroups(),
    ])
  }
})

// ── WATCHERS ──────────────────────────────────────────────────────────────────
watch(() => activeTab.value, (newTab) => {
  if (newTab === 'materials') loadMaterialsMatrix()
  else if (newTab === 'homework') loadHomework()
  else if (newTab === 'payments') loadPayments()
  else if (newTab === 'grades') loadGrades()
})

watch(() => rf.group_id, () => {
  if (activeTab.value === 'materials') loadMaterialsMatrix()
  else if (activeTab.value === 'homework') loadHomework()
  else if (activeTab.value === 'payments') loadPayments()
  else if (activeTab.value === 'grades') loadGrades()
})

watch(() => [rf.date_from, rf.date_to], () => {
  if (activeTab.value === 'materials') loadMaterialsMatrix()
  else if (activeTab.value === 'homework') loadHomework()
  else if (activeTab.value === 'payments') loadPayments()
  else if (activeTab.value === 'grades') loadGrades()
})
</script>

<style scoped>
.attendance-page h1 {
  font-size: 28px; font-weight: 700;
  color: var(--brand-purple); margin-bottom: 24px;
}

/* ── Вкладки ──────────────────────────────────────────────── */
.tabs-wrap {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  border-bottom: 2px solid #ffe3cf;
}

.tab-btn {
  padding: 10px 18px;
  border: none;
  background: transparent;
  color: #888;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--brand-orange);
}

.tab-btn.active {
  color: var(--brand-orange);
  border-bottom-color: var(--brand-orange);
}

/* ── Фильтры отчёта ───────────────────────────────────────── */
.report-filters {
  background: #fff7f0;
  border: 1px solid #ffe3cf;
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 14px 20px;
  align-items: flex-end;
  margin-bottom: 16px;
}
.filter-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 180px;
}
.filter-field label {
  font-size: 12px; font-weight: 700;
  color: var(--brand-orange); text-transform: uppercase; letter-spacing: .05em;
}
.filter-field select,
.filter-field input[type="date"],
.filter-field input[type="text"] {
  padding: 8px 12px; border-radius: 8px;
  border: 1.5px solid #ffe3cf; font-size: 14px;
  font-family: inherit; background: #fff; outline: none;
}
.filter-field select:focus,
.filter-field input:focus { border-color: var(--brand-orange); }

.filter-dates {
  flex-direction: row;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  min-width: unset;
}
.filter-dates label { text-transform: none; font-size: 13px; font-weight: 600; color: #555; }

.filter-check {
  flex-direction: row;
  align-items: center;
  min-width: unset;
}
.filter-check label {
  display: flex; align-items: center; gap: 7px;
  font-size: 13px; font-weight: 500; color: #444;
  text-transform: none; letter-spacing: 0; cursor: pointer;
}

.filter-student {
  flex-direction: row;
  align-items: flex-end;
  gap: 8px;
  flex: 1;
  min-width: 240px;
}
.filter-student label { display: none; }
.filter-student input { flex: 1; }
.clear-btn {
  background: none; border: none; color: var(--brand-orange);
  font-size: 13px; font-weight: 700; cursor: pointer; white-space: nowrap;
  padding: 8px 4px;
}
.clear-btn:hover { text-decoration: underline; }

.no-groups-hint {
  font-size: 12px; color: #e03c3c; margin-top: 4px; font-style: italic;
}

.report-actions { display: flex; justify-content: flex-end; margin-bottom: 16px; }

/* ── Таблица отчёта ───────────────────────────────────────── */
.report-table-wrap { overflow-x: auto; border-radius: 12px; border: 1px solid #ffe3cf; }
.report-table {
  width: 100%; border-collapse: collapse;
  font-size: 14px;
}
.report-table thead tr {
  background: #fff0e4;
}
.report-table th {
  padding: 11px 14px; text-align: left;
  font-size: 12px; font-weight: 700; color: var(--brand-purple);
  text-transform: uppercase; letter-spacing: .05em;
}
.report-table td {
  padding: 10px 14px; border-top: 1px solid #ffe3cf;
}
.row-absent  td { background: #fff5f5; }
.row-late    td { background: #fffaf0; }
.row-excused td { background: #f0f5ff; }
.note-cell { color: #888; font-size: 13px; }

/* значки статуса в таблице */
.record-badge {
  font-size: 12px; font-weight: 700;
  padding: 3px 10px; border-radius: 999px;
}
.status-present .record-badge, .record-badge.status-present { background: #e6f9ef; color: #22a55b; }
.status-absent  .record-badge, .record-badge.status-absent  { background: #fdeaea; color: #e03c3c; }
.status-late    .record-badge, .record-badge.status-late    { background: #fff3dc; color: #d9860a; }
.status-excused .record-badge, .record-badge.status-excused { background: #e8f0fc; color: #5b8dd9; }

/* ── Статистика студента ──────────────────────────────────── */
.stats-bar { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
.stat {
  background: #fff7f0; border-radius: 12px; padding: 14px 20px;
  display: flex; flex-direction: column; gap: 4px;
  border: 1.5px solid #ffe3cf; min-width: 110px; text-align: center;
}
.stat-value { font-size: 28px; font-weight: 700; }
.stat-label { font-size: 12px; color: #888; }

.progress-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.progress-bar  { flex: 1; height: 10px; background: #f0ece8; border-radius: 999px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--brand-orange); border-radius: 999px; transition: width .6s ease; }
.progress-label { font-size: 14px; color: #888; white-space: nowrap; }

.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.filter-btn {
  padding: 6px 14px; border-radius: 999px; border: 2px solid #ffe3cf;
  background: #fff; font-size: 13px; font-weight: 600; color: var(--brand-purple);
  cursor: pointer; transition: all .18s; display: flex; align-items: center; gap: 6px;
}
.filter-btn:hover  { background: #ffe3cf; }
.filter-btn.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }
.filter-count { background: rgba(255,255,255,.35); border-radius: 999px; padding: 1px 7px; font-size: 12px; }

.records-list { display: flex; flex-direction: column; gap: 10px; }
.record-card {
  display: flex; align-items: center; gap: 14px;
  background: #fff7f0; border-radius: 12px;
  padding: 14px 18px; border-left: 5px solid #ddd;
}
.status-present { border-left-color: #22a55b; }
.status-absent  { border-left-color: #e03c3c; background: #fff5f5; }
.status-late    { border-left-color: #d9860a; background: #fffaf0; }
.status-excused { border-left-color: #5b8dd9; background: #f0f5ff; }
.record-status-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.status-present .record-status-dot { background: #22a55b; }
.status-absent  .record-status-dot { background: #e03c3c; }
.status-late    .record-status-dot { background: #d9860a; }
.status-excused .record-status-dot { background: #5b8dd9; }
.record-info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.record-date  { font-size: 15px; font-weight: 600; color: #333; }
.record-note  { font-size: 13px; color: #888; }
.no-filter { text-align: center; color: #bbb; padding: 20px; }

/* ── Пустое состояние ─────────────────────────────────────── */
.no-records {
  text-align: center; padding: 40px;
  background: #fff7f0; border-radius: 14px; color: #888;
}
.no-records-icon { font-size: 48px; margin-bottom: 12px; }
.no-records-icon.no-icon { display: none; }
.no-records p { font-size: 16px; margin-bottom: 6px; }
.no-records-hint { font-size: 14px; color: #bbb; }

/* ── Режим учителя: секции ────────────────────────────────── */
.staff-section {
  background: #fff7f0; border-radius: 14px;
  padding: 20px 22px; margin-bottom: 18px;
  border: 1px solid #ffe3cf;
}
.step-label {
  font-size: 12px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .07em; color: var(--brand-orange); margin-bottom: 14px;
}
.loading-hint { font-size: 14px; color: #aaa; }
.empty-hint {
  display: block;
  text-align: center;
  font-size: 15px;
  color: #aaa;
  font-weight: 400;
  padding: 32px 0;
}

.chip-list { display: flex; flex-wrap: wrap; gap: 10px; }
.chip {
  padding: 8px 18px; border-radius: 999px;
  border: 2px solid #ffe3cf; background: #fff;
  font-size: 14px; font-weight: 600; color: #444;
  cursor: pointer; transition: all .18s;
}
.chip:hover  { background: #ffe3cf; }
.chip.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }

.lesson-list { display: flex; flex-direction: column; gap: 8px; }
.lesson-btn {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 16px; border-radius: 10px;
  border: 2px solid #ffe3cf; background: #fff;
  cursor: pointer; text-align: left; transition: all .18s;
}
.lesson-btn:hover  { background: #fff0e4; }
.lesson-btn.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }
.lesson-day   { font-size: 15px; font-weight: 800; min-width: 28px; }
.lesson-time  { font-size: 13px; font-weight: 600; min-width: 110px; opacity: .85; }
.lesson-topic { font-size: 14px; }

.date-row  { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.date-input {
  padding: 9px 14px; border-radius: 10px;
  border: 2px solid #ffe3cf; font-size: 15px;
  font-family: inherit; outline: none;
}
.date-input:focus { border-color: var(--brand-orange); }
.date-hint { font-size: 13px; color: #aaa; }

.quick-row   { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }
.quick-label { font-size: 13px; color: #888; font-weight: 600; }
.quick-btn {
  padding: 5px 14px; border-radius: 999px; border: 2px solid #ddd;
  background: #f5f5f5; font-size: 13px; font-weight: 700;
  cursor: pointer; transition: all .15s;
}
.qbtn-present:hover { background: #22a55b; color: #fff; border-color: #22a55b; }
.qbtn-late:hover    { background: #d9860a; color: #fff; border-color: #d9860a; }
.qbtn-absent:hover  { background: #e03c3c; color: #fff; border-color: #e03c3c; }
.qbtn-excused:hover { background: #5b8dd9; color: #fff; border-color: #5b8dd9; }

.students-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.student-row {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  background: #fff; border-radius: 10px;
  padding: 12px 16px; border: 1px solid #ffe3cf;
}
.student-name { font-size: 15px; font-weight: 600; min-width: 200px; color: #333; }

.status-buttons { display: flex; gap: 6px; flex-wrap: wrap; }
.status-opt {
  padding: 5px 12px; border-radius: 999px;
  border: 2px solid #ddd; background: #f5f5f5;
  font-size: 13px; font-weight: 600; cursor: pointer; transition: all .15s;
}
.status-opt:hover { border-color: #bbb; background: #eee; }
.status-opt.opt-present.active { background: #22a55b; color: #fff; border-color: #22a55b; }
.status-opt.opt-late.active    { background: #d9860a; color: #fff; border-color: #d9860a; }
.status-opt.opt-absent.active  { background: #e03c3c; color: #fff; border-color: #e03c3c; }
.status-opt.opt-excused.active { background: #5b8dd9; color: #fff; border-color: #5b8dd9; }

.note-input {
  flex: 1; min-width: 140px; padding: 6px 10px;
  border-radius: 8px; border: 1px solid #ddd;
  font-size: 13px; font-family: inherit;
}
.saved-badge { font-size: 13px; color: #22a55b; font-weight: 700; white-space: nowrap; }
.error-badge { font-size: 13px; color: #e03c3c; font-weight: 700; white-space: nowrap; }

.submit-row { display: flex; justify-content: flex-end; margin-bottom: 12px; }
.btn-submit {
  background: var(--brand-orange); color: #fff;
  border: none; padding: 12px 28px; border-radius: 10px;
  font-size: 15px; font-weight: 700; cursor: pointer;
}
.btn-submit:disabled { opacity: .6; cursor: not-allowed; }
.btn-submit:not(:disabled):hover { background: #e55a10; }

.submit-result {
  text-align: center; font-size: 15px; font-weight: 600;
  color: #22a55b; padding: 10px;
  background: #e6f9ef; border-radius: 10px;
}

/* ── Матрица посещаемости ─────────────────────────────────── */
.matrix-wrap {
  margin-top: 32px;
}
.matrix-wrap h3 {
  font-size: 20px; font-weight: 600; color: var(--brand-purple);
  margin-bottom: 0;
}
.matrix-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
}
.add-date-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 2px solid var(--brand-orange);
  background: #fff;
  color: var(--brand-orange);
  font-size: 24px;
  line-height: 1;
  font-weight: 700;
  cursor: pointer;
}
.add-date-btn:hover {
  background: #fff0e4;
}
.matrix-table-wrap {
  overflow-x: auto;
  border: 1px solid #ffe3cf;
  border-radius: 12px;
  background: #fff;
}
.matrix-table {
  min-width: max-content;
}
.matrix-header {
  display: flex;
  background: #fff0e4;
}
.matrix-row {
  display: flex;
}
.attendance-matrix-header,
.attendance-matrix-row {
  display: grid;
}
.matrix-cell {
  padding: 8px 12px;
  border-right: 1px solid #ffe3cf;
  border-bottom: 1px solid #ffe3cf;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 64px;
  font-size: 14px;
}
.matrix-cell:last-child {
  border-right: none;
}
.matrix-row:last-child .matrix-cell {
  border-bottom: none;
}
.header-cell {
  font-weight: 700;
  color: var(--brand-purple);
  text-transform: uppercase;
  letter-spacing: .05em;
  font-size: 12px;
  flex-direction: column;
  line-height: 1.1;
}
.header-time {
  margin-top: 4px;
  font-size: 11px;
  color: #555;
  font-weight: 600;
}
.header-actions {
  margin-top: 4px;
  display: flex;
  gap: 4px;
}
.header-icon-btn {
  width: 18px;
  height: 18px;
  border: 1px solid #ffcfad;
  border-radius: 5px;
  background: #fff;
  color: var(--brand-orange);
  font-size: 12px;
  line-height: 1;
  padding: 0;
  cursor: pointer;
}
.header-icon-btn.danger {
  color: #c53a3a;
  border-color: #f0bcbc;
}
.header-icon-btn:disabled {
  opacity: 0.5;
  cursor: wait;
}
.student-col {
  width: 280px;
  min-width: 280px;
  justify-content: flex-start;
}
.lesson-col {
  width: 72px;
  min-width: 72px;
}
.student-cell {
  justify-content: flex-start;
  font-weight: 600;
  background: #fff7f0;
}
.status-cell {
  height: 44px;
  font-weight: 700;
  font-size: 18px;
  line-height: 1;
  padding: 0;
  border: none;
  border-right: 1px solid #ffe3cf;
  border-bottom: 1px solid #ffe3cf;
  cursor: pointer;
}
.attendance-matrix-header .student-col,
.attendance-matrix-row .student-col,
.attendance-matrix-header .lesson-col,
.attendance-matrix-row .lesson-col {
  width: auto;
  min-width: 0;
}
.status-cell:disabled {
  cursor: wait;
  opacity: 0.7;
}
.mstatus-empty { background: #f5f5f5; color: #999; }
.mstatus-present { background: #22a55b; color: #fff; }
.mstatus-absent  { background: #e03c3c; color: #fff; }
.mstatus-late { background: #d9860a; color: #fff; }
.mstatus-excused { background: #5b8dd9; color: #fff; }

.skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.skeleton-card {
  height: 60px; border-radius: 12px;
  background: linear-gradient(90deg,#fff0e8 25%,#ffe8d6 50%,#fff0e8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }

/* ── Вкладка: Материалы урока ────────────────────────────── */
.materials-toolbar {
  margin-bottom: 14px;
}
.materials-group-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--brand-orange);
  margin: 0;
}
.materials-table-wrap {
  border: 1px solid #d9d9d9;
  background: #f4f4f4;
}
.materials-table-head {
  display: grid;
  grid-template-columns: 220px 1fr 54px;
  background: #ececec;
  border-bottom: 1px solid #d9d9d9;
}
.materials-head-date,
.materials-head-topic {
  padding: 10px 14px;
  font-size: 18px;
  font-weight: 700;
  color: #111;
}
.materials-head-date {
  border-right: 1px solid #c9c9c9;
}
.materials-head-action {
  border-left: 1px solid #c9c9c9;
}
.materials-row {
  display: grid;
  grid-template-columns: 220px 1fr 54px;
  border-bottom: 1px solid #d9d9d9;
}
.materials-row:last-child {
  border-bottom: none;
}
.materials-date-cell {
  border-right: 1px solid #c9c9c9;
  padding: 12px 14px;
  font-size: 16px;
  font-weight: 700;
  color: #111;
}
.materials-topic-cell {
  padding: 12px;
  white-space: pre-wrap;
  font-size: 16px;
  line-height: 1.45;
}
.materials-action-cell {
  border-left: 1px solid #c9c9c9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.materials-action-cell .header-icon-btn {
  width: 24px;
  height: 24px;
}

.materials-action-cell .header-icon-btn:disabled {
  cursor: wait;
}

@media (max-width: 720px) {
  .materials-table-head,
  .materials-row {
    grid-template-columns: 150px 1fr 46px;
  }
  .materials-head-date,
  .materials-head-topic {
    font-size: 15px;
  }
  .materials-date-cell,
  .materials-topic-cell {
    font-size: 14px;
  }
  .materials-toolbar {
    margin-bottom: 12px;
  }
}

/* ── Вкладка: Домашнее задание ──────────────────────────── */
.homework-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.homework-card {
  display: flex;
  gap: 14px;
  background: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  border-left: 4px solid #5b8dd9;
}

.homework-date {
  font-size: 13px;
  font-weight: 700;
  color: #5b8dd9;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: .05em;
}

.homework-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.homework-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.homework-deadline {
  font-size: 13px;
  color: #e03c3c;
  font-weight: 600;
}

/* ── Вкладка: Оплата обучения ────────────────────────────── */
.month-col {
  width: 80px;
  min-width: 80px;
}

.payment-cell {
  height: 44px;
  font-weight: 700;
  font-size: 16px;
  border: none;
  border-right: 1px solid #ffe3cf;
  border-bottom: 1px solid #ffe3cf;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-paid {
  background: #22a55b;
  color: #fff;
}

.payment-unpaid {
  background: #fdeaea;
  color: #e03c3c;
}

.payment-cell:hover {
  opacity: 0.8;
}

/* ── Вкладка: Промежуточная успеваемость ──────────────────── */
.grade-cell {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 15px;
  border: none;
  border-right: 1px solid #ffe3cf;
  border-bottom: 1px solid #ffe3cf;
  background: #f5f5f5;
  color: #333;
}

@media (max-width: 600px) {
  .stats-bar  { gap: 10px; }
  .stat       { min-width: 80px; padding: 10px 12px; }
  .student-name { min-width: unset; width: 100%; }
  .status-buttons { width: 100%; }
  .lesson-time { display: none; }
  .report-filters { flex-direction: column; }
}
</style>
