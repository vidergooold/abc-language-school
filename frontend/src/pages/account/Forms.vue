<template>
  <div class="forms-page">
    <h1>📝 Анкеты и формы</h1>

    <div class="filters">
      <select v-model="filterType">
        <option value="">Все типы</option>
        <option value="child">Школьник</option>
        <option value="adult">Взрослый</option>
        <option value="preschool">Дошкольник</option>
      </select>
      <input v-model="search" type="text" placeholder="Поиск по имени / телефону" />
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else-if="filtered.length" class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>ФИО</th>
            <th>Тип</th>
            <th>Телефон</th>
            <th>Школа / Место работы</th>
            <th>Дата</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in filtered" :key="f.id">
            <td>{{ f.id }}</td>
            <td>{{ f.fio }}</td>
            <td><span :class="['badge', f.type]">{{ typeLabel(f.type) }}</span></td>
            <td>{{ f.phone }}</td>
            <td>{{ f.school || f.work || '—' }}</td>
            <td>{{ f.created_at }}</td>
            <td>
              <button class="btn-view" @click="openDetail(f)">Подробнее</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="empty">Нет анкет.</p>

    <!-- Модальное окно -->
    <div v-if="selected" class="modal-overlay" @click.self="selected = null">
      <div class="modal">
        <button class="modal-close" @click="selected = null">×</button>
        <h2>Анкета #{{ selected.id }}</h2>
        <table class="detail-table">
          <tr v-for="(val, key) in selected" :key="key">
            <td class="detail-key">{{ key }}</td>
            <td>{{ val }}</td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

const loading = ref(true)
const forms = ref<any[]>([])
const filterType = ref('')
const search = ref('')
const selected = ref<any>(null)

const filtered = computed(() =>
  forms.value
    .filter(f => !filterType.value || f.type === filterType.value)
    .filter(f => !search.value || f.fio?.toLowerCase().includes(search.value.toLowerCase()) || f.phone?.includes(search.value))
)

function typeLabel(t: string) {
  return { child: 'Школьник', adult: 'Взрослый', preschool: 'Дошкольник' }[t] || t
}

function openDetail(f: any) { selected.value = f }

onMounted(async () => {
  try {
    const res = await http.get('/admin/forms')
    forms.value = res.data
  } catch { /* silent */ } finally { loading.value = false }
})
</script>

<style scoped>
.forms-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 20px; }
.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters select, .filters input { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 180px; }
.table-wrap { overflow-x: auto; border-radius: 14px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { background: var(--brand-orange); color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #ffe3cf; vertical-align: middle; }
.data-table tr:hover td { background: #fff7f0; }
.badge { padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.badge.child { background: #ffe3cf; color: var(--brand-orange); }
.badge.adult { background: #e8e0ff; color: var(--brand-purple); }
.badge.preschool { background: #d4f7e8; color: #2a9d5c; }
.btn-view { padding: 5px 14px; background: var(--brand-orange); color: #fff; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; }
.empty { color: #aaa; font-size: 15px; padding: 24px 0; }
.loading { color: #aaa; padding: 24px 0; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 300; display: flex; align-items: center; justify-content: center; }
.modal { background: #fff; border-radius: 18px; padding: 28px; max-width: 560px; width: 90%; max-height: 80vh; overflow-y: auto; position: relative; }
.modal h2 { font-size: 20px; font-weight: 700; color: var(--brand-purple); margin-bottom: 16px; }
.modal-close { position: absolute; top: 14px; right: 18px; font-size: 22px; border: none; background: none; cursor: pointer; color: #888; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.detail-table tr { border-bottom: 1px solid #ffe3cf; }
.detail-table td { padding: 8px 10px; }
.detail-key { font-weight: 700; color: var(--brand-purple); width: 40%; white-space: nowrap; }
</style>
