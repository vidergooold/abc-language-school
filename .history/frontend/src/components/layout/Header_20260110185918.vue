<template>
  <header class="header">
    <div class="logo">ABC School</div>
    <nav class="nav">
      <RouterLink to="/">Главная</RouterLink>
      <RouterLink to="/courses">Курсы</RouterLink>
      <RouterLink to="/login">Войти</RouterLink>
      <RouterLink to="/register" class="cta">Регистрация</RouterLink>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-white);
}

.logo {
  font-weight: 700;
  font-size: 20px;
}

.nav a {
  margin-left: 12px;
  text-decoration: none;
  color: var(--text-main);
  font-size: 16px;
}

.cta {
  padding: 8px 14px;
  background: var(--brand-orange);
  color: white;
  border-radius: var(--border-radius);
}
</style>
