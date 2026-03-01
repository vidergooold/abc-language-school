<template>
  <div class="schedule-page">
    <h1>Моё расписание</h1>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="schedule.length" class="schedule-list">
      <div class="schedule-card" v-for="item in schedule" :key="item.id">
        <div class="schedule-day">{{ item.day }}</div>
        <div class="schedule-info">
          <h3 class="schedule-course">{{ item.course }}</h3>
          <p class="schedule-time">🕐 {{ item.time }}</p>
          <p class="schedule-teacher">👤 {{ item.teacher }}</p>
          <p class="schedule-place">📍 {{ item.place }}</p>
        </div>
        <span class="schedule-level">{{ item.level }}</span>
      </div>
    </div>

    <div v-else class="no-schedule">
      <p>У вас пока нет активных курсов.</p>
      <RouterLink to="/enroll" class="btn-enroll">Записаться на курс →</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useEnrollmentsStore } from '@/stores/enrollments'

const loading = ref(true)

// Пример расписания — в реальном проекте придёт из API
const schedule = ref([
  {
    id: 1,
    day: 'Понедельник / Среда / Пятница',
    course: 'Английский язык (уровень B1)',
    time: '18:00 – 19:30',
    teacher: 'Петрова М.С.',
    place: 'ул. Бориса Богаткова, 208/2, офис 5',
    level: 'B1',
  },
])

onMounted(() => {
  // здесь можно подключить API
  setTimeout(() => { loading.value = false }, 300)
})
</script>

<style scoped>
.schedule-page h1 {
  font-size: var(--font-size-h2);
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 24px;
}
.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.schedule-card {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  background: #fff7f0;
  border-radius: 14px;
  padding: 20px;
  border-left: 5px solid var(--brand-orange);
  transition: box-shadow 0.2s, transform 0.2s;
}
.schedule-card:hover {
  box-shadow: 0 6px 20px rgba(255,107,45,0.15);
  transform: translateY(-2px);
}
.schedule-day {
  font-size: 14px;
  font-weight: 700;
  color: var(--brand-orange);
  min-width: 200px;
  padding-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.schedule-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.schedule-course {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-purple);
  margin: 0;
}
.schedule-time,
.schedule-teacher,
.schedule-place {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
}
.schedule-level {
  background: var(--brand-orange);
  color: #fff;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  align-self: flex-start;
  flex-shrink: 0;
}
.no-schedule {
  background: #fff7f0;
  border-radius: 14px;
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 16px;
}
.btn-enroll {
  display: inline-block;
  margin-top: 16px;
  padding: 12px 28px;
  background: var(--brand-orange);
  color: #fff;
  border-radius: 999px;
  font-weight: 700;
  font-size: 16px;
  text-decoration: none;
  transition: background 0.2s, transform 0.15s;
}
.btn-enroll:hover {
  background: var(--brand-red);
  transform: translateY(-2px);
}
.loading {
  color: var(--text-secondary);
  font-size: 16px;
  padding: 40px;
  text-align: center;
}
@media (max-width: 768px) {
  .schedule-card {
    flex-direction: column;
    gap: 12px;
  }
  .schedule-day { min-width: unset; }
}
