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
      <RouterLink to="/organization/grants" class="nav-link">
        Стипендии и поддержка
      </RouterLink>
      <RouterLink to="/organization/accessibility" class="nav-link">
        Доступная среда
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
