<template>
  <div class="org-diagram-page">
    <h2 class="diagram-title">Схема структурных подразделений</h2>
    <div class="diagram-wrapper">
      <div class="diagram-node founder">
        <span class="node-label">УЧРЕДИТЕЛЬ</span>
        <span class="node-name">Шарифова Елена Сергеевна</span>
      </div>

      <div class="diagram-node director">
        <span class="node-label">ДИРЕКТОР</span>
        <span class="node-name">Андрюнина Марина Викторовна</span>
      </div>

      <div class="diagram-row">
        <div class="diagram-node deputy">
          <span class="node-label">Заместитель директора</span>
          <span class="node-name">Шевченко Елена Викторовна</span>
        </div>
        <div class="diagram-node methodologists">
          <span class="node-label">Методисты</span>
          <span class="node-name">Алексеева Марина Владимировна</span>
          <span class="node-name">Митина Ольга Сергеевна</span>
        </div>
        <div class="diagram-node manager">
          <span class="node-label">Администратор, менеджер</span>
          <span class="node-name">Сушкова Ольга Игоревна</span>
        </div>
      </div>

      <div class="diagram-node teachers">
        <span class="node-label">ПРЕПОДАВАТЕЛИ</span>
      </div>
    </div>

    <div class="branches-section">
      <h3 class="branches-title">Филиалы</h3>

      <div v-if="loading" class="loading">Загрузка...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="branches-list">
        <div v-for="branch in branches" :key="branch.id" class="branch-card">
          <h4>{{ branch.name }}</h4>
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
.org-diagram-page {
  max-width: 980px;
  margin: 0 auto;
  padding: 24px;
}

.diagram-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-purple);
  text-align: center;
  margin-bottom: 28px;
}

.diagram-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
}

.diagram-node {
  background: #ffffff;
  border: 2px solid #8b5cf6;
  border-radius: 14px;
  padding: 18px 22px;
  min-width: 280px;
  text-align: center;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  position: relative;
}

.diagram-node::before,
.diagram-node::after {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.director::before {
  top: -28px;
  width: 2px;
  height: 28px;
  background: #8b5cf6;
}

.founder::after {
  display: none;
}

.diagram-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(240px, 1fr));
  gap: 20px;
  width: 100%;
}

.diagram-row::before {
  content: '';
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  width: 2px;
  height: 28px;
  background: #8b5cf6;
}

.diagram-row {
  position: relative;
}

.diagram-row .diagram-node::before {
  display: none;
}

.diagram-row .diagram-node::after {
  display: none;
}

.diagram-node .node-label {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: #3f3f46;
  margin-bottom: 8px;
  letter-spacing: 0.05em;
}

.diagram-node .node-name {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  line-height: 1.5;
}

.diagram-node.teachers {
  min-width: 72%;
}

.diagram-node.teachers::before {
  content: '';
  position: absolute;
  top: -28px;
  width: 2px;
  height: 28px;
  background: #8b5cf6;
  left: 50%;
  transform: translateX(-50%);
}

.diagram-row .deputy,
.diagram-row .methodologists,
.diagram-row .manager {
  min-width: 0;
}

.diagram-row .deputy::before,
.diagram-row .methodologists::before,
.diagram-row .manager::before {
  content: '';
  position: absolute;
  top: -28px;
  width: 2px;
  height: 28px;
  background: #8b5cf6;
  left: 50%;
  transform: translateX(-50%);
}

.diagram-row .deputy::after,
.diagram-row .methodologists::after,
.diagram-row .manager::after {
  display: none;
}

.branches-section {
  margin-top: 40px;
}

.branches-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 20px;
  text-align: center;
}

.loading,
.error {
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
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 18px;
}

.branch-card {
  background: #f9fafb;
  border: 1px solid rgba(139, 92, 246, 0.18);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.04);
}

.branch-card h4 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--brand-purple);
}

.branch-card p {
  margin-bottom: 8px;
  font-size: 15px;
  line-height: 1.6;
}

.branch-card a {
  color: var(--brand-orange);
  text-decoration: none;
}

.branch-card a:hover {
  text-decoration: underline;
}

@media (max-width: 860px) {
  .diagram-row {
    grid-template-columns: 1fr;
  }

  .diagram-node.teachers {
    min-width: 100%;
  }
}
</style>
