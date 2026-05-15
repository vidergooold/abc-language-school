<template>
  <div class="reports-page">
    <div class="page-header">
      <h1>📊 Отчёты</h1>
    </div>

    <div class="filters-card">
      <div class="filter-grid">
        <div class="field filter-field">
          <label>Период</label>
          <input type="month" v-model="filters.period" />
        </div>
        <div class="field filter-field">
          <label>Группа</label>
          <select v-model.number="filters.group_id">
            <option :value="null">Все группы</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="field filter-field">
          <label>Преподаватель</label>
          <select v-model.number="filters.teacher_id">
            <option :value="null">Все преподаватели</option>
            <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
          </select>
        </div>
        <div class="field filter-field">
          <label>Ученик</label>
          <input type="text" v-model.trim="filters.student_name" placeholder="Поиск по имени" />
        </div>
      </div>
    </div>

    <div class="report-panel">
      <h3>Тип отчёта</h3>
      <div class="report-actions">
        <button
          v-for="r in reportTypes"
          :key="r.key"
          type="button"
          class="btn-report"
          :class="{ active: currentReportType === r.key }"
          @click="loadReport(r.key)"
        >
          {{ r.label }}
        </button>
      </div>

      <div v-if="reportLoading" class="loading">Загрузка отчёта...</div>

      <template v-else-if="reportRows.length">
        <div class="report-export">
          <button type="button" class="btn-export" @click="exportReport('excel')">⬇ Экспорт Excel</button>
          <button type="button" class="btn-export" @click="exportReport('pdf')">⬇ Экспорт PDF</button>
        </div>
        <div class="table-wrap">
          <table class="report-table">
            <thead>
              <tr>
                <th v-for="col in reportColumns" :key="col">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in reportRows" :key="idx">
                <td v-for="col in reportColumns" :key="`${idx}-${col}`">{{ row[col] ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <div v-else-if="hasLoaded" class="empty-report">
        Нет данных для выбранных фильтров.
      </div>
      <div v-else class="empty-report">
        Выберите тип отчёта для загрузки данных.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import http from '@/api/http'

const groups = ref<any[]>([])
const teachers = ref<any[]>([])
const reportLoading = ref(false)
const hasLoaded = ref(false)
const currentReportType = ref('')
const reportRows = ref<any[]>([])
const reportColumns = ref<string[]>([])

const filters = reactive({
  period: '',
  group_id: null as number | null,
  teacher_id: null as number | null,
  student_name: '',
})

const reportTypes = [
  { key: 'financial', label: 'Финансовый' },
  { key: 'attendance', label: 'Посещаемость' },
  { key: 'lessons-conducted', label: 'Проведённые занятия' },
  { key: 'teacher-load', label: 'Нагрузка преподавателей' },
]

onMounted(async () => {
  try {
    const [groupsRes, teachersRes] = await Promise.all([
      http.get('/groups', { params: { active_only: false } }),
      http.get('/teachers'),
    ])
    groups.value = Array.isArray(groupsRes.data) ? groupsRes.data : []
    teachers.value = Array.isArray(teachersRes.data) ? teachersRes.data : []
  } catch {
    groups.value = []
    teachers.value = []
  }
})

function reportParams() {
  return {
    period: filters.period || undefined,
    group_id: filters.group_id || undefined,
    teacher_id: filters.teacher_id || undefined,
    student_name: filters.student_name || undefined,
  }
}

async function loadReport(type: string) {
  currentReportType.value = type
  reportLoading.value = true
  hasLoaded.value = false
  try {
    const res = await http.get(`/reports/${type}`, { params: reportParams() })
    const data = res.data?.data ?? res.data
    const rows = Array.isArray(data?.items)
      ? data.items
      : Array.isArray(data)
        ? data
        : [data]
    reportRows.value = rows
    reportColumns.value = Array.from(new Set(rows.flatMap((row: any) => Object.keys(row || {}))))
  } catch {
    reportRows.value = []
    reportColumns.value = []
  } finally {
    reportLoading.value = false
    hasLoaded.value = true
  }
}

async function exportReport(format: 'excel' | 'pdf') {
  if (!currentReportType.value) return
  try {
    const response = await http.get(`/reports/${currentReportType.value}`, {
      params: { ...reportParams(), export_format: format },
      responseType: 'blob',
    })
    const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/octet-stream' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentReportType.value}.${format === 'excel' ? 'csv' : 'pdf'}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch {
    // silent
  }
}
</script>

<style scoped>
.reports-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); }
.page-header { margin-bottom: 20px; }

.filters-card {
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

.field label {
  font-size: 12px;
  font-weight: 700;
  color: var(--brand-orange);
  text-transform: uppercase;
  letter-spacing: .05em;
}

.field select,
.field input[type="text"],
.field input[type="month"] {
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

.report-panel {
  background: #fff7f0;
  border: 1px solid #ffe3cf;
  border-radius: 14px;
  padding: 20px;
}

.report-panel h3 {
  margin: 0 0 12px;
  color: var(--brand-purple);
  font-size: 18px;
  font-weight: 700;
}

.report-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.btn-report {
  background: #fff;
  border: 1.5px solid #ffe3cf;
  color: var(--brand-purple);
  font-size: 14px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-report:hover {
  background: #ffe3cf;
  border-color: var(--brand-orange);
}

.btn-report.active {
  background: var(--brand-orange);
  color: #fff;
  border-color: var(--brand-orange);
}

.report-export {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.btn-export {
  background: none;
  border: 1.5px solid var(--brand-orange);
  color: var(--brand-orange);
  font-size: 13px;
  font-weight: 700;
  padding: 7px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-export:hover {
  background: var(--brand-orange);
  color: #fff;
}

.loading {
  color: #6b7280;
  padding: 12px 0;
}

.empty-report {
  color: #9ca3af;
  font-size: 14px;
  padding: 16px 0;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid #ffe3cf;
  border-radius: 12px;
  background: #fff;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.report-table th {
  background: var(--brand-orange);
  color: #fff;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  white-space: nowrap;
}

.report-table td {
  padding: 9px 12px;
  border-bottom: 1px solid #ffe3cf;
}

.report-table tr:hover td {
  background: #fff7f0;
}

@media (max-width: 768px) {
  .filter-grid { flex-direction: column; }
  .field { min-width: 100%; }
}
</style>
