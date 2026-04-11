<template>
  <div class="clients-layout">
    <h1 class="page-title">Действующим клиентам</h1>
    <p class="page-subtitle">Вся необходимая информация для наших учеников и родителей</p>

    <nav class="sections-nav">
      <RouterLink to="/clients/info" class="nav-link">Важная информация</RouterLink>
      <RouterLink to="/clients/holidays" class="nav-link">Каникулы и выходные дни</RouterLink>
      <RouterLink to="/clients/payment" class="nav-link">Оплата обучения, перерасчет, возврат</RouterLink>
      <RouterLink to="/clients/tax" class="nav-link">Оформление налогового вычета</RouterLink>
    </nav>

    <div class="clients-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.clients-layout {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.sections-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 32px;
  padding: 16px;
  background: #ffe3cf;
  border-radius: 12px;
}

.nav-link {
  padding: 8px 16px;
  background: var(--bg-white);
  color: var(--brand-purple);
  text-decoration: none;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}

.nav-link:hover {
  background: var(--brand-orange);
  color: #ffffff;
}

.nav-link.router-link-active {
  background: var(--brand-orange);
  color: #ffffff;
}

.clients-content {
  background: #ffffff;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
</style>
