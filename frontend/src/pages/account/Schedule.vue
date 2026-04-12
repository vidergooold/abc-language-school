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
import http from '@/api/http'

const loading = ref(true)

// Полное расписание из данных школы (загружается из API или хранится как справочник)
const allSchedule = [
  { id: 1, day: 'Пн / Ср', course: 'Английский язык AS1', time: '12:20–13:10 / 11:50–12:40', teacher: 'Лукьянова С.Я.', place: '5 гимназия, каб. 109', level: 'AS1' },
  { id: 2, day: 'Вт / Чт', course: 'Английский язык FH1', time: '12:00–12:50', teacher: 'Лукьянова С.Я.', place: '121 школа, каб. 214', level: 'FH1' },
  { id: 3, day: 'Вт / Чт', course: 'Английский язык AS1', time: '13:10–14:00', teacher: 'Лукьянова С.Я.', place: '121 школа, каб. 214', level: 'AS1' },
  { id: 4, day: 'Пн / Ср', course: 'Английский язык AS2', time: '11:00–12:00 / 10:30–11:30', teacher: 'Белова А.А.', place: '7 гимназия, каб. 119', level: 'AS2' },
  { id: 5, day: 'Пн / Ср', course: 'Английский язык FH1', time: '12:30–13:20 / 11:30–12:20', teacher: 'Белова А.А.', place: '7 гимназия, каб. 119', level: 'FH1' },
  { id: 6, day: 'Вт / Чт', course: 'Английский язык GWB1', time: '15:30–17:00 / 15:15–16:45', teacher: 'Белова А.А.', place: 'ЛИТ, каб. библ., 116', level: 'GWB1' },
  { id: 7, day: 'Пн / Чт', course: 'Английский язык FH1', time: '12:00–12:50', teacher: 'Зудяева Н.А.', place: '56 школа, каб. 3/10', level: 'FH1' },
  { id: 8, day: 'Пн / Чт', course: 'Английский язык AS1', time: '13:00–13:50', teacher: 'Зудяева Н.А.', place: '56 школа, каб. 3/10', level: 'AS1' },
  { id: 9, day: 'Пн / Чт', course: 'Английский язык AS1', time: '9:50–10:40', teacher: 'Осинина С.Н.', place: '11 гимназия, каб. 113', level: 'AS1' },
  { id: 10, day: 'Пн / Чт', course: 'Английский язык AS2', time: '10:50–11:50', teacher: 'Осинина С.Н.', place: '11 гимназия, каб. 113', level: 'AS2' },
  { id: 11, day: 'Пн / Ср', course: 'Английский язык GWB1+', time: '11:35–13:05', teacher: 'Пасикан А.С.', place: '11 гимназия, каб. 114', level: 'GWB1+' },
  { id: 12, day: 'Вт / Чт', course: 'Английский язык GWA2', time: '12:00–13:15', teacher: 'Пасикан А.С.', place: '11 гимназия, каб. 114', level: 'GWA2' },
  { id: 13, day: 'Пн / Пт', course: 'Английский язык AS1', time: '10:20–11:10', teacher: 'Фомина С.О.', place: '217 школа, каб. 314А', level: 'AS1' },
  { id: 14, day: 'Пн / Пт', course: 'Английский язык AS2', time: '14:20–15:20', teacher: 'Фомина С.О.', place: '217 школа, каб. 314А', level: 'AS2' },
  { id: 15, day: 'Пн / Ср', course: 'Английский язык AS1', time: '10:30–11:15', teacher: 'Колесник Л.Н.', place: '218 школа, каб. АВС', level: 'AS1' },
  { id: 16, day: 'Вт / Чт', course: 'Английский язык AS2', time: '10:10–11:10', teacher: 'Колесник Л.Н.', place: '218 школа, каб. АВС', level: 'AS2' },
  { id: 17, day: 'Пн / Ср', course: 'Английский язык FH1', time: '12:00–12:50', teacher: 'Данилова М.А.', place: '221 школа, каб. 128/311', level: 'FH1' },
  { id: 18, day: 'Вт / Чт', course: 'Английский язык FH1', time: '12:20–12:50 / 11:35–12:45', teacher: 'Данилова М.А.', place: '188 школа, каб. АВС', level: 'FH1' },
  { id: 19, day: 'Пн / Пт', course: 'Английский язык FH1', time: '11:50–12:40 / 11:15–12:05', teacher: 'Позднякова В.С.', place: '188 школа, каб. АВС', level: 'FH1' },
  { id: 20, day: 'Пн / Пт', course: 'Английский язык GWB1', time: '16:05–17:35', teacher: 'Позднякова В.С.', place: '188 школа, каб. АВС', level: 'GWB1' },
  { id: 21, day: 'Пн / Ср', course: 'Английский язык AS2', time: '10:30–11:30', teacher: 'Рубе Д.В.', place: '186 школа, каб. 409', level: 'AS2' },
  { id: 22, day: 'Пн / Ср', course: 'Английский язык AS1', time: '9:00–9:50', teacher: 'Куцых М.Е.', place: '199 школа, вахта', level: 'AS1' },
  { id: 23, day: 'Вт / Чт', course: 'Английский язык GWB1+', time: '9:15–10:45', teacher: 'Пасикан А.С.', place: 'Офис, каб. 4', level: 'GWB1+' },
  { id: 24, day: 'Пн / Ср', course: 'Английский язык GWB1', time: '19:15–20:45', teacher: 'Рубе Д.В.', place: 'Офис', level: 'GWB1' },
  { id: 25, day: 'Вт / Чт', course: 'Английский язык AS3', time: '10:10–11:10', teacher: 'Евдокимова П.Е.', place: 'Офис, каб. 2', level: 'AS3' },
  { id: 26, day: 'Пн / Ср', course: 'Английский язык GWB2+', time: '17:20–18:50', teacher: 'Караваева А.Д.', place: 'Офис, каб. 2', level: 'GWB2+' },
  { id: 27, day: 'Вт / Чт', course: 'Английский язык GWB1', time: '9:30–11:10', teacher: 'Митина О.С.', place: 'Офис, каб. 3', level: 'GWB1' },
  { id: 28, day: 'Вт / Чт', course: 'Английский язык FH1', time: '18:00–18:50', teacher: 'Федорова А.В.', place: 'Офис, каб. 5', level: 'FH1' },
  { id: 29, day: 'Пн / Ср', course: 'Английский язык FH1', time: '11:35–12:25', teacher: 'Федорова А.В.', place: '11 школа, каб. 203', level: 'FH1' },
  { id: 30, day: 'Пн / Ср', course: 'Английский язык FH1', time: '12:10–13:00', teacher: 'Тихвинская В.О.', place: 'ЭКЛ, Крылова 44', level: 'FH1' },
  { id: 31, day: 'Вт / Чт', course: 'Английский язык AS1', time: '12:10–13:00', teacher: 'Походная А.И.', place: 'ЭКЛ, каб. АВС', level: 'AS1' },
  { id: 32, day: 'Пн', course: 'Английский язык FH1', time: '12:10–13:00', teacher: 'Родина Т.П.', place: '9 гимназия, каб. 37', level: 'FH1' },
  { id: 33, day: 'Пт', course: 'Английский язык FH1', time: '12:10–13:00', teacher: 'Козлова Е.Г.', place: '9 гимназия, каб. 41', level: 'FH1' },
  { id: 34, day: 'Вт / Ср', course: 'Английский язык AS1', time: '18:00–18:50 / 11:10–12:00', teacher: 'Переведенцева А.А.', place: '155 школа, каб. 426', level: 'AS1' },
  { id: 35, day: 'Пн / Ср', course: 'Английский язык GWB1+', time: '9:30–11:00', teacher: 'Темлякова А.М.', place: '216 школа, каб. 317/1', level: 'GWB1+' },
  { id: 36, day: 'Пн / Ср', course: 'Английский язык GWB1', time: '9:45–11:15', teacher: 'Арнгольд В.Е.', place: '216 школа, каб. 410', level: 'GWB1' },
  { id: 37, day: 'Пт', course: 'Английский язык (1–2 класс)', time: '12:10–14:00', teacher: 'Быковская М.Э.', place: '13 школа, каб. 18', level: 'Нач.' },
  { id: 38, day: 'Сб', course: 'Английский язык (3 класс)', time: '11:00–13:10', teacher: 'Турабова Д.Д.', place: '222 школа, каб. 191', level: 'Нач.' },
  { id: 39, day: 'Пн / Ср', course: 'Английский язык (2–1 класс)', time: '11:30–13:20', teacher: 'Винокурова Е.А.', place: '195 школа, каб. 229', level: 'Нач.' },
  { id: 40, day: 'Пн / Ср', course: 'Английский язык (2 класс)', time: '12:00–12:50', teacher: 'Воронцова А.В.', place: '167 школа, каб. 211', level: 'Нач.' },
]

const schedule = ref(allSchedule)

onMounted(async () => {
  try {
    const res = await http.get('/schedule/my')
    if (res.data && res.data.length) schedule.value = res.data
  } catch {
    // fallback: показываем полное расписание
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.schedule-page h1 { font-size: var(--font-size-h2); font-weight: 700; color: var(--brand-purple); margin-bottom: 24px; }
.schedule-list { display: flex; flex-direction: column; gap: 16px; }
.schedule-card { display: flex; align-items: flex-start; gap: 20px; background: #fff7f0; border-radius: 14px; padding: 20px; border-left: 5px solid var(--brand-orange); transition: box-shadow 0.2s, transform 0.2s; }
.schedule-card:hover { box-shadow: 0 6px 20px rgba(255,107,45,0.15); transform: translateY(-2px); }
.schedule-day { font-size: 14px; font-weight: 700; color: var(--brand-orange); min-width: 140px; padding-top: 2px; text-transform: uppercase; letter-spacing: 0.04em; }
.schedule-info { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.schedule-course { font-size: 18px; font-weight: 700; color: var(--brand-purple); margin: 0; }
.schedule-time, .schedule-teacher, .schedule-place { font-size: 15px; color: var(--text-secondary); margin: 0; }
.schedule-level { background: var(--brand-orange); color: #fff; padding: 4px 12px; border-radius: 999px; font-size: 14px; font-weight: 700; align-self: flex-start; flex-shrink: 0; }
.no-schedule { background: #fff7f0; border-radius: 14px; padding: 40px; text-align: center; color: var(--text-secondary); font-size: 16px; }
.btn-enroll { display: inline-block; margin-top: 16px; padding: 12px 28px; background: var(--brand-orange); color: #fff; border-radius: 999px; font-weight: 700; font-size: 16px; text-decoration: none; }
.loading { color: var(--text-secondary); font-size: 16px; padding: 40px; text-align: center; }
@media (max-width: 768px) { .schedule-card { flex-direction: column; gap: 12px; } .schedule-day { min-width: unset; } }
</style>
