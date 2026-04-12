<template>
  <div class="attendance-page">
    <h1>✅ Посещаемость</h1>

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
        <div class="no-records-icon">✅</div>
        <p>Записей о посещаемости пока нет.</p>
        <p class="no-records-hint">Они появятся здесь, когда преподаватель начнёт отмечать занятия.</p>
      </div>
    </template>

    <!-- ══════════════════════════════════════
         РЕЖИМ УЧИТЕЛЯ / АДМИНА — отметить
    ══════════════════════════════════════ -->
    <template v-else-if="auth.isStaff">

      <!-- Шаг 1: выбрать группу -->
      <div class="staff-section">
        <div class="step-label">Шаг 1 — Выберите группу</div>
        <div v-if="groupsLoading" class="loading-hint">Загрузка групп...</div>
        <div v-else-if="!groups.length" class="empty-hint">Групп не найдено.</div>
        <div v-else class="chip-list">
          <button
            v-for="g in groups" :key="g.id"
            class="chip" :class="{ active: selectedGroupId === g.id }"
            @click="onSelectGroup(g.id)"
          >{{ g.name }}</button>
        </div>
      </div>

      <!-- Шаг 2: выбрать занятие -->
      <div v-if="selectedGroupId" class="staff-section">
        <div class="step-label">Шаг 2 — Выберите занятие</div>
        <div v-if="lessonsLoading" class="loading-hint">Загрузка занятий...</div>
        <div v-else-if="!lessons.length" class="empty-hint">Занятий для этой группы нет.</div>
        <div v-else class="lesson-list">
          <button
            v-for="l in lessons" :key="l.id"
            class="lesson-btn" :class="{ active: selectedLesson?.id === l.id }"
            @click="onSelectLesson(l)"
          >
            <span class="lesson-day">{{ dayLabel(l.day_of_week) }}</span>
            <span class="lesson-time">{{ fmtTime(l.time_start) }} – {{ fmtTime(l.time_end) }}</span>
            <span class="lesson-topic">{{ l.topic || 'Занятие' }}</span>
          </button>
        </div>
      </div>

      <!-- Шаг 3: выбрать дату проведения -->
      <div v-if="selectedLesson" class="staff-section">
        <div class="step-label">Шаг 3 — Дата проведения занятия</div>
        <div class="date-row">
          <input
            type="date"
            class="date-input"
            v-model="lessonDateStr"
            :max="todayStr"
          />
          <span class="date-hint">Выберите дату, когда занятие фактически проводилось</span>
        </div>
      </div>

      <!-- Шаг 4: отметить учеников -->
      <div v-if="selectedLesson && lessonDateStr" class="staff-section">
        <div class="step-label">Шаг 4 — Отметьте учеников</div>
        <div v-if="studentsLoading" class="loading-hint">Загрузка списка...</div>
        <div v-else-if="!students.length" class="empty-hint">В группе нет студентов.</div>
        <div v-else>
          <!-- Быстрые кнопки -->
          <div class="quick-row">
            <span class="quick-label">Быстро отметить всех:</span>
            <button v-for="opt in statusOptions" :key="opt.value"
              class="quick-btn" :class="'qbtn-' + opt.value"
              @click="markAll(opt.value)"
            >{{ opt.label }}</button>
          </div>

          <div class="students-list">
            <div v-for="s in students" :key="s.id" class="student-row">
              <div class="student-name">{{ s.student_name }}</div>
              <div class="status-buttons">
                <button
                  v-for="opt in statusOptions" :key="opt.value"
                  class="status-opt" :class="{ active: marks[s.id] === opt.value, ['opt-' + opt.value]: true }"
                  @click="marks[s.id] = opt.value"
                >{{ opt.label }}</button>
              </div>
              <input v-model="notes[s.id]" class="note-input" placeholder="Примечание..." />
              <span v-if="rowSaved[s.id]" class="saved-badge">✅ Сохранено</span>
              <span v-else-if="rowError[s.id]" class="error-badge">⚠️ {{ rowError[s.id] }}</span>
            </div>
          </div>

          <div class="submit-row">
            <button class="btn-submit" @click="submitAll" :disabled="submitting">
              {{ submitting ? 'Сохраняю...' : 'Сохранить отметки' }}
            </button>
          </div>

          <div v-if="submitDone" class="submit-result">
            ✅ Готово: {{ savedCount }} сохранено
            <span v-if="errorCount"> · ⚠️ {{ errorCount }} ошибок (уже отмечены?)</span>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// ── ОБЩИЕ УТИЛИТЫ ──────────────────────────────────────────────────────
const DAY_LABELS: Record<string, string> = {
  monday: 'Пн', tuesday: 'Вт', wednesday: 'Ср',
  thursday: 'Чт', friday: 'Пт', saturday: 'Сб', sunday: 'Вс',
}
function dayLabel(d: string) { return DAY_LABELS[d] ?? d }
function fmtTime(t: string) { return t?.slice(0, 5) ?? '' }
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

const statusOptions = [
  { value: 'present', label: 'Был' },
  { value: 'late',    label: 'Опоздал' },
  { value: 'absent',  label: 'Не был' },
  { value: 'excused', label: 'Уваж. прич.' },
]

// ── СТУДЕНТ: своя посещаемость ─────────────────────────────────────────
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
  { label: 'Был на занятии',    value: counts.value.present, color: '#22a55b' },
  { label: 'Отсутствовал',      value: counts.value.absent,  color: '#e03c3c' },
  { label: 'Опоздал',          value: counts.value.late,    color: '#d9860a' },
  { label: 'Уважит. причина',  value: counts.value.excused, color: '#5b8dd9' },
])
const filters = computed(() => [
  { key: 'all',     label: 'Все',             count: records.value.length },
  { key: 'present', label: 'Присутствовал',  count: counts.value.present },
  { key: 'absent',  label: 'Отсутствовал',   count: counts.value.absent  },
  { key: 'late',    label: 'Опоздал',          count: counts.value.late    },
  { key: 'excused', label: 'Уваж. прич.',    count: counts.value.excused },
])
const filteredRecords = computed(() =>
  activeFilter.value === 'all'
    ? records.value
    : records.value.filter(r => r.status === activeFilter.value)
)

// ── УЧИТЕЛЬ: отметить посещаемость ────────────────────────────────────
const groupsLoading   = ref(false)
const lessonsLoading  = ref(false)
const studentsLoading = ref(false)
const submitting      = ref(false)
const submitDone      = ref(false)

const groups   = ref<any[]>([])
const lessons  = ref<any[]>([])
const students = ref<any[]>([])

const selectedGroupId = ref<number | null>(null)
const selectedLesson  = ref<any>(null)
const lessonDateStr   = ref('')   // 'YYYY-MM-DD' из <input type="date">

const marks    = reactive<Record<number, string>>({})
const notes    = reactive<Record<number, string>>({})
const rowSaved = reactive<Record<number, boolean>>({})
const rowError = reactive<Record<number, string>>({})

const savedCount = computed(() => Object.values(rowSaved).filter(Boolean).length)
const errorCount = computed(() => Object.values(rowError).filter(Boolean).length)

function clearStudentState() {
  students.value = []
  ;(Object.keys(marks)  as any[]).forEach(k => delete marks[k])
  ;(Object.keys(notes)  as any[]).forEach(k => delete notes[k])
  ;(Object.keys(rowSaved) as any[]).forEach(k => delete rowSaved[k])
  ;(Object.keys(rowError) as any[]).forEach(k => delete rowError[k])
  submitDone.value = false
}

async function loadGroups() {
  groupsLoading.value = true
  try {
    const r = await http.get('/groups')
    groups.value = r.data
  } catch { groups.value = [] }
  finally { groupsLoading.value = false }
}

async function onSelectGroup(id: number) {
  selectedGroupId.value = id
  selectedLesson.value  = null
  lessonDateStr.value   = ''
  clearStudentState()
  lessons.value = []
  lessonsLoading.value = true
  try {
    const r = await http.get('/schedule', { params: { group_id: id } })
    lessons.value = r.data
  } catch { lessons.value = [] }
  finally { lessonsLoading.value = false }
}

async function onSelectLesson(lesson: any) {
  selectedLesson.value = lesson
  lessonDateStr.value  = todayStr   // по умолчанию — сегодня
  clearStudentState()
  studentsLoading.value = true
  try {
    const r = await http.get(`/groups/${selectedGroupId.value}/students`)
    students.value = r.data
    // по умолчанию все — «Был»
    students.value.forEach((s: any) => { marks[s.id] = 'present' })
  } catch { students.value = [] }
  finally { studentsLoading.value = false }
}

function markAll(status: string) {
  students.value.forEach((s: any) => { marks[s.id] = status })
}

async function submitAll() {
  submitting.value = true
  submitDone.value = false
  // сбрасываем предыдущие результаты
  ;(Object.keys(rowSaved) as any[]).forEach(k => delete rowSaved[k])
  ;(Object.keys(rowError) as any[]).forEach(k => delete rowError[k])

  const lessonDateISO = new Date(lessonDateStr.value + 'T00:00:00').toISOString()

  for (const s of students.value) {
    try {
      await http.post('/attendance/', {
        lesson_id:        selectedLesson.value.id,
        student_group_id: s.id,
        status:           marks[s.id] ?? 'present',
        note:             notes[s.id] || null,
        lesson_date:      lessonDateISO,
      })
      rowSaved[s.id] = true
    } catch (e: any) {
      const detail = e?.response?.data?.detail
      rowError[s.id] = typeof detail === 'string' ? detail : 'Ошибка'
    }
  }
  submitting.value = false
  submitDone.value = true
}

// ── INIT ───────────────────────────────────────────────────────────────
onMounted(async () => {
  if (auth.isStudent) {
    try {
      const res = await http.get('/attendance/my')
      records.value = res.data
    } catch { records.value = [] }
    finally { loading.value = false }
  } else if (auth.isStaff) {
    await loadGroups()
  }
})
</script>

<style scoped>
.attendance-page h1 {
  font-size: 28px; font-weight: 700;
  color: var(--brand-purple); margin-bottom: 24px;
}

/* ── Статистика студента ───────────────────────────────── */
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
.filter-btn:hover { background: #ffe3cf; }
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
.record-date { font-size: 15px; font-weight: 600; color: #333; }
.record-note { font-size: 13px; color: #888; }
.record-badge { font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 999px; }
.status-present .record-badge { background: #e6f9ef; color: #22a55b; }
.status-absent  .record-badge { background: #fdeaea; color: #e03c3c; }
.status-late    .record-badge { background: #fff3dc; color: #d9860a; }
.status-excused .record-badge { background: #e8f0fc; color: #5b8dd9; }
.no-filter { text-align: center; color: #bbb; padding: 20px; }

/* ── Пустое состояние ─────────────────────────────────── */
.no-records {
  text-align: center; padding: 40px;
  background: #fff7f0; border-radius: 14px; color: #888;
}
.no-records-icon { font-size: 48px; margin-bottom: 12px; }
.no-records p { font-size: 16px; margin-bottom: 6px; }
.no-records-hint { font-size: 14px; color: #bbb; }

/* ── Режим учителя: секции ─────────────────────────────── */
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
.empty-hint   { font-size: 14px; color: #bbb; }

/* группы */
.chip-list { display: flex; flex-wrap: wrap; gap: 10px; }
.chip {
  padding: 8px 18px; border-radius: 999px;
  border: 2px solid #ffe3cf; background: #fff;
  font-size: 14px; font-weight: 600; color: #444;
  cursor: pointer; transition: all .18s;
}
.chip:hover { background: #ffe3cf; }
.chip.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }

/* занятия */
.lesson-list { display: flex; flex-direction: column; gap: 8px; }
.lesson-btn {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 16px; border-radius: 10px;
  border: 2px solid #ffe3cf; background: #fff;
  cursor: pointer; text-align: left; transition: all .18s;
}
.lesson-btn:hover { background: #fff0e4; }
.lesson-btn.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }
.lesson-day  { font-size: 15px; font-weight: 800; min-width: 28px; }
.lesson-time { font-size: 13px; font-weight: 600; min-width: 110px; opacity: .85; }
.lesson-topic { font-size: 14px; }

/* дата */
.date-row   { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.date-input {
  padding: 9px 14px; border-radius: 10px;
  border: 2px solid #ffe3cf; font-size: 15px;
  font-family: inherit; outline: none;
}
.date-input:focus { border-color: var(--brand-orange); }
.date-hint { font-size: 13px; color: #aaa; }

/* быстрые кнопки */
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

/* строка студента */
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

/* Скелетон */
.skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.skeleton-card {
  height: 60px; border-radius: 12px;
  background: linear-gradient(90deg,#fff0e8 25%,#ffe8d6 50%,#fff0e8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }

@media (max-width: 600px) {
  .stats-bar  { gap: 10px; }
  .stat       { min-width: 80px; padding: 10px 12px; }
  .student-name { min-width: unset; width: 100%; }
  .status-buttons { width: 100%; }
  .lesson-time { display: none; }
}
</style>
