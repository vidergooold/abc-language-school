<template>
  <div class="account-layout">
    <aside class="sidebar">
      <h3>Личный кабинет</h3>
      <nav>
        <RouterLink to="/account">Профиль</RouterLink>
        <button @click="logout">Выйти</button>
      </nav>
    </aside>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

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
  padding: 16px;
  background: var(--bg-white);
}

.sidebar nav {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.content {
  flex: 1;
  padding: 24px;
}
</style>
