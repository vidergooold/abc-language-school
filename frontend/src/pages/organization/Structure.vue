<template>
  <div class="org-section">
    <h2 class="section-title">Структура и филиалы</h2>

    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="branches-list">
      <div v-for="branch in branches" :key="branch.id" class="branch-card">
        <h3>{{ branch.name }}</h3>
        <p><strong>Руководитель:</strong> {{ branch.manager_name || '—' }}</p>
        <p><strong>Должность:</strong> {{ branch.manager_position || '—' }}</p>
        <p><strong>Адрес:</strong> {{ branch.address }}</p>
        <p>
          <strong>Телефон:</strong>
          <a v-if="branch.phone" :href="`tel:${branch.phone}`">{{ formatPhone(branch.phone) }}</a>
          <span v-else>—</span>
        </p>
        <p><strong>Режим работы:</strong> {{ branch.working_hours || '—' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface Branch {
  id: number
  name: string
  address: string
  phone: string | null
  manager_name: string | null
  manager_position: string | null
  working_hours: string | null
}

const branches = ref<Branch[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

function formatPhone(phone: string): string {
  const digits = phone.replace(/\D/g, '')
  if (digits.length === 11) {
    return `(${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7, 9)}-${digits.slice(9, 11)}`
  }
  return phone
}

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/api/v1/branches/`)
    if (!res.ok) throw new Error(`Ошибка ${res.status}`)
    branches.value = await res.json()
  } catch (e: any) {
    error.value = 'Не удалось загрузить данные о филиалах'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.org-section {
  font-size: 17px;
  line-height: 1.6;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 20px;
}

.loading, .error {
  padding: 24px;
  text-align: center;
  color: var(--brand-purple);
  font-size: 16px;
}

.error {
  color: #c0392b;
}

.branches-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.branch-card {
  background: #ffe3cf;
  padding: 20px;
  border-radius: 12px;
}

.branch-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 12px;
}

.branch-card p {
  font-size: 15px;
  margin-bottom: 6px;
}

.branch-card a {
  color: var(--brand-orange);
  text-decoration: none;
}

.branch-card a:hover {
  text-decoration: underline;
}
</style>
