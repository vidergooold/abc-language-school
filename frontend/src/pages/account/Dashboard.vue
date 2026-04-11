<template>
  <div class="dashboard">
    <h1>📊 Главная</h1>
    <p class="welcome">Добро пожаловать, <strong>{{ auth.user?.full_name || auth.user?.email }}</strong>!</p>

    <!-- Блок для админа и учителя -->
    <template v-if="isStaff">
      <div class="stats-grid">
        <div class="stat-card" v-for="s in stats" :key="s.label">
          <div class="stat-icon">{{ s.icon }}</div>
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>

      <div class="recent-grid">
        <div class="recent-block">
          <h2>📝 Последние анкеты</h2>
          <div v-if="recentForms.length" class="recent-list">
            <div class="recent-item" v-for="f in recentForms" :key="f.id">
              <span class="recent-name">{{ f.fio }}</span>
              <span class="recent-meta">{{ f.type }} • {{ f.date }}</span>
            </div>
          </div>
          <p v-else class="empty">Анкет пока нет</p>
          <RouterLink to="/account/forms" class="see-all">Смотреть все →</RouterLink>
        </div>

        <div class="recent-block">
          <h2>💬 Последние сообщения</h2>
          <div v-if="recentFeedback.length" class="recent-list">
            <div class="recent-item" v-for="fb in recentFeedback" :key="fb.id">
              <span class="recent-name">{{ fb.name }}</span>
              <span class="recent-meta">{{ fb.phone }} • {{ fb.date }}</span>
            </div>
          </div>
          <p v-else class="empty">Сообщений пока нет</p>
          <RouterLink to="/account/feedback" class="see-all">Смотреть все →</RouterLink>
        </div>
      </div>
    </template>

    <!-- Блок для студента -->
    <template v-else>
      <div class="student-cards">
        <RouterLink to="/account/schedule" class="student-card">
          <div class="student-card__icon">🗓</div>
          <div class="student-card__title">Расписание</div>
          <div class="student-card__desc">Посмотреть расписание занятий</div>
        </RouterLink>
        <RouterLink to="/account/documents" class="student-card">
          <div class="student-card__icon">📂</div>
          <div class="student-card__title">Документы</div>
          <div class="student-card__desc">Ваши договоры и справки</div>
        </RouterLink>
        <RouterLink to="/account/news" class="student-card">
          <div class="student-card__icon">📣</div>
          <div class="student-card__title">Новости</div>
          <div class="student-card__desc">Новости и объявления школы</div>
        </RouterLink>
        <RouterLink to="/account/profile" class="student-card">
          <div class="student-card__icon">👤</div>
          <div class="student-card__title">Профиль</div>
          <div class="student-card__desc">Редактировать личные данные</div>
        </RouterLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const isStaff = computed(() => ['admin', 'teacher'].includes(auth.user?.role || ''))

const stats = ref([
  { icon: '📝', label: 'Анкет за всё время', value: '—' },
  { icon: '👥', label: 'Учеников', value: '—' },
  { icon: '💬', label: 'Обращений', value: '—' },
  { icon: '🗓', label: 'Групп в расписании', value: '—' },
])

const recentForms = ref<any[]>([])
const recentFeedback = ref<any[]>([])

onMounted(async () => {
  if (!isStaff.value) return
  try {
    const [formsRes, fbRes, statsRes] = await Promise.all([
      http.get('/admin/forms?limit=5'),
      http.get('/admin/feedback?limit=5'),
      http.get('/admin/stats'),
    ])
    recentForms.value = formsRes.data
    recentFeedback.value = fbRes.data
    const s = statsRes.data
    stats.value[0].value = s.total_forms ?? '—'
    stats.value[1].value = s.total_students ?? '—'
    stats.value[2].value = s.total_feedback ?? '—'
    stats.value[3].value = s.schedule_groups ?? '—'
  } catch { /* silent */ }
})
</script>

<style scoped>
.dashboard h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 4px; }
.welcome { font-size: 17px; color: var(--text-secondary, #666); margin-bottom: 28px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 32px; }
.stat-card { background: #fff7f0; border-radius: 16px; padding: 20px; text-align: center; border: 2px solid #ffe3cf; }
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-value { font-size: 32px; font-weight: 700; color: var(--brand-orange); }
.stat-label { font-size: 14px; color: var(--text-secondary, #888); margin-top: 4px; }
.recent-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.recent-block { background: #fff7f0; border-radius: 16px; padding: 20px; }
.recent-block h2 { font-size: 18px; font-weight: 700; color: var(--brand-purple); margin-bottom: 14px; }
.recent-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.recent-item { display: flex; flex-direction: column; gap: 2px; padding: 10px; background: #fff; border-radius: 8px; }
.recent-name { font-size: 15px; font-weight: 600; color: #333; }
.recent-meta { font-size: 13px; color: var(--text-secondary, #888); }
.empty { font-size: 14px; color: var(--text-secondary, #aaa); margin-bottom: 12px; }
.see-all { font-size: 14px; color: var(--brand-orange); text-decoration: none; font-weight: 600; }
/* Студент */
.student-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.student-card { background: #fff7f0; border-radius: 16px; padding: 24px 20px; border: 2px solid #ffe3cf; text-decoration: none; transition: box-shadow 0.2s, transform 0.2s; display: flex; flex-direction: column; gap: 8px; }
.student-card:hover { box-shadow: 0 4px 20px #ffe3cf; transform: translateY(-2px); }
.student-card__icon { font-size: 32px; }
.student-card__title { font-size: 18px; font-weight: 700; color: var(--brand-purple); }
.student-card__desc { font-size: 14px; color: var(--text-secondary, #888); }
@media (max-width: 768px) { .recent-grid { grid-template-columns: 1fr; } }
</style>
