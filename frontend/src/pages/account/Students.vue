<template>
  <div class="students-page">
    <h1>👥 Ученики</h1>

    <div class="filters">
      <input v-model="search" type="text" placeholder="Поиск по имени, школе" />
      <select v-model="filterSchool">
        <option value="">Все школы</option>
        <option v-for="s in schools" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="filtered.length" class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>ФИО ученика</th>
            <th>Возраст / класс</th>
            <th>Школа</th>
            <th>Уровень</th>
            <th>Телефон родителя</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filtered" :key="s.id">
            <td>{{ s.id }}</td>
            <td>{{ s.fio }}</td>
            <td>{{ s.age }} л. / {{ s.grade }}кл.</td>
            <td>{{ s.school }}</td>
            <td><span class="level-badge">{{ s.level || '—' }}</span></td>
            <td>{{ s.phone }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="empty">Ученики не найдены.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

const loading = ref(true)
const students = ref<any[]>([])
const search = ref('')
const filterSchool = ref('')

const schools = computed(() => [...new Set(students.value.map((s: any) => s.school).filter(Boolean))])

const filtered = computed(() =>
  students.value
    .filter(s => !search.value || s.fio?.toLowerCase().includes(search.value.toLowerCase()) || s.school?.toLowerCase().includes(search.value.toLowerCase()))
    .filter(s => !filterSchool.value || s.school === filterSchool.value)
)

onMounted(async () => {
  try {
    const res = await http.get('/admin/students')
    students.value = res.data
  } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.students-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 20px; }
.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 180px; }
.table-wrap { overflow-x: auto; border-radius: 14px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { background: var(--brand-orange); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #ffe3cf; }
.data-table tr:hover td { background: #fff7f0; }
.level-badge { background: var(--brand-orange); color: #fff; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.empty, .loading { color: #aaa; padding: 24px 0; font-size: 15px; }
</style>
