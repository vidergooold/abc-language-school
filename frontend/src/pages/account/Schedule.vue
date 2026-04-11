<template>
  <div class="schedule-page">
    <h1>🗓 Моё расписание</h1>

    <!-- Скелетон -->
    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-card" v-for="n in 4" :key="n"></div>
    </div>

    <template v-else-if="schedule.length">
      <!-- Фильтр по дням -->
      <div class="day-filter">
        <button
          v-for="d in days"
          :key="d.key"
          class="day-btn"
          :class="{ active: activeDay === d.key }"
          @click="activeDay = d.key"
        >{{ d.label }}</button>
      </div>

      <div class="schedule-list">
        <div
          class="schedule-card"
          v-for="item in filteredSchedule"
          :key="item.id"
        >
          <div class="schedule-day">{{ item.day_of_week }}</div>
          <div class="schedule-info">
            <h3 class="schedule-course">{{ item.course_name || item.group_name || 'Занятие' }}</h3>
            <p class="schedule-time">🕐 {{ formatTime(item.time_start) }}–{{ formatTime(item.time_end) }}</p>
            <p v-if="item.teacher_name" class="schedule-teacher">👤 {{ item.teacher_name }}</p>
            <p v-if="item.classroom_name" class="schedule-place">📍 {{ item.classroom_name }}</p>
            <span v-if="item.status === 'rescheduled'" class="badge-rescheduled">Перенесено</span>
          </div>
          <span class="schedule-level">{{ item.level || item.group_name || '—' }}</span>
        </div>
        <p v-if="!filteredSchedule.length" class="no-day">В этот день занятий нет</p>
      </div>
    </template>

    <div v-else class="no-schedule">
      <div class="no-schedule-icon">🗓</div>
      <p>У вас пока нет активных курсов.</p>
      <RouterLink to="/enroll" class="btn-enroll">Записаться на курс →</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const loading = ref(true)
const schedule = ref<any[]>([])

const days = [
  { key: 'all', label: 'Все' },
  { key: 'Пн', label: 'Пн' },
  { key: 'Вт', label: 'Вт' },
  { key: 'Ср', label: 'Ср' },
  { key: 'Чт', label: 'Чт' },
  { key: 'Пт', label: 'Пт' },
  { key: 'Сб', label: 'Сб' },
]
const activeDay = ref('all')

const filteredSchedule = computed(() => {
  if (activeDay.value === 'all') return schedule.value
  return schedule.value.filter(item =>
    (item.day_of_week || '').startsWith(activeDay.value)
  )
})

function formatTime(t: string): string {
  if (!t) return ''
  return t.slice(0, 5) // HH:MM
}

onMounted(async () => {
  try {
    const isStaff = ['admin', 'teacher'].includes(auth.user?.role || '')
    const endpoint = isStaff ? '/schedule' : '/schedule/my'
    const res = await http.get(endpoint)
    schedule.value = res.data
  } catch {
    schedule.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.schedule-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 24px; }

/* Фильтр */
.day-filter { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
.day-btn {
  padding: 6px 16px; border-radius: 999px; border: 2px solid #ffe3cf;
  background: #fff; font-size: 14px; font-weight: 600; color: var(--brand-purple);
  cursor: pointer; transition: all 0.18s;
}
.day-btn:hover { background: #ffe3cf; }
.day-btn.active { background: var(--brand-orange); color: #fff; border-color: var(--brand-orange); }

/* Карточки */
.schedule-list { display: flex; flex-direction: column; gap: 16px; }
.schedule-card {
  display: flex; align-items: flex-start; gap: 20px;
  background: #fff7f0; border-radius: 14px; padding: 20px;
  border-left: 5px solid var(--brand-orange);
  transition: box-shadow 0.2s, transform 0.2s;
}
.schedule-card:hover { box-shadow: 0 6px 20px rgba(255,107,45,0.15); transform: translateY(-2px); }
.schedule-day {
  font-size: 13px; font-weight: 700; color: var(--brand-orange);
  min-width: 40px; padding-top: 2px; text-transform: uppercase; letter-spacing: 0.04em;
}
.schedule-info { flex: 1; display: flex; flex-direction: column; gap: 5px; }
.schedule-course { font-size: 18px; font-weight: 700; color: var(--brand-purple); margin: 0; }
.schedule-time, .schedule-teacher, .schedule-place { font-size: 14px; color: var(--text-secondary, #666); margin: 0; }
.schedule-level {
  background: var(--brand-orange); color: #fff;
  padding: 4px 12px; border-radius: 999px;
  font-size: 13px; font-weight: 700; align-self: flex-start; flex-shrink: 0;
}
.badge-rescheduled {
  display: inline-block; margin-top: 4px;
  background: #fff3cd; color: #856404;
  padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
}

/* Пустое состояние */
.no-schedule {
  background: #fff7f0; border-radius: 14px; padding: 48px;
  text-align: center; color: var(--text-secondary, #888);
}
.no-schedule-icon { font-size: 48px; margin-bottom: 12px; }
.no-schedule p { font-size: 16px; margin-bottom: 20px; }
.btn-enroll {
  display: inline-block; padding: 12px 28px;
  background: var(--brand-orange); color: #fff;
  border-radius: 999px; font-weight: 700; font-size: 16px; text-decoration: none;
}
.no-day { color: var(--text-secondary, #aaa); font-size: 15px; padding: 20px 0; text-align: center; }

/* Скелетон */
.skeleton-list { display: flex; flex-direction: column; gap: 16px; }
.skeleton-card {
  height: 100px; border-radius: 14px;
  background: linear-gradient(90deg, #fff0e8 25%, #ffe8d6 50%, #fff0e8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer { 0% { background-position: -200% 0 } 100% { background-position: 200% 0 } }

@media (max-width: 768px) {
  .schedule-card { flex-direction: column; gap: 12px; }
  .schedule-day { min-width: unset; }
}
</style>
