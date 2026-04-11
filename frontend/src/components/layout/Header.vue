<template>
  <header class="header">
    <RouterLink to="/" class="logo">
      <img src="/logo.png" alt="ABC Лингвоцентр" class="logo-img" />
    </RouterLink>

    <nav class="nav">
      <RouterLink to="/" class="nav-link">Главная</RouterLink>

      <div
        class="nav-item nav-dropdown"
        @mouseenter="openMenu('org')"
        @mouseleave="closeMenu('org')"
      >
        <span class="nav-dropdown__trigger" :class="{ active: openMenuName === 'org' }">
          Сведения об организации
        </span>
        <div class="nav-dropdown__menu" v-show="openMenuName === 'org'">
          <div class="nav-dropdown__inner">
            <RouterLink to="/organization/main" @click="closeAll">Основные сведения</RouterLink>
            <RouterLink to="/organization/structure" @click="closeAll">Структура и филиалы</RouterLink>
            <RouterLink to="/organization/docs" @click="closeAll">Документы</RouterLink>
            <RouterLink to="/organization/education" @click="closeAll">Образование</RouterLink>
            <RouterLink to="/organization/standards" @click="closeAll">Образовательные стандарты</RouterLink>
            <RouterLink to="/organization/staff" @click="closeAll">Руководство и педсостав</RouterLink>
            <RouterLink to="/organization/mto" @click="closeAll">Материально-техническое обеспечение</RouterLink>
            <RouterLink to="/organization/grants" @click="closeAll">Стипендии и гранты</RouterLink>
            <RouterLink to="/organization/paid" @click="closeAll">Платные услуги</RouterLink>
            <RouterLink to="/organization/budget" @click="closeAll">Финансово-хозяйственная деятельность</RouterLink>
            <RouterLink to="/organization/vacancy" @click="closeAll">Вакантные места</RouterLink>
            <RouterLink to="/organization/accessible" @click="closeAll">Доступная среда</RouterLink>
            <RouterLink to="/organization/international" @click="closeAll">Международное сотрудничество</RouterLink>
          </div>
        </div>
      </div>

      <div
        class="nav-item nav-dropdown"
        @mouseenter="openMenu('clients')"
        @mouseleave="closeMenu('clients')"
      >
        <span class="nav-dropdown__trigger" :class="{ active: openMenuName === 'clients' }">
          Действующим клиентам
        </span>
        <div class="nav-dropdown__menu" v-show="openMenuName === 'clients'">
          <div class="nav-dropdown__inner">
            <RouterLink to="/clients/info" @click="closeAll">Важная информация</RouterLink>
            <RouterLink to="/clients/holidays" @click="closeAll">Каникулы и выходные дни</RouterLink>
            <RouterLink to="/clients/payment" @click="closeAll">Оплата обучения, перерасчет, возврат</RouterLink>
            <RouterLink to="/clients/tax" @click="closeAll">Оформление налогового вычета</RouterLink>
          </div>
        </div>
      </div>

      <RouterLink to="/testing" class="nav-link">Пройти тестирование</RouterLink>
      <RouterLink to="/enroll" class="nav-link">Стать участником</RouterLink>
      <RouterLink to="/account" class="nav-link">Личный кабинет</RouterLink>
      <RouterLink to="/jobs" class="nav-link">Хотите работать у нас?</RouterLink>

      <a href="#feedback" class="nav-feedback" @click="scrollToFeedback">Обратная связь</a>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const openMenuName = ref<string | null>(null)

function openMenu(name: string) {
  openMenuName.value = name
}

function closeMenu(name: string) {
  if (openMenuName.value === name) {
    openMenuName.value = null
  }
}

function closeAll() {
  openMenuName.value = null
}

function scrollToFeedback(e: Event) {
  e.preventDefault()
  closeAll()
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
  position: sticky;
  top: 0;
  z-index: 100;
}
.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  cursor: pointer;
  transition: opacity 0.2s;
  flex-shrink: 0;
}
.logo:hover {
  opacity: 0.8;
}
.logo-img {
  height: 70px;
  width: auto;
  object-fit: contain;
}
.nav {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: nowrap;
}
.nav-link {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-purple);
  text-decoration: none;
  padding: 5px 7px;
  border-radius: 8px;
  transition: background 0.2s, color 0.2s;
  white-space: nowrap;
}
.nav-link:hover {
  background: #ffe3cf;
  color: var(--brand-orange);
}
.nav-link.router-link-active {
  color: var(--brand-orange);
  background: #fff0e6;
}
.nav-item {
  position: relative;
  cursor: pointer;
}
.nav-dropdown__trigger {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-purple);
  padding: 5px 7px;
  border-radius: 8px;
  transition: background 0.2s, color 0.2s;
  user-select: none;
  display: block;
  white-space: nowrap;
}
.nav-dropdown__trigger.active,
.nav-dropdown__trigger:hover {
  background: #ffe3cf;
  color: var(--brand-orange);
}
.nav-dropdown__menu {
  position: absolute;
  top: 100%;
  left: 0;
  padding-top: 6px;
  z-index: 200;
}
.nav-dropdown__inner {
  display: flex;
  flex-direction: column;
  background: #fff7f0;
  padding: 8px 0;
  border-radius: 12px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.15);
  min-width: 290px;
  border: 1px solid #ffe3cf;
  animation: dropIn 0.15s ease;
}
@keyframes dropIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}
.nav-dropdown__inner a {
  padding: 10px 18px;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 500;
  color: var(--brand-purple);
  text-decoration: none;
  transition: background 0.15s, padding-left 0.15s;
}
.nav-dropdown__inner a:hover {
  background: #ffe3cf;
  color: var(--brand-orange);
  padding-left: 24px;
}
.nav-dropdown__inner a.router-link-active {
  background: #ffe3cf;
  color: var(--brand-orange);
  font-weight: 700;
}
.nav-feedback {
  padding: 6px 13px;
  border-radius: 999px;
  background: var(--brand-orange);
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
  font-size: 13px;
  transition: background 0.2s, transform 0.15s;
  cursor: pointer;
  white-space: nowrap;
}
.nav-feedback:hover {
  background: var(--brand-red);
  transform: translateY(-1px);
}
</style>
