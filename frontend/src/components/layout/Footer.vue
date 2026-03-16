<template>
  <footer class="footer">
    <div class="footer__content">
      <div class="footer__left">
        <h2 class="footer__title">Контактная информация</h2>

        <div class="footer__office">
          <h3>Наш офис:</h3>
          <p class="footer__location">📍 Новосибирск</p>
          <p>ул. Бориса Богаткова, 208/2, офис 4, 5</p>
        </div>

        <div class="footer__phones">
          <a href="tel:+79139121809" class="footer__phone">+7 (913) 912-18-09</a>
        </div>

        <p class="footer__email">
          <a href="mailto:info@abc-school.ru">info@abc-school.ru</a>
        </p>

        <div class="footer__docs">
          <RouterLink to="/privacy" class="footer__doc-link">Политика конфиденциальности</RouterLink>
          <RouterLink to="/consent" class="footer__doc-link">Согласие на обработку персональных данных</RouterLink>
        </div>

        <button class="footer__btn" @click="scrollToFeedback">Обратная связь</button>
      </div>

      <div class="footer__right">
        <iframe
          class="footer__map"
          src="https://yandex.ru/map-widget/v1/?um=constructor%3A2176bde44a3a0278af824b3d4e41f7e66ef0d049a83924a08779f616ec73ade1&amp;source=constructor"
          frameborder="0"
          allowfullscreen
        ></iframe>
        <p class="map-note">👆 На карте отмечены все 22 филиала ABC School</p>
      </div>
    </div>

    <div class="footer__copyright">
      <p>© 2026 ABC Language School. Все права защищены.</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

function scrollToFeedback() {
  const el = document.getElementById('feedback')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.footer {
  background: linear-gradient(135deg, var(--brand-dark-red), var(--brand-red));
  color: #ffffff;
  padding: 32px 24px;
  margin-top: 40px;
  font-size: 16px;
}

.footer__content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 32px;
}

.footer__left h2 {
  font-size: 26px;
  margin-bottom: 16px;
}

.footer__office h3 {
  font-size: 18px;
  margin-bottom: 6px;
}

.footer__location {
  font-weight: 700;
  font-size: 18px;
}

.footer__phones {
  margin: 12px 0;
}

.footer__phone,
.footer__email a {
  color: #ffffff;
  font-size: 18px;
  text-decoration: none;
}

.footer__docs {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 14px 0;
}

.footer__doc-link {
  color: #ffe3cf;
  font-size: 14px;
  text-decoration: underline;
  transition: color 0.2s;
}
.footer__doc-link:hover {
  color: #ffffff;
}

.footer__btn {
  background: #ffffff;
  color: var(--brand-purple);
  padding: 10px 20px;
  border-radius: 999px;
  border: none;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 12px;
}

.footer__right {
  position: relative;
  min-height: 320px;
  border-radius: 16px;
  overflow: hidden;
}

.footer__map {
  width: 100%;
  height: 100%;
  min-height: 320px;
  border-radius: 16px;
}

.map-note {
  margin-top: 8px;
  font-size: 14px;
  text-align: center;
  opacity: 0.9;
}

.footer__copyright {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  opacity: 0.8;
}
</style>
