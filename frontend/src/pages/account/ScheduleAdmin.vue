<template>
  <div class="schedule-admin">
    <h1>🗓 Расписание</h1>

    <div class="filters">
      <input v-model="search" type="text" placeholder="Поиск по школе / учителю" />
      <select v-model="filterDay">
        <option value="">Все дни</option>
        <option v-for="d in days" :key="d" :value="d">{{ d }}</option>
      </select>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Школа</th>
            <th>Учитель</th>
            <th>Дни</th>
            <th>Время</th>
            <th>Уровень</th>
            <th>Кабинет</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filtered" :key="item.id">
            <td>{{ item.school }}</td>
            <td>{{ item.teacher }}</td>
            <td>{{ item.days }}</td>
            <td>{{ item.time }}</td>
            <td><span class="level-badge">{{ item.level }}</span></td>
            <td>{{ item.room }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const search = ref('')
const filterDay = ref('')
const days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']

const schedule = ref([
  { id: 1, school: '5 гимназия', teacher: 'Лукьянова С.Я.', days: 'Пн/Ср', time: '12:20–13:10 / 11:50–12:40', level: 'AS1', room: 'каб. 109' },
  { id: 2, school: '121 школа', teacher: 'Лукьянова С.Я.', days: 'Вт/Чт', time: '12:00–12:50', level: 'FH1', room: 'каб. 214' },
  { id: 3, school: '121 школа', teacher: 'Лукьянова С.Я.', days: 'Вт/Чт', time: '13:10–14:00', level: 'AS1', room: 'каб. 214' },
  { id: 4, school: '7 гимназия', teacher: 'Белова А.А.', days: 'Пн/Ср', time: '11:00–12:00 / 10:30–11:30', level: 'AS2', room: 'каб. 119' },
  { id: 5, school: '7 гимназия', teacher: 'Белова А.А.', days: 'Пн/Ср', time: '12:30–13:20 / 11:30–12:20', level: 'FH1', room: 'каб. 119' },
  { id: 6, school: 'ЛИТ', teacher: 'Белова А.А.', days: 'Вт/Чт', time: '15:30–17:00 / 15:15–16:45', level: 'GWB1', room: 'каб. библ., 116' },
  { id: 7, school: '56 школа', teacher: 'Зудяева Н.А.', days: 'Пн/Чт', time: '12:00–12:50', level: 'FH1', room: 'каб. 3/10' },
  { id: 8, school: '56 школа', teacher: 'Зудяева Н.А.', days: 'Пн/Чт', time: '13:00–13:50', level: 'AS1', room: 'каб. 3/10' },
  { id: 9, school: '11 гимназия', teacher: 'Осинина С.Н.', days: 'Пн/Чт', time: '9:50–10:40', level: 'AS1', room: 'каб. 113' },
  { id: 10, school: '11 гимназия', teacher: 'Осинина С.Н.', days: 'Пн/Чт', time: '10:50–11:50', level: 'AS2', room: 'каб. 113' },
  { id: 11, school: '11 гимназия', teacher: 'Пасикан А.С.', days: 'Пн/Ср', time: '11:35–13:05', level: 'GWB1+', room: 'каб. 114' },
  { id: 12, school: '217 школа', teacher: 'Фомина С.О.', days: 'Пн/Пт', time: '10:20–11:10', level: 'AS1', room: 'каб. 314А' },
  { id: 13, school: '217 школа', teacher: 'Фомина С.О.', days: 'Пн/Пт', time: '14:20–15:20', level: 'AS2', room: 'каб. 314А' },
  { id: 14, school: '218 школа', teacher: 'Колесник Л.Н.', days: 'Пн/Ср', time: '10:30–11:15', level: 'AS1', room: 'каб. АВС' },
  { id: 15, school: '218 школа', teacher: 'Колесник Л.Н.', days: 'Вт/Чт', time: '10:10–11:10', level: 'AS2', room: 'каб. АВС' },
  { id: 16, school: '2 школа', teacher: 'Андрюнина М.В.', days: 'Вт/Чт', time: '13:00–13:50', level: 'FH1', room: 'каб. 43' },
  { id: 17, school: '2 школа', teacher: 'Турабова Д.Д.', days: 'Вт/Чт', time: '13:40–14:40', level: 'AS2', room: 'каб. 3' },
  { id: 18, school: '186 школа', teacher: 'Рубе Д.В.', days: 'Пн/Ср', time: '10:30–11:30', level: 'AS2', room: 'каб. 409' },
  { id: 19, school: '199 школа', teacher: 'Куцых М.Е.', days: 'Пн/Ср', time: '11:50–12:40', level: 'FH1', room: 'вахта' },
  { id: 20, school: '188 школа', teacher: 'Позднякова В.С.', days: 'Пн/Пт', time: '11:50–12:40', level: 'FH1', room: 'каб. АВС' },
  { id: 21, school: '221 школа', teacher: 'Данилова М.А.', days: 'Пн/Ср', time: '12:00–12:50', level: 'FH1', room: 'каб. 128/311' },
])

const filtered = computed(() =>
  schedule.value
    .filter(i => !search.value || i.school.toLowerCase().includes(search.value.toLowerCase()) || i.teacher.toLowerCase().includes(search.value.toLowerCase()))
    .filter(i => !filterDay.value || i.days.includes(filterDay.value))
)
</script>

<style scoped>
.schedule-admin h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 20px; }
.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 180px; }
.table-wrap { overflow-x: auto; border-radius: 14px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { background: var(--brand-orange); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #ffe3cf; }
.data-table tr:hover td { background: #fff7f0; }
.level-badge { background: var(--brand-orange); color: #fff; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
</style>
