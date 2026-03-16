<template>
  <div class="forms-page">
    <div class="page-header">
      <h1>📝 Анкеты и формы</h1>
      <a href="/enroll" target="_blank" class="btn-public">🔗 Форма записи для посетителей ↗</a>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>

    <div v-else>
      <div class="filters">
        <input v-model="search" placeholder="Поиск по имени" />
        <select v-model="filterType">
          <option value="">Все типы</option>
          <option v-for="t in types" :key="t" :value="t">{{ t }}</option>
        </select>
        <select v-model="filterStatus">
          <option value="">Все статусы</option>
          <option value="new">🟡 Новые</option>
          <option value="processed">✅ Обработаны</option>
        </select>
      </div>

      <div v-if="filtered.length" class="forms-list">
        <div class="form-card" v-for="f in filtered" :key="f.id" :class="{ 'form-card--new': f.status === 'new' }">
          <div class="form-card__header">
            <span class="form-card__name">{{ f.fio }}</span>
            <span class="form-tag">{{ f.type }}</span>
            <span class="form-date">{{ f.created_at }}</span>
            <span class="status-badge" :class="f.status === 'new' ? 'status-new' : 'status-done'">
              {{ f.status === 'new' ? '🟡 Новая' : '✅ Обработана' }}
            </span>
          </div>
          <div class="form-card__body">
            <p>📞 {{ f.phone }}</p>
            <p v-if="f.email">📧 {{ f.email }}</p>
            <p v-if="f.comment">💬 {{ f.comment }}</p>
          </div>
          <div class="form-card__actions">
            <button v-if="f.status === 'new'" class="btn-process" @click="markProcessed(f.id)">✅ Отметить обработанной</button>
            <button class="btn-del" @click="deleteForm(f.id)">🗑️ Удалить</button>
          </div>
        </div>
      </div>
      <p v-else class="empty">Анкет нет.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

const loading = ref(true)
const forms = ref<any[]>([])
const search = ref('')
const filterType = ref('')
const filterStatus = ref('')

const types = computed(() => [...new Set(forms.value.map((f: any) => f.type).filter(Boolean))])

const filtered = computed(() =>
  forms.value
    .filter(f => !search.value || f.fio?.toLowerCase().includes(search.value.toLowerCase()))
    .filter(f => !filterType.value || f.type === filterType.value)
    .filter(f => !filterStatus.value || f.status === filterStatus.value)
)

async function load() {
  try { const r = await http.get('/admin/forms'); forms.value = r.data } catch {}
  finally { loading.value = false }
}

async function markProcessed(id: number) {
  try { await http.patch(`/admin/forms/${id}`, { status: 'processed' }); await load() } catch {}
}

async function deleteForm(id: number) {
  if (!confirm('Удалить анкету?')) return
  try { await http.delete(`/admin/forms/${id}`); await load() } catch {}
}

onMounted(load)
</script>

<style scoped>
.forms-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.btn-public { background: #f5f0ff; color: var(--brand-purple); border: 1.5px solid #e8deff; padding: 9px 18px; border-radius: 10px; text-decoration: none; font-size: 14px; font-weight: 600; transition: background 0.2s; }
.btn-public:hover { background: #e8deff; }
.filters { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.filters input, .filters select { padding: 9px 14px; border-radius: 10px; border: 1.5px solid #ffe3cf; font-size: 15px; min-width: 160px; }
.forms-list { display: flex; flex-direction: column; gap: 14px; }
.form-card { background: #fff7f0; border-radius: 14px; padding: 16px 20px; border: 2px solid #ffe3cf; }
.form-card--new { border-color: #ffb347; background: #fffbf0; }
.form-card__header { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }
.form-card__name { font-size: 16px; font-weight: 700; color: #333; }
.form-tag { background: var(--brand-orange); color: #fff; font-size: 12px; font-weight: 700; padding: 2px 10px; border-radius: 999px; }
.form-date { font-size: 12px; color: #aaa; margin-left: auto; }
.status-badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }
.status-new { background: #fff3cd; color: #856404; }
.status-done { background: #d4edda; color: #155724; }
.form-card__body p { font-size: 14px; color: #555; margin: 3px 0; }
.form-card__actions { display: flex; gap: 10px; margin-top: 12px; }
.btn-process { background: #d4edda; color: #155724; border: none; padding: 7px 14px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px; }
.btn-del { background: #ffeaea; color: var(--brand-red); border: none; padding: 7px 14px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px; }
.empty, .loading { color: #aaa; padding: 24px 0; font-size: 15px; }
</style>
