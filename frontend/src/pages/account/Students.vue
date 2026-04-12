<template>
  <div class="students-page">
    <div class="page-header">
      <h1>👥 Ученики</h1>
      <div class="header-actions">
        <span class="total-badge">{{ students.length }} чел.</span>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filters">
      <input v-model="search" type="text" placeholder="🔍 Поиск по имени или телефону" />
      <select v-model="filterType">
        <option value="">Все типы</option>
        <option value="child">Школьники</option>
        <option value="adult">Взрослые</option>
        <option value="preschool">Дошкольники</option>
      </select>
      <select v-model="filterStatus">
        <option value="">Все статусы</option>
        <option value="new">Новые</option>
        <option value="processed">Обработанные</option>
        <option value="cancelled">Отменённые</option>
      </select>
    </div>

    <!-- Скелетон -->
    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-row" v-for="n in 6" :key="n"></div>
    </div>

    <div v-else-if="filtered.length" class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>ФИО</th>
            <th>Тип</th>
            <th>Возраст</th>
            <th>Телефон</th>
            <th>Email</th>
            <th>Статус</th>
            <th>Дата заявки</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filtered" :key="s.id + '-' + s.type">
            <td class="col-id">{{ s.id }}</td>
            <td class="col-name">{{ s.fio || '—' }}</td>
            <td><span class="type-badge" :class="'type-' + s.type">{{ typeLabel(s.type) }}</span></td>
            <td>{{ s.age ? s.age + ' л.' : '—' }}</td>
            <td>{{ s.phone || '—' }}</td>
            <td>{{ s.email || '—' }}</td>
            <td><span class="status-badge" :class="'status-' + (s.status || 'new')">{{ statusLabel(s.status) }}</span></td>
            <td class="col-date">{{ s.created_at || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">👥</div>
      <p>Ученики не найдены.</p>
      <p class="empty-hint">Они появятся здесь автоматически, когда кто-то заполнит анкету на сайте.</p>
    </div>

    <div class="hint-box">
      <strong>💡 Откуда берутся ученики?</strong>
      <p>Ученики появляются автоматически, когда родители или сами ученики заполняют анкеты на странице
      <RouterLink to="/enroll">«Запись на занятие»</RouterLink>. Все анкеты доступны в разделе
      <RouterLink to="/account/forms">«Анкеты и формы»</RouterLink>.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import http from '@/api/http'

const loading = ref(true)
const students = ref<any[]>([])
const search = ref('')
const filterType = ref('')
const filterStatus = ref('')

const filtered = computed(() =>
  students.value
    .filter(s => !search.value ||
      (s.fio ?? '').toLowerCase().includes(search.value.toLowerCase()) ||
      (s.phone ?? '').includes(search.value)
    )
    .filter(s => !filterType.value || s.type === filterType.value)
    .filter(s => !filterStatus.value || (s.status || 'new') === filterStatus.value)
)

function typeLabel(t: string): string {
  return { child: 'Школьник', adult: 'Взрослый', preschool: 'Дошкольник' }[t] ?? t
}
function statusLabel(s: string): string {
  return { new: 'Новая', processed: 'Обработана', cancelled: 'Отменена' }[s] ?? (s || 'Новая')
}

async function load() {
  try {
    const res = await http.get('/admin/students')
    students.value = res.data
  } catch {
    students.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.students-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.total-badge { background: var(--brand-orange); color: #fff; padding: 4px 14px; border-radius: 999px; font-size: 14px; font-weight: 700; }

.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 160px; outline: none; }
.filters input:focus, .filters select:focus { border-color: var(--brand-orange); }

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
.col-id { color: #bbb; font-size: 13px; }
.col-name { font-weight: 600; color: #333; }
.col-date { font-size: 13px; color: #aaa; white-space: nowrap; }

.type-badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }
.type-child     { background: #e8f4ff; color: #2a7bbf; }
.type-adult     { background: #fff0e8; color: var(--brand-orange); }
.type-preschool { background: #f0ffe8; color: #3a9a22; }

.status-badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }
.status-new       { background: #e8f0ff; color: #2a5bbf; }
.status-processed { background: #e6f9ef; color: #22a55b; }
.status-cancelled { background: #fdeaea; color: #e03c3c; }

.empty-state { text-align: center; padding: 48px; background: #fff7f0; border-radius: 14px; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { font-size: 16px; color: #888; margin-bottom: 6px; }
.empty-hint { font-size: 14px; color: #bbb; }

.hint-box { margin-top: 28px; background: #f5f0ff; border-radius: 14px; padding: 18px 20px; border-left: 4px solid var(--brand-purple); }
.hint-box strong { font-size: 15px; color: var(--brand-purple); display: block; margin-bottom: 6px; }
.hint-box p { font-size: 14px; color: #555; margin: 0; line-height: 1.6; }
.hint-box a { color: var(--brand-orange); font-weight: 600; }
</style>
