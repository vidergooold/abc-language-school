<template>
  <div class="feedback-page">
    <h1>💬 Обратная связь</h1>

    <div class="filters">
      <input v-model="search" type="text" placeholder="Поиск по имени / телефону" />
      <select v-model="filterRead">
        <option value="">Все</option>
        <option value="false">Непрочитанные</option>
        <option value="true">Обработанные</option>
      </select>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else class="cards">
      <div
        class="fb-card"
        v-for="fb in filtered"
        :key="fb.id"
        :class="{ unread: !fb.is_read }"
        @click="markRead(fb)"
      >
        <div class="fb-top">
          <strong>{{ fb.name }}</strong>
          <span class="fb-date">{{ fb.created_at }}</span>
          <span v-if="!fb.is_read" class="fb-badge">Новое</span>
        </div>
        <div class="fb-contact">
          <a :href="`tel:${fb.phone}`">{{ fb.phone }}</a>
          <span v-if="fb.email">• {{ fb.email }}</span>
        </div>
        <p class="fb-message">{{ fb.message || '—' }}</p>
      </div>
    </div>

    <p v-if="!loading && !filtered.length" class="empty">Сообщений нет.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

const loading = ref(true)
const feedbacks = ref<any[]>([])
const search = ref('')
const filterRead = ref('')

const filtered = computed(() =>
  feedbacks.value
    .filter(f => !search.value || f.name?.toLowerCase().includes(search.value.toLowerCase()) || f.phone?.includes(search.value))
    .filter(f => filterRead.value === '' || String(f.is_read) === filterRead.value)
)

async function markRead(fb: any) {
  if (!fb.is_read) {
    try { await http.patch(`/admin/feedback/${fb.id}/read`) } catch {}
    fb.is_read = true
  }
}

onMounted(async () => {
  try {
    const res = await http.get('/admin/feedback')
    feedbacks.value = res.data
  } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.feedback-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 20px; }
.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 180px; }
.cards { display: flex; flex-direction: column; gap: 14px; }
.fb-card { background: #fff7f0; border-radius: 14px; padding: 16px 20px; cursor: pointer; border-left: 4px solid #ffe3cf; transition: box-shadow 0.2s; }
.fb-card.unread { border-left-color: var(--brand-orange); background: #fff; box-shadow: 0 2px 10px rgba(255,107,45,0.12); }
.fb-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
.fb-top { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.fb-top strong { font-size: 16px; color: #222; }
.fb-date { font-size: 13px; color: #aaa; margin-left: auto; }
.fb-badge { background: var(--brand-orange); color: #fff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; }
.fb-contact { font-size: 14px; color: var(--brand-orange); margin-bottom: 8px; }
.fb-contact a { color: var(--brand-orange); text-decoration: none; }
.fb-message { font-size: 14px; color: #555; line-height: 1.5; }
.empty, .loading { color: #aaa; padding: 24px 0; font-size: 15px; }
</style>
