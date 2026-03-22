<template>
  <div class="org-layout">
    <h1 class="page-title">Сведения об образовательной организации</h1>

    <nav class="sections-nav">
      <RouterLink to="/organization/main" class="nav-link">Основные сведения</RouterLink>
      <RouterLink to="/organization/structure" class="nav-link">Структура и филиалы</RouterLink>
      <RouterLink to="/organization/docs" class="nav-link">Документы</RouterLink>
      <RouterLink to="/organization/education" class="nav-link">Образование</RouterLink>
      <RouterLink to="/organization/management" class="nav-link">Руководство</RouterLink>
      <RouterLink to="/organization/staff" class="nav-link">Педагогический состав</RouterLink>
      <RouterLink to="/organization/facilities" class="nav-link">Материально-техническое обеспечение</RouterLink>
      <RouterLink to="/organization/services" class="nav-link">Платные услуги</RouterLink>
      <RouterLink to="/organization/finance" class="nav-link">Финансы</RouterLink>
      <RouterLink to="/organization/vacancies" class="nav-link">Вакантные места</RouterLink>
      <RouterLink to="/organization/grants" class="nav-link">Стипендии и поддержка</RouterLink>
      <RouterLink to="/organization/accessibility" class="nav-link">Доступная среда</RouterLink>
      <RouterLink to="/organization/international" class="nav-link">Международное сотрудничество</RouterLink>
    </nav>

    <div class="org-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.org-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 24px;
}

.sections-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 220px;
  float: left;
  margin-right: 32px;
}

.nav-link {
  display: block;
  padding: 10px 14px;
  border-radius: 8px;
  color: var(--brand-purple);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: background 0.2s;
}

.nav-link:hover {
  background: #f5f0ff;
}

.nav-link.router-link-active {
  background: var(--brand-purple);
  color: #fff;
}

.org-content {
  overflow: hidden;
}
</style>
