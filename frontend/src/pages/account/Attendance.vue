<template>
  <div class="attendance-page">
    <h1>✅ Посещаемость</h1>

    <!-- Скелетон -->
    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-card" v-for="n in 5" :key="n"></div>
    </div>

    <template v-else-if="records.length">
      <!-- Статистика сверху -->
      <div class="stats-bar">
        <div class="stat" v-for="s in statCards" :key="s.label">
          <span class="stat-value" :style="{ color: s.color }">{{ s.value }}</span>
          <span class="stat-label">{{ s.label }}</span>
        </div>
        <div class="stat">
          <span class="stat-value" style="color: var(--brand-orange)">
            {{ attendanceRate }}%
          </span>
          <span class="stat-label">Посещаемость</span>
        </div>
      </div>

      <!-- Прогресс-бар -->
      <div class="progress-wrap">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: attendanceRate + '%' }"></div>
        </div>
        <span class="progress-label">{{ attendanceRate }}% занятий посещено</span>
      </div>

      <!-- Фильтр по статусу -->
      <div class="filter-row">
        <button
          v-for="f in filters"
          :key="f.key"
          class="filter-btn"
          :class="{ active: activeFilter === f.key }"
          @click="activeFilter = f.key"
        >{{ f.label }} <span class="filter-count">{{ f.count }}</span></button>
      </div>

      <!-- Список -->
      <div class="records-list">
        <div
          class="record-card"
          v-for="r in filteredRecords"
          :key="r.id"
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

    <!-- Пустое состояние -->
    <div v-else class="no-records">
      <div class="no-records-icon">✅</div>
      <p>Записей о посещаемости пока нет.</p>
      <p class="no-records-hint">Они появятся здесь, когда преподаватель начнёт отмечать занятия.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

const loading = ref(true)
const records = ref<any[]>([])
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
  { label: 'Был на занятии',      value: counts.value.present, color: '#22a55b' },
  { label: 'Отсутствовал',          value: counts.value.absent,  color: '#e03c3c' },
  { label: 'Опоздал',              value: counts.value.late,    color: '#d9860a' },
  { label: 'Уважит. причина',     value: counts.value.excused, color: '#5b8dd9' },
])

const filters = computed(() => [
  { key: 'all',     label: 'Все',              count: records.value.length },
  { key: 'present', label: 'Присутствовал',  count: counts.value.present },
  { key: 'absent',  label: 'Отсутствовал',   count: counts.value.absent  },
  { key: 'late',    label: 'Опоздал',          count: counts.value.late    },
  { key: 'excused', label: 'Уважит. прич.',   count: counts.value.excused },
])

const filteredRecords = computed(() =>
  activeFilter.value === 'all'
    ? records.value
    : records.value.filter(r => r.status === activeFilter.value)
)

function statusLabel(s: string): string {
  return { present: 'Был', absent: 'Не был', late: 'Опоздал', excused: 'Уваж. прич.' }[s] ?? s
}

function formatDate(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric', weekday: 'short' })
}

onMounted(async () => {
  try {
    const res = await http.get('/attendance/my')
    records.value = res.data
  } catch {
    records.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.attendance-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 24px; }

/* Статистика */
.stats-bar {
  display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px;
}
.stat {
  background: #fff7f0; border-radius: 12px; padding: 14px 20px;
  display: flex; flex-direction: column; gap: 4px;
  border: 1.5px solid #ffe3cf; min-width: 110px; text-align: center;
}
.stat-value { font-size: 28px; font-weight: 700; }
.stat-label { font-size: 12px; color: #888; }

/* Прогресс */
.progress-wrap { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.progress-bar { flex: 1; height: 10px; background: #f0ece8; border-radius: 999px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--brand-orange); border-radius: 999px; transition: width 0.6s ease; }
.progress-label { font-size: 14px; color: #888; white-space: nowrap; }

/* Фильтр */
.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.filter-btn {
  padding: 6px 14px; border-radius: 999px; border: 2px solid #ffe3cf;
  background: #fff; font-size: 13px; font-weight: 600; color: var(--brand-purple);
  cursor: pointer; transition: all 0.18s; display: flex; align-items: center; gap: 6px;
}
.filter-btn:hover { background: #ffe3cf; }
.filter-btn.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }
.filter-count {
  background: rgba(255,255,255,0.35); border-radius: 999px;
  padding: 1px 7px; font-size: 12px;
}
.filter-btn.active .filter-count { background: rgba(255,255,255,0.3); }

/* Список */
.records-list { display: flex; flex-direction: column; gap: 10px; }
.record-card {
  display: flex; align-items: center; gap: 14px;
  background: #fff7f0; border-radius: 12px;
  padding: 14px 18px; border-left: 5px solid #ddd;
  transition: box-shadow 0.2s;
}
.record-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.07); }

/* Цвета по статусу */
.status-present { border-left-color: #22a55b; }
.status-absent  { border-left-color: #e03c3c; background: #fff5f5; }
.status-late    { border-left-color: #d9860a; background: #fffaf0; }
.status-excused { border-left-color: #5b8dd9; background: #f0f5ff; }

.record-status-dot {
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
  background: currentColor;
}
.status-present .record-status-dot { background: #22a55b; }
.status-absent  .record-status-dot { background: #e03c3c; }
.status-late    .record-status-dot { background: #d9860a; }
.status-excused .record-status-dot { background: #5b8dd9; }

.record-info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.record-date { font-size: 15px; font-weight: 600; color: #333; }
.record-note { font-size: 13px; color: #888; }

.record-badge {
  font-size: 13px; font-weight: 700; padding: 4px 12px;
  border-radius: 999px; white-space: nowrap;
}
.status-present .record-badge { background: #e6f9ef; color: #22a55b; }
.status-absent  .record-badge { background: #fdeaea; color: #e03c3c; }
.status-late    .record-badge { background: #fff3dc; color: #d9860a; }
.status-excused .record-badge { background: #e8f0fc; color: #5b8dd9; }

.no-filter { text-align: center; color: #bbb; padding: 20px; font-size: 15px; }

/* Пустое */
.no-records {
  text-align: center; padding: 48px; background: #fff7f0;
  border-radius: 14px; color: #888;
}
.no-records-icon { font-size: 48px; margin-bottom: 12px; }
.no-records p { font-size: 16px; margin-bottom: 6px; }
.no-records-hint { font-size: 14px; color: #bbb; }

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
}
</style>
