<template>
  <div class="payment-page">
    <h1>Оплата обучения</h1>

    <div class="filters-card report-filters">
      <div class="filter-grid">
        <div class="field filter-field">
          <label>Филиал</label>
          <select v-model.number="filters.branch_id" @change="onBranchChange">
            <option :value="null">Все филиалы</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>

        <div class="field filter-field">
          <label>Преподаватель</label>
          <select v-model.number="filters.teacher_id" @change="onTeacherChange" :disabled="!filters.branch_id">
            <option :value="null">Все преподаватели</option>
            <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
          </select>
        </div>

        <div class="field filter-field">
          <label>Группа</label>
          <select v-model.number="filters.group_id" @change="loadPaymentMatrix" :disabled="!filters.teacher_id">
            <option :value="null">Выберите группу</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>

        <div class="field filter-field">
          <label>Год</label>
          <select v-model.number="filters.study_year" @change="loadPaymentMatrix">
            <option :value="2025">2025-2026</option>
            <option :value="2026">2026-2027</option>
          </select>
        </div>

        <div class="field checkbox-field">
          <label>
            <input type="checkbox" v-model="filters.only_debtors" @change="applyLocalFilters" />
            Только должники
          </label>
        </div>

        <div class="field filter-field student-field">
          <label>Студент</label>
          <input type="text" v-model.trim="filters.student_name" placeholder="Поиск по имени" @input="applyLocalFilters" />
          <button type="button" class="clear-btn" @click="filters.student_name = ''; applyLocalFilters()">Очистить</button>
        </div>
      </div>
    </div>

    <section v-if="selectedGroup" class="group-head">
      <h2>{{ selectedGroup.name }}</h2>
      <p class="price-line">Стоимость обучения: {{ formatRub(groupPrice) }}</p>
      <p class="meta-line">8 занятий по 50 минут</p>
    </section>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="selectedGroup" class="table-wrap">
      <table class="payment-table">
        <thead>
          <tr>
            <th class="col-num">№</th>
            <th class="col-name">ФИО ученика</th>
            <th v-for="col in monthColumns" :key="col.key">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in visibleRows" :key="row.student_group_id">
            <td class="center">{{ idx + 1 }}</td>
            <td>{{ row.student_name }}</td>
            <td v-for="col in monthColumns" :key="`${row.student_group_id}-${col.key}`" class="center">
              <button
                class="icon-dot"
                :class="statusClass(row, col.key)"
                :title="statusTitle(row, col.key)"
                @click="updateCellStatus(row, col.key)"
              >
                {{ statusSymbol(row, col.key) }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="hint">Выберите группу для просмотра оплаты.</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import http from '@/api/http'

type InvoiceLike = {
  id: number
  group_id: number
  student_group_id: number | null
  student_name: string
  period: string
  status: 'pending' | 'paid' | 'partial' | 'overdue' | 'refunded'
}

type MatrixRow = {
  student_group_id: number
  student_name: string
  byPeriod: Record<string, InvoiceLike | null>
}

const branches = ref<any[]>([])
const teachers = ref<any[]>([])
const groups = ref<any[]>([])
const students = ref<any[]>([])
const invoices = ref<InvoiceLike[]>([])
const selectedGroup = ref<any | null>(null)
const loading = ref(false)

const filters = reactive({
  branch_id: null as number | null,
  teacher_id: null as number | null,
  group_id: null as number | null,
  study_year: 2025,
  only_debtors: false,
  student_name: '',
})

const monthColumns = computed(() => {
  const y = filters.study_year
  return [
    { key: 'additional', label: 'Дополнит.' },
    { key: `${y}-09`, label: `Сентябрь ${y}` },
    { key: `${y}-10`, label: `Октябрь ${y}` },
    { key: `${y}-11`, label: `Ноябрь ${y}` },
    { key: `${y}-12`, label: `Декабрь ${y}` },
    { key: `${y + 1}-01`, label: `Январь ${y + 1}` },
    { key: `${y + 1}-02`, label: `Февраль ${y + 1}` },
    { key: `${y + 1}-03`, label: `Март ${y + 1}` },
    { key: `${y + 1}-04`, label: `Апрель ${y + 1}` },
    { key: `${y + 1}-05`, label: `Май ${y + 1}` },
  ]
})

const rows = computed<MatrixRow[]>(() => {
  const map = new Map<number, MatrixRow>()

  students.value.forEach((s) => {
    map.set(s.id, {
      student_group_id: s.id,
      student_name: s.student_name,
      byPeriod: Object.fromEntries(monthColumns.value.map((c) => [c.key, null])),
    })
  })

  invoices.value.forEach((inv) => {
    if (!inv.student_group_id || !map.has(inv.student_group_id)) return
    const row = map.get(inv.student_group_id)!
    if (inv.period in row.byPeriod) row.byPeriod[inv.period] = inv
  })

  return Array.from(map.values()).sort((a, b) => a.student_name.localeCompare(b.student_name, 'ru'))
})

const visibleRows = ref<MatrixRow[]>([])

const groupPrice = computed(() => selectedGroup.value?.course?.price_per_month ?? 3400)

onMounted(async () => {
  await loadBranches()
})

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
  selectedGroup.value = null
  visibleRows.value = []
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
  selectedGroup.value = null
  visibleRows.value = []
  if (!filters.teacher_id) return
  try {
    groups.value = (await http.get('/groups', { params: { branch_id: filters.branch_id, teacher_id: filters.teacher_id } })).data
  } catch {
    groups.value = []
  }
}

async function loadPaymentMatrix() {
  if (!filters.group_id) {
    selectedGroup.value = null
    visibleRows.value = []
    return
  }
  loading.value = true
  try {
    const [groupRes, studentsRes, invoicesRes] = await Promise.all([
      http.get(`/groups/${filters.group_id}`),
      http.get(`/groups/${filters.group_id}/students`),
      http.get('/invoices', { params: { group_id: filters.group_id } }),
    ])
    selectedGroup.value = groupRes.data
    students.value = studentsRes.data || []
    invoices.value = invoicesRes.data || []
    applyLocalFilters()
  } catch {
    selectedGroup.value = null
    students.value = []
    invoices.value = []
    visibleRows.value = []
  } finally {
    loading.value = false
  }
}

function applyLocalFilters() {
  let list = rows.value
  if (filters.student_name) {
    const q = filters.student_name.toLowerCase()
    list = list.filter((r) => r.student_name.toLowerCase().includes(q))
  }
  if (filters.only_debtors) {
    // В должники попадают все, у кого есть хотя бы один месяц без статуса paid,
    // включая пустую ячейку (счёт ещё не создан).
    list = list.filter((r) =>
      monthColumns.value
        .slice(1)
        .some((col) => r.byPeriod[col.key]?.status !== 'paid')
    )
  }
  visibleRows.value = list
}

function iconTitle(status: string) {
  if (status === 'paid') return 'Оплачено'
  if (status === 'partial') return 'Частичная / доп. правка'
  return 'Не оплачено'
}

function cellStatus(row: MatrixRow, key: string) {
  return row.byPeriod[key]?.status ?? null
}

function statusClass(row: MatrixRow, key: string) {
  const status = cellStatus(row, key)
  if (key === 'additional') {
    return status === 'paid' ? 'paid' : 'unpaid'
  }
  if (status === 'partial') return 'edit'
  if (status === 'paid') return 'paid'
  return 'unpaid'
}

function statusTitle(row: MatrixRow, key: string) {
  const status = cellStatus(row, key)
  return iconTitle(status || 'pending')
}

function statusSymbol(row: MatrixRow, key: string) {
  const status = cellStatus(row, key)
  if (key === 'additional') {
    return status === 'paid' ? '+' : '-'
  }
  if (status === 'paid') return '+'
  if (status === 'partial') return '✎'
  return '-'
}

function nextStatusForCell(row: MatrixRow, key: string): 'pending' | 'paid' | 'partial' {
  const status = cellStatus(row, key)
  if (key === 'additional') {
    return status === 'paid' ? 'pending' : 'paid'
  }
  if (status === 'paid') return 'pending'
  return 'paid'
}

async function updateCellStatus(row: MatrixRow, key: string) {
  if (!filters.group_id) return
  const nextStatus = nextStatusForCell(row, key)
  try {
    await http.post('/invoices/cell-status', {
      group_id: filters.group_id,
      student_group_id: row.student_group_id,
      student_name: row.student_name,
      period: key,
      status: nextStatus,
      amount: groupPrice.value,
    })
    await loadPaymentMatrix()
  } catch {
    // silent UI fallback
  }
}

function formatRub(value: number) {
  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0)) + ' руб.'
}
</script>

<style scoped>
.payment-page {
  max-width: 100%;
}

.payment-page h1 {
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

.field select,
.field input[type="text"],
.filter-field select,
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

.checkbox-field label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1.5px solid #ffe3cf;
  border-radius: 8px;
  background: #fff;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  text-transform: none;
  letter-spacing: 0;
}

.checkbox-field input {
  margin: 0;
}

.student-field {
  flex-direction: row;
  align-items: flex-end;
  gap: 8px;
  flex: 1;
  grid-column: 1 / -1;
  min-width: 240px;
}

.student-field label {
  display: none;
}

.student-field input {
  flex: 1;
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

.group-head h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #111827;
}

.price-line {
  margin: 3px 0 0;
  color: #6b7280;
  font-size: 12px;
}

.meta-line {
  margin: 2px 0 14px;
  color: #6b7280;
  font-size: 12px;
  font-style: italic;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid #d1d5db;
}

.payment-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1180px;
}

.payment-table th,
.payment-table td {
  border: 1px solid #d7dbe0;
  padding: 8px;
}

.payment-table thead th {
  background: #f7e2c8;
  text-align: center;
  font-weight: 700;
  font-size: 13px;
}

.payment-table tbody tr:nth-child(odd) {
  background: #ffffff;
}

.payment-table tbody tr:nth-child(even) {
  background: #f8fafc;
}

.col-num {
  width: 52px;
}

.col-name {
  min-width: 220px;
}

.center {
  text-align: center;
}

.icon-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  font-size: 12px;
  line-height: 20px;
  font-weight: 700;
  cursor: pointer;
  color: #fff;
  padding: 0;
  transition: filter 0.15s ease;
}

.icon-dot:hover {
  filter: brightness(0.9);
}

.icon-dot.paid {
  background: #1ea853;
}

.icon-dot.unpaid {
  background: #db3a34;
}

.icon-dot.edit {
  background: #eab308;
}

.hint,
.loading {
  color: #6b7280;
  margin-top: 12px;
}

.hint {
  text-align: center;
}

@media (max-width: 1200px) {
  .filter-grid { gap: 12px 14px; }
}

@media (max-width: 768px) {
  .filter-grid { flex-direction: column; }
  .field { min-width: 100%; }
}
</style>
