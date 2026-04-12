<template>
  <div class="dashboard">
    <h1>📊 Главная</h1>
    <p class="welcome">Добро пожаловать, <strong>{{ auth.user?.full_name || auth.user?.email }}</strong>!</p>

    <!-- ===== ADMIN / TEACHER ===== -->
    <template v-if="isStaff">
      <div class="stats-grid">
        <div class="stat-card" v-for="s in stats" :key="s.label">
          <div class="stat-icon">{{ s.icon }}</div>
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- Разбивка по типам анкет -->
      <div v-if="formsByType" class="forms-breakdown">
        <h2>📊 Анкеты по типам</h2>
        <div class="breakdown-list">
          <div class="breakdown-item" v-for="(val, key) in formsByType" :key="key">
            <span class="breakdown-label">{{ typeLabel(key) }}</span>
            <div class="breakdown-bar-wrap">
              <div class="breakdown-bar" :style="{ width: barWidth(val) + '%' }"></div>
            </div>
            <span class="breakdown-val">{{ val }}</span>
          </div>
        </div>
      </div>

      <div class="recent-grid">
        <div class="recent-block">
          <h2>📝 Последние анкеты</h2>
          <div v-if="loadingForms" class="skeleton-list">
            <div class="skeleton-row" v-for="n in 3" :key="n"></div>
          </div>
          <div v-else-if="recentForms.length" class="recent-list">
            <div class="recent-item" v-for="f in recentForms" :key="f.id">
              <div class="recent-item__left">
                <span class="recent-name">{{ f.fio }}</span>
                <span class="recent-meta">{{ typeLabel(f.type) }} • {{ f.date }}</span>
              </div>
              <span class="status-badge" :class="'status-' + (f.status || 'new')">{{ statusLabel(f.status) }}</span>
            </div>
          </div>
          <p v-else class="empty">Анкет пока нет</p>
          <RouterLink to="/account/forms" class="see-all">Смотреть все →</RouterLink>
        </div>

        <div class="recent-block">
          <h2>💬 Последние обращения</h2>
          <div v-if="loadingFeedback" class="skeleton-list">
            <div class="skeleton-row" v-for="n in 3" :key="n"></div>
          </div>
          <div v-else-if="recentFeedback.length" class="recent-list">
            <div class="recent-item" v-for="fb in recentFeedback" :key="fb.id">
              <div class="recent-item__left">
                <span class="recent-name">{{ fb.name }}</span>
                <span class="recent-meta">{{ fb.phone }} • {{ fb.date }}</span>
              </div>
              <span v-if="!fb.is_read" class="unread-dot">●</span>
            </div>
          </div>
          <p v-else class="empty">Сообщений пока нет</p>
          <RouterLink to="/account/feedback" class="see-all">Смотреть все →</RouterLink>
        </div>
      </div>
    </template>

    <!-- ===== STUDENT ===== -->
    <template v-else>
      <!-- Карточки быстрых ссылок -->
      <div class="student-cards">
        <RouterLink to="/account/schedule" class="student-card">
          <div class="student-card__icon">🗓</div>
          <div class="student-card__title">Расписание</div>
          <div class="student-card__desc">Посмотреть расписание занятий</div>
        </RouterLink>
        <RouterLink to="/account/attendance" class="student-card">
          <div class="student-card__icon">✅</div>
          <div class="student-card__title">Посещаемость</div>
          <div class="student-card__desc" v-if="attendanceRate !== null">{{ attendanceRate }}% занятий посещено</div>
          <div class="student-card__desc" v-else>Ваша посещаемость занятий</div>
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

      <!-- Ближайшее занятие -->
      <div v-if="nextLesson" class="next-lesson-block">
        <h2>📅 Ближайшее занятие</h2>
        <div class="next-lesson-card">
          <div class="next-lesson__day">{{ nextLesson.day_of_week }}</div>
          <div class="next-lesson__info">
            <strong>{{ nextLesson.course_name || nextLesson.group_name || 'Занятие' }}</strong>
            <span>🕐 {{ formatTime(nextLesson.time_start) }}–{{ formatTime(nextLesson.time_end) }}</span>
            <span v-if="nextLesson.teacher_name">👤 {{ nextLesson.teacher_name }}</span>
            <span v-if="nextLesson.classroom_name">📍 {{ nextLesson.classroom_name }}</span>
          </div>
        </div>
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

// --- STAFF ---
const stats = ref([
  { icon: '📝', label: 'Анкет за всё время', value: '—' },
  { icon: '👥', label: 'Учеников в базе', value: '—' },
  { icon: '💬', label: 'Обращений', value: '—' },
  { icon: '🏫', label: 'Групп в расписании', value: '—' },
])
const formsByType = ref<Record<string, number> | null>(null)
const recentForms = ref<any[]>([])
const recentFeedback = ref<any[]>([])
const loadingForms = ref(false)
const loadingFeedback = ref(false)

const totalForms = computed(() =>
  formsByType.value ? Object.values(formsByType.value).reduce((a, b) => a + b, 0) : 0
)
function barWidth(val: number): number {
  if (!totalForms.value) return 0
  return Math.round((val / totalForms.value) * 100)
}
function typeLabel(key: string): string {
  return { child: 'Школьник', adult: 'Взрослый', preschool: 'Дошкольник', teacher: 'Учитель', testing: 'Тестирование' }[key] ?? key
}
function statusLabel(s: string): string {
  return { new: 'Новая', processed: 'Обработана', cancelled: 'Отменена' }[s] ?? (s || 'Новая')
}

// --- STUDENT ---
const attendanceRate = ref<number | null>(null)
const nextLesson = ref<any | null>(null)

function formatTime(t: string): string {
  if (!t) return ''
  return t.slice(0, 5)
}

onMounted(async () => {
  if (isStaff.value) {
    loadingForms.value = true
    loadingFeedback.value = true
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
      formsByType.value = s.forms_by_type ?? null
    } catch { /* silent */ } finally {
      loadingForms.value = false
      loadingFeedback.value = false
    }
  } else {
    // Student: load attendance rate + next lesson
    try {
      const attRes = await http.get('/attendance/my')
      const records: any[] = attRes.data
      if (records.length) {
        const present = records.filter(r => r.status === 'present' || r.status === 'late').length
        attendanceRate.value = Math.round(present / records.length * 100)
      }
    } catch {}
    try {
      const schRes = await http.get('/schedule/my')
      if (schRes.data?.length) nextLesson.value = schRes.data[0]
    } catch {}
  }
})
</script>

<style scoped>
.dashboard h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 4px; }
.welcome { font-size: 17px; color: var(--text-secondary, #666); margin-bottom: 28px; }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 28px; }
.stat-card { background: #fff7f0; border-radius: 16px; padding: 20px; text-align: center; border: 2px solid #ffe3cf; }
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-value { font-size: 32px; font-weight: 700; color: var(--brand-orange); }
.stat-label { font-size: 13px; color: var(--text-secondary, #888); margin-top: 4px; }

/* Breakdown */
.forms-breakdown { background: #fff7f0; border-radius: 16px; padding: 20px; margin-bottom: 28px; border: 2px solid #ffe3cf; }
.forms-breakdown h2 { font-size: 16px; font-weight: 700; color: var(--brand-purple); margin-bottom: 14px; }
.breakdown-list { display: flex; flex-direction: column; gap: 10px; }
.breakdown-item { display: flex; align-items: center; gap: 10px; }
.breakdown-label { min-width: 110px; font-size: 14px; color: #555; }
.breakdown-bar-wrap { flex: 1; height: 8px; background: #ffe3cf; border-radius: 999px; overflow: hidden; }
.breakdown-bar { height: 100%; background: var(--brand-orange); border-radius: 999px; transition: width 0.5s ease; }
.breakdown-val { font-size: 14px; font-weight: 700; color: var(--brand-orange); min-width: 28px; text-align: right; }

/* Recent */
.recent-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.recent-block { background: #fff7f0; border-radius: 16px; padding: 20px; }
.recent-block h2 { font-size: 18px; font-weight: 700; color: var(--brand-purple); margin-bottom: 14px; }
.recent-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.recent-item { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 12px; background: #fff; border-radius: 10px; }
.recent-item__left { display: flex; flex-direction: column; gap: 2px; }
.recent-name { font-size: 15px; font-weight: 600; color: #333; }
.recent-meta { font-size: 13px; color: var(--text-secondary, #888); }
.status-badge { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 999px; white-space: nowrap; }
.status-new       { background: #e8f0ff; color: #2a5bbf; }
.status-processed { background: #e6f9ef; color: #22a55b; }
.status-cancelled { background: #fdeaea; color: #e03c3c; }
.unread-dot { color: var(--brand-orange); font-size: 18px; flex-shrink: 0; }
.empty { font-size: 14px; color: var(--text-secondary, #aaa); margin-bottom: 12px; }
.see-all { font-size: 14px; color: var(--brand-orange); text-decoration: none; font-weight: 600; }
.see-all:hover { text-decoration: underline; }

/* Skeleton */
.skeleton-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.skeleton-row { height: 48px; border-radius: 10px; background: linear-gradient(90deg,#ffe8d6 25%,#ffd6b8 50%,#ffe8d6 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; }
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }

/* Student */
.student-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px; }
.student-card { background: #fff7f0; border-radius: 16px; padding: 22px 18px; border: 2px solid #ffe3cf; text-decoration: none; transition: box-shadow 0.2s, transform 0.2s; display: flex; flex-direction: column; gap: 8px; }
.student-card:hover { box-shadow: 0 4px 20px #ffe3cf; transform: translateY(-2px); }
.student-card__icon { font-size: 30px; }
.student-card__title { font-size: 17px; font-weight: 700; color: var(--brand-purple); }
.student-card__desc { font-size: 13px; color: var(--text-secondary, #888); }

/* Next lesson */
.next-lesson-block { background: #fff7f0; border-radius: 16px; padding: 20px; border: 2px solid #ffe3cf; }
.next-lesson-block h2 { font-size: 18px; font-weight: 700; color: var(--brand-purple); margin-bottom: 14px; }
.next-lesson-card { display: flex; gap: 20px; align-items: flex-start; }
.next-lesson__day { font-size: 13px; font-weight: 700; color: var(--brand-orange); text-transform: uppercase; min-width: 40px; padding-top: 2px; }
.next-lesson__info { display: flex; flex-direction: column; gap: 5px; }
.next-lesson__info strong { font-size: 17px; color: var(--brand-purple); }
.next-lesson__info span { font-size: 14px; color: var(--text-secondary, #666); }

@media (max-width: 768px) { .recent-grid { grid-template-columns: 1fr; } }
</style>
