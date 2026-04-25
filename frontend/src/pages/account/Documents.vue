<template>
  <div class="docs-page">
    <h1>📂 Документы</h1>

    <!-- Скелетон -->
    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-item" v-for="n in 5" :key="n"></div>
    </div>

    <template v-else>
      <!-- Персональные документы (contract, receipt) -->
      <section v-if="personal.length" class="doc-section">
        <h2>🔐 Мои документы</h2>
        <div class="doc-list">
          <a
            v-for="doc in personal"
            :key="doc.id"
            :href="doc.file_url"
            target="_blank"
            class="doc-item doc-item--personal"
          >
            <span class="doc-icon">{{ categoryIcon(doc.category) }}</span>
            <span class="doc-info">
              <span class="doc-name">{{ doc.title }}</span>
              <span v-if="doc.description" class="doc-desc">{{ doc.description }}</span>
              <span class="doc-date">📅 {{ formatDate(doc.created_at) }}</span>
            </span>
            <span class="doc-arrow">↓</span>
          </a>
        </div>
      </section>

      <!-- Общие документы по категориям -->
      <template v-for="sec in publicSections" :key="sec.key">
        <section v-if="sec.docs.length" class="doc-section">
          <h2>{{ sec.icon }} {{ sec.title }}</h2>
        <div class="doc-list">
          <a
            v-for="doc in sec.docs"
            :key="doc.id"
            :href="doc.file_url"
            target="_blank"
            class="doc-item"
          >
            <span class="doc-icon">📄</span>
            <span class="doc-info">
              <span class="doc-name">{{ doc.title }}</span>
              <span v-if="doc.description" class="doc-desc">{{ doc.description }}</span>
            </span>
            <span class="doc-arrow">↓</span>
          </a>
        </div>
      </section>

      <!-- Пустое состояние -->
      <div v-if="!personal.length && !publicDocs.length" class="no-docs">
        <div class="no-docs-icon">📂</div>
        <p>Документы ещё не добавлены.</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const loading = ref(true)
const allDocs = ref<any[]>([])

// Фильтрация
const personal   = computed(() => allDocs.value.filter(d => d.user_id))
const publicDocs = computed(() => allDocs.value.filter(d => !d.user_id))

const publicSections = computed(() => [
  {
    key: 'policy',
    icon: '🔒',
    title: 'Политики и согласия',
    docs: publicDocs.value.filter(d => d.category === 'policy'),
  },
  {
    key: 'schedule',
    icon: '📅',
    title: 'Расписание',
    docs: publicDocs.value.filter(d => d.category === 'schedule'),
  },
  {
    key: 'template',
    icon: '📝',
    title: 'Бланки анкет',
    docs: publicDocs.value.filter(d => d.category === 'template'),
  },
  {
    key: 'other',
    icon: '📁',
    title: 'Прочее',
    docs: publicDocs.value.filter(d => d.category === 'other'),
  },
])

function categoryIcon(cat: string): string {
  const icons: Record<string, string> = {
    contract: '📃',
    receipt:  '🧾',
    policy:   '🔒',
    schedule: '📅',
    template: '📝',
    other:    '📄',
  }
  return icons[cat] ?? '📄'
}

function formatDate(iso: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' })
}

onMounted(async () => {
  try {
    const isAuth = !!auth.token
    const endpoint = isAuth ? '/documents/my' : '/documents/public'
    const res = await http.get(endpoint)
    allDocs.value = res.data
  } catch {
    allDocs.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.docs-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 28px; }

.doc-section { margin-bottom: 32px; }
.doc-section h2 { font-size: 19px; font-weight: 700; color: var(--brand-purple); margin-bottom: 12px; }

.doc-list { display: flex; flex-direction: column; gap: 10px; }
.doc-item {
  display: flex; align-items: center; gap: 14px;
  background: #fff7f0; border-radius: 12px; padding: 14px 18px;
  text-decoration: none; color: #333;
  border: 1.5px solid #ffe3cf;
  transition: box-shadow 0.2s, border-color 0.2s, transform 0.15s;
}
.doc-item:hover {
  box-shadow: 0 4px 14px rgba(255,107,45,0.15);
  border-color: var(--brand-orange);
  transform: translateY(-1px);
}
.doc-item--personal { border-color: #c5b8f0; background: #f5f0ff; }
.doc-item--personal:hover { border-color: var(--brand-purple); box-shadow: 0 4px 14px rgba(100,60,200,0.12); }

.doc-icon { font-size: 22px; flex-shrink: 0; }
.doc-info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.doc-name { font-size: 15px; font-weight: 600; color: #333; }
.doc-desc { font-size: 13px; color: #888; }
.doc-date { font-size: 12px; color: #bbb; }
.doc-arrow { font-size: 18px; color: var(--brand-orange); flex-shrink: 0; }

/* Пустое состояние */
.no-docs {
  text-align: center; padding: 48px;
  background: #fff7f0; border-radius: 14px;
  color: #aaa;
}
.no-docs-icon { font-size: 48px; margin-bottom: 12px; }

/* Скелетон */
.skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.skeleton-item {
  height: 64px; border-radius: 12px;
  background: linear-gradient(90deg, #fff0e8 25%, #ffe8d6 50%, #fff0e8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
@keyframes shimmer { 0% { background-position: -200% 0 } 100% { background-position: 200% 0 } }
</style>
