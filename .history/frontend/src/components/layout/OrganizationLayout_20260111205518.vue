<template>
  <div class="org-layout">
    <h1 class="page-title">Сведения об образовательной организации</h1>

    <nav class="sections-nav">
      <RouterLink to="/organization/main" class="nav-link">
        Основные сведения
      </RouterLink>
      <RouterLink to="/organization/structure" class="nav-link">
        Структура и филиалы
      </RouterLink>
      <RouterLink to="/organization/docs" class="nav-link">
        Документы
      </RouterLink>
      <RouterLink to="/organization/education" class="nav-link">
        Образование
      </RouterLink>
      <RouterLink to="/organization/management" class="nav-link">
        Руководство
      </RouterLink>
      <RouterLink to="/organization/staff" class="nav-link">
        Педагогический состав
      </RouterLink>
      <RouterLink to="/organization/facilities" class="nav-link">
        Материально-техническое обеспечение
      </RouterLink>
      <RouterLink to="/organization/services" class="nav-link">
        Платные услуги
      </RouterLink>
      <RouterLink to="/organization/finance" class="nav-link">
        Финансы
      </RouterLink>
      <RouterLink to="/organization/vacancies" class="nav-link">
        Вакантные места
      </RouterLink>
      <RouterLink to="/organization/international" class="nav-link">
        Международное сотрудничество
      </RouterLink>
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
  border: 2px solid transparent;
}

.nav-link:hover {
  background: var(--brand-orange);
  color: #ffffff;
}

.nav-link.router-link-active {
  background: var(--brand-orange);
  color: #ffffff;
}

.org-content {
  background: #ffffff;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
</style>
