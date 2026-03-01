<template>
  <header class="header">
    <RouterLink to="/" class="logo">ABC School</RouterLink>

    <nav class="nav">
      <RouterLink to="/">Главная</RouterLink>

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

      <RouterLink to="/account" class="nav-item">
        Личный кабинет
      </RouterLink>

      <RouterLink to="/jobs" class="nav-item">
        Хотите работать у нас?
      </RouterLink>

      <RouterLink to="/#feedback" class="nav-item nav-feedback">
        Обратная связь
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
  background: #ffffff;
  border-bottom: 3px solid var(--brand-orange);
}

.logo {
  font-weight: 700;
  font-size: 22px;
  color: var(--brand-purple);
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s;
}

.logo:hover {
  color: var(--brand-orange);
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

/* выпадающие меню */
.nav-dropdown__menu {
  display: none;
  position: absolute;
  top: 120%;
  left: 0;
  flex-direction: column;
  background: #fff7f0;
  padding: 8px 0;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
  min-width: 240px;
  z-index: 10;
}

.nav-dropdown:hover .nav-dropdown__menu {
  display: flex;
}

.nav-dropdown__menu a {
  padding: 6px 12px;
  white-space: nowrap;
  font-size: 14px;
}

.nav-dropdown__menu a:hover {
  background: #ffe3cf;
}

.nav-feedback {
  padding: 6px 14px;
  border-radius: 999px;
  background: var(--brand-orange);
  color: #ffffff;
}
</style>
