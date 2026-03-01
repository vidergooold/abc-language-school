<template>
  <header class="header">
    <RouterLink to="/" class="logo">
      <img src="/logo.png" alt="ABC School" class="logo-img" />
    </RouterLink>

    <nav class="nav">
      <RouterLink to="/">Главная</RouterLink>

      <div class="nav-item nav-dropdown">
        <span>Сведения об организации</span>
        <div class="nav-dropdown__menu">
          <RouterLink to="/organization/main">Основные сведения</RouterLink>
          <RouterLink to="/organization/structure">
            Структура и управление
          </RouterLink>
          <RouterLink to="/organization/docs">Документы</RouterLink>
          <RouterLink to="/organization/education">Образование</RouterLink>
          <RouterLink to="/organization/management">Руководство</RouterLink>
          <RouterLink to="/organization/staff">Педагогический состав</RouterLink>
          <RouterLink to="/organization/facilities">
            Материально-техническое обеспечение
          </RouterLink>
          <RouterLink to="/organization/services">
            Платные образовательные услуги
          </RouterLink>
          <RouterLink to="/organization/finance">
            Финансово-хозяйственная деятельность
          </RouterLink>
          <RouterLink to="/organization/vacancies">Вакантные места</RouterLink>
          <RouterLink to="/organization/international">
            Международное сотрудничество
          </RouterLink>
        </div>
      </div>

      <div class="nav-item nav-dropdown">
        <span>Действующим клиентам</span>
        <div class="nav-dropdown__menu">
          <RouterLink to="/clients/important">Важная информация</RouterLink>
          <RouterLink to="/clients/holidays">
            Каникулы и выходные дни
          </RouterLink>
          <RouterLink to="/clients/payment">
            Оплата, перерасчет, возврат
          </RouterLink>
          <RouterLink to="/clients/tax">Налоговый вычет</RouterLink>
        </div>
      </div>

      <div class="nav-item nav-dropdown">
        <span>Пройти тестирование</span>
        <div class="nav-dropdown__menu">
          <RouterLink to="/testing">1–5 классы</RouterLink>
          <RouterLink to="/testing">6–8 классы</RouterLink>
          <RouterLink to="/testing">9–11 классы, взрослые</RouterLink>
        </div>
      </div>

      <div class="nav-item nav-dropdown">
        <span>Стать участником</span>
        <div class="nav-dropdown__menu">
          <RouterLink to="/enroll">Анкета школьника</RouterLink>
          <RouterLink to="/enroll">Анкета взрослого</RouterLink>
          <RouterLink to="/enroll">Анкета дошкольника</RouterLink>
        </div>
      </div>

      <RouterLink to="/account" class="nav-item">
        Личный кабинет
      </RouterLink>

      <RouterLink to="/jobs" class="nav-item">
        Хотите работать у нас?
      </RouterLink>

      <a href="/#feedback" class="nav-item nav-feedback" @click="scrollToFeedback">
        Обратная связь
      </a>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

function scrollToFeedback(e: Event) {
  e.preventDefault()
  const el = document.getElementById('feedback')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  } else {
    window.location.href = '/#feedback'
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #ffffff;
  border-bottom: 3px solid var(--brand-orange);
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo:hover {
  opacity: 0.8;
}

.logo-img {
  height: 50px; /* настрой высоту под свой логотип */
  width: auto;
  object-fit: contain;
}

.nav {
  display: flex;
  gap: 16px;
  align-items: center;
}

.nav a,
.nav-item span {
  font-size: 16px;
  font-weight: 600;
  color: var(--brand-purple);
  text-decoration: none;
}

.nav-item {
  position: relative;
  cursor: pointer;
}

.nav-dropdown__menu {
  display: none;
  position: absolute;
  top: 120%;
  left: 0;
  flex-direction: column;
  background: #fff7f0;
  padding: 12px 0;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
  min-width: 280px;
  z-index: 10;
}

.nav-dropdown:hover .nav-dropdown__menu {
  display: flex;
}

.nav-dropdown__menu a {
  padding: 12px 16px;
  white-space: nowrap;
  font-size: 15px;
}

.nav-dropdown__menu a:hover {
  background: #ffe3cf;
}

.nav-feedback {
  padding: 8px 16px;
  border-radius: 999px;
  background: var(--brand-orange);
  color: #ffffff;
  text-decoration: none;
}

.nav-feedback:hover {
  background: var(--brand-red);
}
</style>
