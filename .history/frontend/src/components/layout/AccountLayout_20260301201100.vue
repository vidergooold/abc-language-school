<template>
  <div class="account-layout">
    <aside class="sidebar">
      <h3>Личный кабинет</h3>
      <nav>
        <RouterLink to="/account" class="sidebar-link">Профиль</RouterLink>
        <RouterLink to="/account/schedule" class="sidebar-link">Расписание</RouterLink>
        <button @click="logout" class="sidebar-logout">Выйти</button>
      </nav>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter, RouterLink } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.account-layout {
  display: flex;
  min-height: calc(100vh - 80px);
}
.sidebar {
  width: 220px;
  padding: 24px 16px;
  background: var(--bg-white);
  border-right: 2px solid #ffe3cf;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sidebar h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--brand-orange);
}
.sidebar nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.sidebar-link {
  display: block;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  color: var(--brand-purple);
  text-decoration: none;
  transition: background 0.2s, color 0.2s, padding-left 0.2s;
}
.sidebar-link:hover {
  background: #ffe3cf;
  color: var(--brand-orange);
  padding-left: 18px;
}
.sidebar-link.router-link-active {
  background: #ffe3cf;
  color: var(--brand-orange);
  font-weight: 700;
}
.sidebar-logout {
  margin-top: 16px;
  padding: 10px 14px;
  border-radius: 10px;
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 500;
  color: var(--brand-red);
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: background 0.2s;
}
.sidebar-logout:hover { background: #ffeaea; }
.content { flex: 1; padding: 32px; }
</style>
