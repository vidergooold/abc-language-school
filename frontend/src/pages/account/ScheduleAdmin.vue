<template>
  <div class="schedule-admin">
    <div class="page-header">
      <h1>🗓 Расписание (управление)</h1>
      <RouterLink to="/courses" class="btn-public">🔗 Публичное расписание ↗</RouterLink>
    </div>

    <div class="filters">
      <input v-model="search" type="text" placeholder="🔍 Поиск по школе / учителю / уровню" />
      <select v-model="filterDay">
        <option value="">Все дни</option>
        <option v-for="d in days" :key="d.key" :value="d.key">{{ d.label }}</option>
      </select>
    </div>

    <!-- Скелетон -->
    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-row" v-for="n in 8" :key="n"></div>
    </div>

    <template v-else-if="filtered.length">
      <div class="count-label">Показано: {{ filtered.length }} из {{ schedule.length }}</div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Школа / место</th>
              <th>Учитель</th>
              <th>Дни</th>
              <th>Время</th>
              <th>Уровень</th>
              <th>Кабинет</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filtered" :key="item.id">
              <td class="col-school">{{ item.school || item.group_name || '—' }}</td>
              <td>{{ item.teacher || item.teacher_name || '—' }}</td>
              <td class="col-days">{{ item.days || item.day_of_week || '—' }}</td>
              <td class="col-time">{{ item.time || (formatTime(item.time_start) + '–' + formatTime(item.time_end)) }}</td>
              <td><span class="level-badge">{{ item.level || item.group_name || '—' }}</span></td>
              <td>{{ item.room || item.classroom_name || '—' }}</td>
              <td>
                <span class="status-badge" :class="'s-' + (item.status || 'scheduled')">
                  {{ lessonStatus(item.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon">🗓</div>
      <p>{{ schedule.length ? 'Ничего не найдено по фильтру.' : 'Расписание пока не добавлено.' }}</p>
      <p class="empty-hint">Расписание формируется из данных в системе через раздел групп и занятий.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import http from '@/api/http'

const loading = ref(true)
const schedule = ref<any[]>([])
const search = ref('')
const filterDay = ref('')

const days = [
  { key: 'monday',    label: 'Понедельник' },
  { key: 'tuesday',   label: 'Вторник' },
  { key: 'wednesday', label: 'Среда' },
  { key: 'thursday',  label: 'Четверг' },
  { key: 'friday',    label: 'Пятница' },
  { key: 'saturday',  label: 'Суббота' },
]

const filtered = computed(() =>
  schedule.value
    .filter(i => !search.value ||
      (i.school || i.group_name || '').toLowerCase().includes(search.value.toLowerCase()) ||
      (i.teacher || i.teacher_name || '').toLowerCase().includes(search.value.toLowerCase()) ||
      (i.level || '').toLowerCase().includes(search.value.toLowerCase())
    )
    .filter(i => !filterDay.value ||
      (i.day_of_week || i.days || '').toLowerCase().includes(filterDay.value.toLowerCase())
    )
)

function formatTime(t: string): string {
  if (!t) return ''
  return t.slice(0, 5)
}

function lessonStatus(s: string): string {
  return { scheduled: 'По расписанию', completed: 'Проведено', cancelled: 'Отменено', rescheduled: 'Перенесено' }[s] ?? (s || 'По расписанию')
}

onMounted(async () => {
  try {
    const res = await http.get('/schedule')
    schedule.value = Array.isArray(res.data) ? res.data : []
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
.btn-public { background: #f5f0ff; color: var(--brand-purple); border: 1.5px solid #e8deff; padding: 9px 18px; border-radius: 10px; text-decoration: none; font-size: 14px; font-weight: 600; transition: background 0.2s; }
.btn-public:hover { background: #e8deff; }

.filters { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 180px; outline: none; }
.filters input:focus, .filters select:focus { border-color: var(--brand-orange); }

.count-label { font-size: 13px; color: #aaa; margin-bottom: 12px; }

/* Skeleton */
.skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.skeleton-row { height: 46px; border-radius: 10px; background: linear-gradient(90deg,#fff0e8 25%,#ffe8d6 50%,#fff0e8 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; }
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }

.table-wrap { overflow-x: auto; border-radius: 14px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { background: var(--brand-orange); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #ffe3cf; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #fff7f0; }
.col-school { font-weight: 600; color: #333; }
.col-days { color: var(--brand-orange); font-weight: 600; white-space: nowrap; }
.col-time { white-space: nowrap; }
.level-badge { background: var(--brand-orange); color: #fff; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }

.status-badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }
.s-scheduled   { background: #e8f4ff; color: #2a7bbf; }
.s-completed   { background: #e6f9ef; color: #22a55b; }
.s-cancelled   { background: #fdeaea; color: #e03c3c; }
.s-rescheduled { background: #fff3dc; color: #d9860a; }

.empty-state { text-align: center; padding: 48px; background: #fff7f0; border-radius: 14px; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { font-size: 16px; color: #888; margin-bottom: 6px; }
.empty-hint { font-size: 14px; color: #bbb; }
</style>
