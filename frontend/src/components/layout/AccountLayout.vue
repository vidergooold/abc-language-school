<template>
  <div class="account-layout">
    <aside class="sidebar">
      <div class="sidebar__header">
        <h3>Личный кабинет</h3>
        <p class="sidebar__role" :class="roleClass">{{ roleLabel }}</p>
        <p class="sidebar__name">{{ auth.user?.full_name || auth.user?.email }}</p>
      </div>
      <nav>
        <!-- Все роли -->
        <RouterLink to="/account" exact-active-class="router-link-active" class="sidebar-link">📊 Главная</RouterLink>
        <RouterLink to="/account/schedule" class="sidebar-link">🗓 Расписание</RouterLink>
        <RouterLink to="/account/documents" class="sidebar-link">📂 Документы</RouterLink>
        <RouterLink to="/account/attendance" class="sidebar-link">✅ Посещаемость</RouterLink>
        <RouterLink to="/account/profile" class="sidebar-link">👤 Профиль</RouterLink>

        <!-- Только учитель и админ -->
        <template v-if="isStaff">
          <RouterLink to="/account/news" class="sidebar-link">📣 Новости</RouterLink>
          <div class="sidebar-section">Управление</div>
          <RouterLink to="/account/students" class="sidebar-link">👥 Ученики</RouterLink>
          <RouterLink to="/account/forms" class="sidebar-link">📝 Анкеты и формы</RouterLink>
          <RouterLink to="/account/feedback" class="sidebar-link">💬 Обратная связь</RouterLink>
        </template>

        <!-- Только админ -->
        <template v-if="isAdmin">
          <RouterLink to="/account/schedule-admin" class="sidebar-link">🗓 Расписание (ред.)</RouterLink>
        </template>

        <div class="sidebar-divider"></div>
        <button @click="logout" class="sidebar-logout">🚪 Выйти</button>
      </nav>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, RouterLink } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const role      = computed(() => auth.user?.role)
const isAdmin   = computed(() => role.value === 'admin')
const isTeacher = computed(() => role.value === 'teacher')
const isStaff   = computed(() => isAdmin.value || isTeacher.value)

const roleLabel = computed(() => {
  if (isAdmin.value)   return '🔑 Администратор'
  if (isTeacher.value) return '👨\u200d🏫 Учитель'
  return '🎓 Студент'
})
const roleClass = computed(() => {
  if (isAdmin.value)   return 'role-admin'
  if (isTeacher.value) return 'role-teacher'
  return 'role-student'
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.account-layout { display: flex; min-height: calc(100vh - 80px); }
.sidebar {
  width: 250px; padding: 20px 16px;
  background: var(--bg-white); border-right: 2px solid #ffe3cf;
  display: flex; flex-direction: column; gap: 4px; flex-shrink: 0;
}
.sidebar__header { margin-bottom: 16px; padding-bottom: 14px; border-bottom: 2px solid var(--brand-orange); }
.sidebar__header h3 { font-size: 17px; font-weight: 700; color: var(--brand-purple); margin-bottom: 4px; }
.sidebar__role {
  display: inline-block; padding: 2px 10px; border-radius: 999px;
  font-size: 12px; font-weight: 700; margin-bottom: 4px;
}
.role-admin   { background: #ffeaea; color: var(--brand-red); }
.role-teacher { background: #ffe3cf; color: var(--brand-orange); }
.role-student { background: #e8f4ff; color: #2a7bbf; }
.sidebar__name {
  font-size: 13px; color: var(--text-secondary, #888);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.sidebar-section {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--text-secondary, #aaa);
  padding: 12px 12px 4px;
}
.sidebar-link {
  display: block; padding: 10px 12px; border-radius: 10px;
  font-size: 15px; font-weight: 500; color: var(--brand-purple);
  text-decoration: none; transition: background 0.2s, color 0.2s, padding-left 0.2s;
}
.sidebar-link:hover { background: #ffe3cf; color: var(--brand-orange); padding-left: 16px; }
.sidebar-link.router-link-active { background: #ffe3cf; color: var(--brand-orange); font-weight: 700; }
.sidebar-divider { height: 1px; background: #ffe3cf; margin: 8px 0; }
.sidebar-logout {
  padding: 10px 12px; border-radius: 10px; border: none; background: none;
  font-size: 15px; font-weight: 500; color: var(--brand-red);
  cursor: pointer; text-align: left; font-family: inherit; width: 100%;
  transition: background 0.2s;
}
.sidebar-logout:hover { background: #ffeaea; }
.content { flex: 1; padding: 32px; overflow-x: auto; }
@media (max-width: 768px) {
  .account-layout { flex-direction: column; }
  .sidebar { width: 100%; border-right: none; border-bottom: 2px solid #ffe3cf; }
  .content { padding: 20px 16px; }
}
</style>
