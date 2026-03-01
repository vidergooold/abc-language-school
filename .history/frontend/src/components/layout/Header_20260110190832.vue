<template>
  <header class="header">
    <div class="logo">ABC School</div>

    <nav class="nav">
      <RouterLink to="/">Главная</RouterLink>

      <!-- Сведения об образовательной организации -->
      <div class="nav-item nav-dropdown">
        <span>Сведения об организации</span>
        <div class="nav-dropdown__menu">
          <RouterLink to="/organization#main">Основные сведения</RouterLink>
          <RouterLink to="/organization#structure">
            Структура и управление
          </RouterLink>
          <RouterLink to="/organization#docs">Документы</RouterLink>
          <RouterLink to="/organization#education">Образование</RouterLink>
          <RouterLink to="/organization#staff">Педагогический состав</RouterLink>
          <RouterLink to="/organization#services">
            Платные образовательные услуги
          </RouterLink>
          <RouterLink to="/organization#finance">
            Финансово-хозяйственная деятельность
          </RouterLink>
        </div>
      </div>

      <!-- Действующим клиентам -->
      <div class="nav-item nav-dropdown">
        <span>Действующим клиентам</span>
        <div class="nav-dropdown__menu">
          <RouterLink to="/clients#important">Важная информация</RouterLink>
          <RouterLink to="/clients#holidays">
            Каникулы и выходные дни
          </RouterLink>
          <RouterLink to="/clients#payment">
            Оплата, перерасчет, возврат
          </RouterLink>
          <RouterLink to="/clients#tax">
            Налоговый вычет
          </RouterLink>
        </div>
      </div>

      <!-- Пройти тестирование -->
      <div class="nav-item nav-dropdown">
        <span>Пройти тестирование</span>
        <div class="nav-dropdown__menu">
          <RouterLink to="/testing#1-5">1–5 классы</RouterLink>
          <RouterLink to="/testing#6-8">6–8 классы</RouterLink>
          <RouterLink to="/testing#9-11">
            9–11 классы, взрослые
          </RouterLink>
        </div>
      </div>

      <!-- Стать участником -->
      <div class="nav-item nav-dropdown">
        <span>Стать участником</span>
        <div class="nav-dropdown__menu">
          <RouterLink to="/enroll#child">Анкета школьника</RouterLink>
          <RouterLink to="/enroll#adult">Анкета взрослого</RouterLink>
          <RouterLink to="/enroll#preschool">
            Анкета дошкольника
          </RouterLink>
        </div>
      </div>

      <!-- Личный кабинет -->
      <RouterLink to="/account" class="nav-item">
        Личный кабинет
      </RouterLink>

      <!-- Хотите работать у нас? -->
      <RouterLink to="/jobs" class="nav-item">
        Хотите работать у нас?
      </RouterLink>
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
  padding: 12px 16px;
  background: var(--bg-white);
}

.logo {
  font-weight: 700;
  font-size: 20px;
}

.nav {
  display: flex;
  gap: 16px;
  align-items: center;
}

.nav-item {
  position: relative;
  font-size: 15px;
  cursor: pointer;
  color: var(--text-main);
}

.nav a {
  text-decoration: none;
  color: var(--text-main);
}

/* Выпадающие меню */
.nav-dropdown:hover .nav-dropdown__menu {
  display: flex;
}

.nav-dropdown__menu {
  display: none;
  position: absolute;
  top: 120%;
  left: 0;
  flex-direction: column;
  background: var(--bg-white);
  padding: 8px 0;
  border-radius: 8px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
  min-width: 220px;
  z-index: 10;
}

.nav-dropdown__menu a {
  padding: 6px 12px;
  white-space: nowrap;
  font-size: 14px;
}

.nav-dropdown__menu a:hover {
  background: #f3f4f6;
}
</style>
