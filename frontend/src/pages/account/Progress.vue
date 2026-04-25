<template>
  <div class="progress-page">
    <h1>Промежуточная успеваемость</h1>

    <div class="filters-card report-filters">
      <div class="filter-grid">
        <div class="field filter-field">
          <label>Филиал</label>
          <select v-model.number="filters.branch_id" @change="onBranchChange">
            <option :value="null">Выберите филиал</option>
            <option v-for="branch in branches" :key="branch.id" :value="branch.id">{{ branch.name }}</option>
          </select>
        </div>

        <div class="field filter-field">
          <label>Преподаватель</label>
          <select v-model.number="filters.teacher_id" @change="onTeacherChange" :disabled="!filters.branch_id">
            <option :value="null">Выберите преподавателя</option>
            <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">{{ teacher.full_name }}</option>
          </select>
        </div>

        <div class="field filter-field">
          <label>Группа</label>
          <select v-model.number="filters.group_id" @change="loadMatrix" :disabled="!filters.teacher_id">
            <option :value="null">Выберите группу</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">{{ group.name }}</option>
          </select>
        </div>

        <div class="field filter-field date-field">
          <label>Дата с</label>
          <input type="date" v-model="filters.date_from" @change="loadMatrix" />
        </div>

        <div class="field filter-field date-field">
          <label>По</label>
          <input type="date" v-model="filters.date_to" @change="loadMatrix" />
        </div>

        <div class="field filter-field student-field">
          <label>Студент</label>
          <input type="text" v-model.trim="filters.student_name" placeholder="Поиск по имени" />
          <button type="button" class="clear-btn" @click="filters.student_name = ''">Очистить</button>
        </div>
      </div>
    </div>

    <section v-if="groupInfo" class="group-info">
      <h2>{{ groupInfo.course_name }}, {{ groupInfo.teacher_name }}</h2>
      <p>{{ groupInfo.schedule.join(', ') || 'Расписание не указано' }}</p>
    </section>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="groupInfo" class="matrix-wrap">
      <table class="progress-table">
        <thead>
          <tr>
            <th class="col-student">Ученики</th>
            <th class="col-extra">Дополнит.</th>
            <th v-for="lesson in lessons" :key="lessonKey(lesson)" class="col-lesson">
              {{ formatLessonHeader(lesson) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(student, index) in visibleStudents" :key="student.id" :class="{ attention: attentionIds.has(student.id) }">
            <td class="student-cell">{{ index + 1 }}. {{ student.student_name }}</td>
            <td class="extra-cell">
              <button
                class="note-chip"
                :class="{ active: studentNotes(student.id).length > 0 }"
                @click="openStudentNotes(student)"
                title="Дополнительные заметки по ученику"
              >
                !
              </button>
            </td>
            <td v-for="lesson in lessons" :key="`${student.id}-${lessonKey(lesson)}`" class="lesson-cell">
              <div class="cell-stack">
                <button
                  class="grade-box"
                  :class="gradeClass(student.id, lesson)"
                  @click="cycleGrade(student.id, lesson)"
                  :title="cellGrade(student.id, lesson) ? 'Изменить оценку' : 'Поставить оценку'"
                >
                  {{ cellGrade(student.id, lesson) ?? '' }}
                </button>
                <button
                  class="note-chip"
                  :class="{ active: Boolean(cellRecord(student.id, lesson)?.note) }"
                  @click="openLessonNote(student, lesson)"
                  title="Комментарий к уроку"
                >
                  !
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="empty-text">Выберите группу, чтобы увидеть промежуточную успеваемость.</p>

    <div v-if="noteModal.open" class="modal-backdrop" @click.self="closeNoteModal">
      <div class="modal">
        <h3>{{ noteModal.mode === 'student' ? noteModal.studentName : `${noteModal.studentName} · ${noteModal.lessonLabel}` }}</h3>

        <div v-if="noteModal.mode === 'student'" class="notes-list">
          <p v-if="!noteModal.items.length" class="empty-notes">Заметок пока нет.</p>
          <div v-for="item in noteModal.items" :key="item.key" class="note-item">
            <strong>{{ item.label }}</strong>
            <span>{{ item.note }}</span>
          </div>
        </div>

        <div v-else class="note-editor">
          <label>Комментарий
            <textarea v-model="noteModal.note" rows="5" placeholder="Добавьте комментарий по уроку..."></textarea>
          </label>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeNoteModal">Закрыть</button>
          <button v-if="noteModal.mode === 'lesson'" class="btn-primary" @click="saveLessonNote" :disabled="savingNote">
            {{ savingNote ? 'Сохраняю...' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import http from '@/api/http'

type LessonSlot = {
  id: number
  slot_date: string
  time_start: string | null
}

type MatrixStudent = {
  id: number
  student_name: string
}

type CellRecord = {
  grade: number | null
  note: string | null
  status: string | null
}

const branches = ref<any[]>([])
const teachers = ref<any[]>([])
const groups = ref<any[]>([])
const lessons = ref<LessonSlot[]>([])
const students = ref<MatrixStudent[]>([])
const records = ref<Record<string, CellRecord>>({})
const attentionIds = ref<Set<number>>(new Set())
const groupInfo = ref<any | null>(null)
const loading = ref(false)
const savingNote = ref(false)

const filters = reactive({
  branch_id: null as number | null,
  teacher_id: null as number | null,
  group_id: null as number | null,
  date_from: '',
  date_to: '',
  student_name: '',
})

const noteModal = reactive({
  open: false,
  mode: 'lesson' as 'lesson' | 'student',
  studentId: null as number | null,
  studentName: '',
  lesson: null as LessonSlot | null,
  lessonLabel: '',
  note: '',
  items: [] as Array<{ key: string; label: string; note: string }>,
})

const visibleStudents = computed(() => {
  const query = filters.student_name.trim().toLowerCase()
  if (!query) return students.value
  return students.value.filter((student) => student.student_name.toLowerCase().includes(query))
})

onMounted(loadBranches)

async function loadBranches() {
  try {
    branches.value = (await http.get('/branches/')).data
  } catch {
    branches.value = []
  }
}

async function onBranchChange() {
  filters.teacher_id = null
  filters.group_id = null
  teachers.value = []
  groups.value = []
  resetMatrix()
  if (!filters.branch_id) return
  try {
    teachers.value = (await http.get('/teachers/', { params: { branch_id: filters.branch_id } })).data
  } catch {
    teachers.value = []
  }
}

async function onTeacherChange() {
  filters.group_id = null
  groups.value = []
  resetMatrix()
  if (!filters.teacher_id) return
  try {
    groups.value = (await http.get('/groups', { params: { branch_id: filters.branch_id, teacher_id: filters.teacher_id } })).data
  } catch {
    groups.value = []
  }
}

async function loadMatrix() {
  if (!filters.group_id) {
    resetMatrix()
    return
  }
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (filters.date_from) params.date_from = filters.date_from
    if (filters.date_to) params.date_to = filters.date_to
    const res = await http.get(`/attendance/group/${filters.group_id}/grades`, { params })
    groupInfo.value = res.data.group
    students.value = res.data.students || []
    lessons.value = res.data.lessons || []
    records.value = res.data.records || {}
    attentionIds.value = new Set<number>(res.data.attention_student_ids || [])
  } catch {
    resetMatrix()
  } finally {
    loading.value = false
  }
}

function resetMatrix() {
  groupInfo.value = null
  students.value = []
  lessons.value = []
  records.value = {}
  attentionIds.value = new Set()
}

function lessonKey(lesson: LessonSlot) {
  return `${lesson.id}:${lesson.slot_date}`
}

function recordKey(studentId: number, lesson: LessonSlot) {
  return `${studentId}:${lesson.id}:${lesson.slot_date}`
}

function cellRecord(studentId: number, lesson: LessonSlot) {
  return records.value[recordKey(studentId, lesson)] || null
}

function cellGrade(studentId: number, lesson: LessonSlot) {
  return cellRecord(studentId, lesson)?.grade ?? null
}

function gradeClass(studentId: number, lesson: LessonSlot) {
  const grade = cellGrade(studentId, lesson)
  if (grade === 5) return 'grade-5'
  if (grade === 4) return 'grade-4'
  if (grade === 3) return 'grade-3'
  return 'grade-empty'
}

function nextGrade(current: number | null) {
  if (current == null) return 4
  if (current === 4) return 5
  return null
}

async function cycleGrade(studentId: number, lesson: LessonSlot) {
  const current = cellRecord(studentId, lesson)
  const student = students.value.find((item) => item.id === studentId)
  if (!student) return
  try {
    const payload = {
      lesson_id: lesson.id,
      student_group_id: studentId,
      lesson_date: `${lesson.slot_date}T00:00:00`,
      status: current?.status || 'present',
      grade: nextGrade(current?.grade ?? null),
      note: current?.note || null,
    }
    const res = await http.put('/attendance/upsert', payload)
    records.value[recordKey(studentId, lesson)] = {
      grade: res.data.grade,
      note: res.data.note,
      status: res.data.status,
    }
  } catch {
    // silent ui fallback
  }
}

function formatLessonHeader(lesson: LessonSlot) {
  const date = new Date(`${lesson.slot_date}T00:00:00`)
  const datePart = date.toLocaleDateString('ru-RU')
  const timePart = (lesson.time_start || '').slice(0, 5)
  return `${datePart} ${timePart}`.trim()
}

function studentNotes(studentId: number) {
  return lessons.value
    .map((lesson) => {
      const record = cellRecord(studentId, lesson)
      if (!record?.note) return null
      return {
        key: `${studentId}-${lessonKey(lesson)}`,
        label: formatLessonHeader(lesson),
        note: record.note,
      }
    })
    .filter(Boolean) as Array<{ key: string; label: string; note: string }>
}

function openStudentNotes(student: MatrixStudent) {
  noteModal.open = true
  noteModal.mode = 'student'
  noteModal.studentId = student.id
  noteModal.studentName = student.student_name
  noteModal.lesson = null
  noteModal.lessonLabel = ''
  noteModal.note = ''
  noteModal.items = studentNotes(student.id)
}

function openLessonNote(student: MatrixStudent, lesson: LessonSlot) {
  noteModal.open = true
  noteModal.mode = 'lesson'
  noteModal.studentId = student.id
  noteModal.studentName = student.student_name
  noteModal.lesson = lesson
  noteModal.lessonLabel = formatLessonHeader(lesson)
  noteModal.note = cellRecord(student.id, lesson)?.note || ''
  noteModal.items = []
}

function closeNoteModal() {
  noteModal.open = false
  noteModal.studentId = null
  noteModal.studentName = ''
  noteModal.lesson = null
  noteModal.lessonLabel = ''
  noteModal.note = ''
  noteModal.items = []
}

async function saveLessonNote() {
  if (!noteModal.studentId || !noteModal.lesson) return
  const current = cellRecord(noteModal.studentId, noteModal.lesson)
  savingNote.value = true
  try {
    const res = await http.put('/attendance/upsert', {
      lesson_id: noteModal.lesson.id,
      student_group_id: noteModal.studentId,
      lesson_date: `${noteModal.lesson.slot_date}T00:00:00`,
      status: current?.status || 'present',
      grade: current?.grade ?? null,
      note: noteModal.note || null,
    })
    records.value[recordKey(noteModal.studentId, noteModal.lesson)] = {
      grade: res.data.grade,
      note: res.data.note,
      status: res.data.status,
    }
    if (res.data.note) {
      attentionIds.value.add(noteModal.studentId)
    }
    closeNoteModal()
  } catch {
    // silent ui fallback
  } finally {
    savingNote.value = false
  }
}

</script>

<style scoped>
.progress-page {
  max-width: 100%;
}

.progress-page h1 {
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-purple);
}

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
  grid-column: 1 / -1;
}

.student-field label {
  display: none;
}

.student-field input {
  flex: 1;
}

.field select,
.field input {
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

.clear-btn {
  background: none;
  border: none;
  color: var(--brand-orange);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  padding: 8px 4px;
}

.clear-btn:hover {
  text-decoration: underline;
}

.group-info {
  margin-bottom: 14px;
}

.group-info h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #111827;
}

.group-info p {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 14px;
}

.matrix-wrap {
  overflow-x: auto;
  border: 1px solid #d1d5db;
}

.progress-table {
  width: 100%;
  min-width: 980px;
  border-collapse: collapse;
}

.progress-table th,
.progress-table td {
  border: 1px solid #d7dbe0;
  padding: 8px;
}

.progress-table thead th {
  background: #f7e2c8;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
}

.col-student {
  min-width: 240px;
  text-align: left;
}

.col-extra {
  min-width: 80px;
}

.col-lesson {
  min-width: 110px;
}

.student-cell {
  font-weight: 600;
}

.progress-table tbody tr:nth-child(odd) {
  background: #fff;
}

.progress-table tbody tr:nth-child(even) {
  background: #f8fafc;
}

.progress-table tbody tr.attention {
  background: #fde8ef;
}

.extra-cell,
.lesson-cell {
  text-align: center;
}

.cell-stack {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.grade-box {
  width: 28px;
  height: 28px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.grade-box.grade-5 {
  background: #dcfce7;
  border-color: #86efac;
  color: #166534;
}

.grade-box.grade-4 {
  background: #fef3c7;
  border-color: #fcd34d;
  color: #92400e;
}

.grade-box.grade-3 {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #991b1b;
}

.grade-box.grade-empty {
  color: #9ca3af;
}

.note-chip {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background: #f3f4f6;
  color: #4b5563;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.note-chip.active {
  background: #dbeafe;
  border-color: #93c5fd;
  color: #1d4ed8;
}

.grade-box:hover,
.note-chip:hover {
  filter: brightness(0.96);
}

.loading,
.empty-text {
  color: #6b7280;
}

.empty-text {
  text-align: center;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.35);
  z-index: 30;
}

.modal {
  width: min(560px, calc(100vw - 24px));
  background: #fff;
  border-radius: 14px;
  padding: 22px;
}

.modal h3 {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 700;
}

.note-editor label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
}

.note-editor textarea {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 10px;
  font: inherit;
}

.note-editor input {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 10px;
  font: inherit;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 320px;
  overflow: auto;
}

.note-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.note-item strong {
  font-size: 13px;
}

.note-item span,
.empty-notes {
  color: #6b7280;
  font-size: 14px;
}

.modal-error {
  margin-top: 12px;
  color: #b91c1c;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}

.btn-primary,
.btn-secondary {
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  background: #0f766e;
  color: #fff;
}

.btn-secondary {
  background: #e5e7eb;
}

@media (max-width: 1200px) {
  .filter-grid { gap: 12px 14px; }
}

@media (max-width: 768px) {
  .filter-grid { flex-direction: column; }
  .field { min-width: 100%; }
}
</style>
