<template>
  <div class="attendance-page">
    <h1>✅ Посещаемость</h1>

    <!-- ═══════════════════════════════════════════════════════
         РЕЖИМ СТУДЕНТА — своя посещаемость
    ════════════════════════════════════════════════════════ -->
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

    <!-- ═══════════════════════════════════════════════════════
         РЕЖИМ УЧИТЕЛЯ / АДМИНА — отметить посещаемость
    ════════════════════════════════════════════════════════ -->
    <template v-else-if="auth.isStaff">

      <!-- Шаг 1: выбери группу -->
      <div class="staff-section">
        <div class="step-label">Шаг 1 — Выберите группу</div>
        <div v-if="groupsLoading" class="loading-hint">Загрузка групп...</div>
        <div v-else-if="groups.length === 0" class="no-records">
          <p>Групп нет. Обратитесь к администратору.</p>
        </div>
        <div v-else class="group-list">
          <button
            v-for="g in groups" :key="g.id"
            class="group-btn" :class="{ active: selectedGroupId === g.id }"
            @click="selectGroup(g.id)"
          >{{ g.name }}</button>
        </div>
      </div>

      <!-- Шаг 2: выбери занятие -->
      <div v-if="selectedGroupId" class="staff-section">
        <div class="step-label">Шаг 2 — Выберите занятие</div>
        <div v-if="lessonsLoading" class="loading-hint">Загрузка занятий...</div>
        <div v-else-if="lessons.length === 0" class="no-records">
          <p>Занятий для этой группы нет.</p>
        </div>
        <div v-else class="lesson-list">
          <button
            v-for="l in lessons" :key="l.id"
            class="lesson-btn" :class="{ active: selectedLessonId === l.id }"
            @click="selectLesson(l)"
          >
            <span class="lesson-date">{{ formatDate(l.date) }}</span>
            <span class="lesson-name">{{ l.subject || l.title || 'Занятие' }}</span>
          </button>
        </div>
      </div>

      <!-- Шаг 3: отметить учеников -->
      <div v-if="selectedLessonId" class="staff-section">
        <div class="step-label">Шаг 3 — Отметьте учеников</div>
        <div v-if="studentsLoading" class="loading-hint">Загрузка учеников...</div>
        <div v-else-if="students.length === 0" class="no-records">
          <p>В группе нет учеников.</p>
        </div>
        <div v-else>
          <div class="students-list">
            <div v-for="s in students" :key="s.id" class="student-row">
              <div class="student-name">{{ s.student_name }}</div>
              <div class="status-buttons">
                <button
                  v-for="opt in statusOptions" :key="opt.value"
                  class="status-opt"
                  :class="{ active: marks[s.id] === opt.value, ['opt-' + opt.value]: true }"
                  @click="marks[s.id] = opt.value"
                >{{ opt.label }}</button>
              </div>
              <input
                v-model="notes[s.id]"
                class="note-input"
                placeholder="Примечание..."
              />
              <span v-if="saved[s.id]" class="saved-badge">✅ Сохранено</span>
              <span v-if="errors[s.id]" class="error-badge">⚠️ {{ errors[s.id] }}</span>
            </div>
          </div>

          <div class="submit-row">
            <button class="btn-submit" @click="submitAll" :disabled="submitting">
              {{ submitting ? 'Сохраняю...' : 'Сохранить отметки' }}
            </button>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// ── СТУДЕНТ: своя посещаемость ─────────────────────────────────────────
const loading     = ref(true)
const records     = ref<any[]>([])
const activeFilter = ref('all')

const counts = computed(() => ({
  present: records.value.filter(r => r.status === 'present').length,
  absent:  records.value.filter(r => r.status === 'absent').length,
  late:    records.value.filter(r => r.status === 'late').length,
  excused: records.value.filter(r => r.status === 'excused').length,
}))
const attendanceRate = computed(() => {
  const total = records.value.length
  if (!total) return 0
  return Math.round((counts.value.present + counts.value.late) / total * 100)
})
const statCards = computed(() => [
  { label: 'Был на занятии',    value: counts.value.present, color: '#22a55b' },
  { label: 'Отсутствовал',      value: counts.value.absent,  color: '#e03c3c' },
  { label: 'Опоздал',            value: counts.value.late,    color: '#d9860a' },
  { label: 'Уважит. причина', value: counts.value.excused, color: '#5b8dd9' },
])
const filters = computed(() => [
  { key: 'all',     label: 'Все',             count: records.value.length },
  { key: 'present', label: 'Присутствовал', count: counts.value.present },
  { key: 'absent',  label: 'Отсутствовал',  count: counts.value.absent  },
  { key: 'late',    label: 'Опоздал',          count: counts.value.late    },
  { key: 'excused', label: 'Уваж. прич.',   count: counts.value.excused },
])
const filteredRecords = computed(() =>
  activeFilter.value === 'all'
    ? records.value
    : records.value.filter(r => r.status === activeFilter.value)
)

// ── УЧИТЕЛЬ / АДМИН: отметка ─────────────────────────────────────────────
const groupsLoading   = ref(false)
const lessonsLoading  = ref(false)
const studentsLoading = ref(false)
const submitting      = ref(false)

const groups          = ref<any[]>([])
const lessons         = ref<any[]>([])
const students        = ref<any[]>([])

const selectedGroupId  = ref<number | null>(null)
const selectedLessonId = ref<number | null>(null)
const selectedLesson   = ref<any>(null)

const marks  = reactive<Record<number, string>>({})
const notes  = reactive<Record<number, string>>({})
const saved  = reactive<Record<number, boolean>>({})
const errors = reactive<Record<number, string>>({})

const statusOptions = [
  { value: 'present', label: 'Был' },
  { value: 'late',    label: 'Опоздал' },
  { value: 'absent',  label: 'Не был' },
  { value: 'excused', label: 'Уваж. прич.' },
]

async function loadGroups() {
  groupsLoading.value = true
  try {
    const r = await http.get('/groups')
    groups.value = r.data
  } catch { groups.value = [] }
  finally { groupsLoading.value = false }
}

async function selectGroup(id: number) {
  selectedGroupId.value  = id
  selectedLessonId.value = null
  selectedLesson.value   = null
  students.value         = []
  lessons.value          = []
  lessonsLoading.value   = true
  try {
    const r = await http.get(`/schedule?group_id=${id}`)
    lessons.value = r.data
  } catch { lessons.value = [] }
  finally { lessonsLoading.value = false }
}

async function selectLesson(lesson: any) {
  selectedLessonId.value = lesson.id
  selectedLesson.value   = lesson
  studentsLoading.value  = true
  // Сбрасываем отметки
  Object.keys(marks).forEach(k => delete (marks as any)[k])
  Object.keys(notes).forEach(k => delete (notes as any)[k])
  Object.keys(saved).forEach(k => delete (saved as any)[k])
  Object.keys(errors).forEach(k => delete (errors as any)[k])
  try {
    const r = await http.get(`/groups/${selectedGroupId.value}/students`)
    students.value = r.data
    // По умолчанию все «присутствовал»
    students.value.forEach((s: any) => { marks[s.id] = 'present' })
  } catch { students.value = [] }
  finally { studentsLoading.value = false }
}

async function submitAll() {
  submitting.value = true
  for (const s of students.value) {
    delete (saved as any)[s.id]
    delete (errors as any)[s.id]
    try {
      await http.post('/attendance/', {
        lesson_id:        selectedLessonId.value,
        student_group_id: s.id,
        status:           marks[s.id] || 'present',
        note:             notes[s.id] || null,
        lesson_date:      selectedLesson.value?.date
          ? new Date(selectedLesson.value.date).toISOString()
          : new Date().toISOString(),
      })
      saved[s.id] = true
    } catch (e: any) {
      const detail = e?.response?.data?.detail
      errors[s.id] = typeof detail === 'string' ? detail : 'Ошибка'
    }
  }
  submitting.value = false
}

// ── Общие ─────────────────────────────────────────────────────────────────
function statusLabel(s: string): string {
  return { present: 'Был', absent: 'Не был', late: 'Опоздал', excused: 'Уваж. прич.' }[s] ?? s
}
function formatDate(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric', weekday: 'short' })
}

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
.attendance-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 24px; }

/* ── Статистика студента ───────────────────────── */
.stats-bar { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
.stat {
  background: #fff7f0; border-radius: 12px; padding: 14px 20px;
  display: flex; flex-direction: column; gap: 4px;
  border: 1.5px solid #ffe3cf; min-width: 110px; text-align: center;
}
.stat-value { font-size: 28px; font-weight: 700; }
.stat-label { font-size: 12px; color: #888; }

.progress-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.progress-bar { flex: 1; height: 10px; background: #f0ece8; border-radius: 999px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--brand-orange); border-radius: 999px; transition: width 0.6s ease; }
.progress-label { font-size: 14px; color: #888; white-space: nowrap; }

.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.filter-btn {
  padding: 6px 14px; border-radius: 999px; border: 2px solid #ffe3cf;
  background: #fff; font-size: 13px; font-weight: 600; color: var(--brand-purple);
  cursor: pointer; transition: all 0.18s; display: flex; align-items: center; gap: 6px;
}
.filter-btn:hover { background: #ffe3cf; }
.filter-btn.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }
.filter-count { background: rgba(255,255,255,0.35); border-radius: 999px; padding: 1px 7px; font-size: 12px; }

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
.record-badge { font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 999px; white-space: nowrap; }
.status-present .record-badge { background: #e6f9ef; color: #22a55b; }
.status-absent  .record-badge { background: #fdeaea; color: #e03c3c; }
.status-late    .record-badge { background: #fff3dc; color: #d9860a; }
.status-excused .record-badge { background: #e8f0fc; color: #5b8dd9; }
.no-filter { text-align: center; color: #bbb; padding: 20px; font-size: 15px; }

/* ── Пустое состояние ──────────────────────────── */
.no-records { text-align: center; padding: 40px; background: #fff7f0; border-radius: 14px; color: #888; }
.no-records-icon { font-size: 48px; margin-bottom: 12px; }
.no-records p { font-size: 16px; margin-bottom: 6px; }
.no-records-hint { font-size: 14px; color: #bbb; }

/* ── Режим учителя ────────────────────────────── */
.staff-section {
  background: #fff7f0;
  border-radius: 14px;
  padding: 20px 22px;
  margin-bottom: 20px;
  border: 1px solid #ffe3cf;
}
.step-label {
  font-size: 13px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--brand-orange); margin-bottom: 14px;
}
.loading-hint { font-size: 14px; color: #aaa; }

.group-list { display: flex; flex-wrap: wrap; gap: 10px; }
.group-btn {
  padding: 9px 18px; border-radius: 10px; border: 2px solid #ffe3cf;
  background: #fff; font-size: 14px; font-weight: 600; color: #444;
  cursor: pointer; transition: all 0.18s;
}
.group-btn:hover { background: #ffe3cf; }
.group-btn.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }

.lesson-list { display: flex; flex-direction: column; gap: 8px; }
.lesson-btn {
  display: flex; align-items: center; gap: 14px;
  padding: 11px 16px; border-radius: 10px; border: 2px solid #ffe3cf;
  background: #fff; cursor: pointer; text-align: left; transition: all 0.18s;
}
.lesson-btn:hover { background: #ffe3cf; }
.lesson-btn.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }
.lesson-date { font-size: 13px; font-weight: 700; min-width: 180px; }
.lesson-name { font-size: 14px; }

/* Список учеников */
.students-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }
.student-row {
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  background: #fff; border-radius: 10px; padding: 12px 16px;
  border: 1px solid #ffe3cf;
}
.student-name { font-size: 15px; font-weight: 600; min-width: 180px; color: #333; }

.status-buttons { display: flex; gap: 6px; flex-wrap: wrap; }
.status-opt {
  padding: 5px 12px; border-radius: 999px; border: 2px solid #ddd;
  background: #f5f5f5; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.15s;
}
.status-opt.opt-present.active { background: #22a55b; color: #fff; border-color: #22a55b; }
.status-opt.opt-late.active    { background: #d9860a; color: #fff; border-color: #d9860a; }
.status-opt.opt-absent.active  { background: #e03c3c; color: #fff; border-color: #e03c3c; }
.status-opt.opt-excused.active { background: #5b8dd9; color: #fff; border-color: #5b8dd9; }
.status-opt:hover { border-color: #bbb; background: #eee; }

.note-input {
  flex: 1; min-width: 140px; padding: 6px 10px;
  border-radius: 8px; border: 1px solid #ddd;
  font-size: 13px; font-family: inherit;
}
.saved-badge  { font-size: 13px; color: #22a55b; font-weight: 600; white-space: nowrap; }
.error-badge  { font-size: 13px; color: #e03c3c; font-weight: 600; white-space: nowrap; }

.submit-row { display: flex; justify-content: flex-end; }
.btn-submit {
  background: var(--brand-orange); color: #fff; border: none;
  padding: 12px 28px; border-radius: 10px; font-size: 15px;
  font-weight: 700; cursor: pointer;
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-submit:not(:disabled):hover { background: #e55a10; }

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
  .stats-bar { gap: 10px; }
  .stat { min-width: 80px; padding: 10px 12px; }
  .student-name { min-width: unset; width: 100%; }
  .status-buttons { width: 100%; }
}
</style>
