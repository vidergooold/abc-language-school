<template>
  <footer class="footer">
    <div class="footer__content">
      <!-- Левая колонка: контакты -->
      <div class="footer__left">
        <h2 class="footer__title">Контактная информация</h2>

        <div class="footer__office">
          <h3>Наш офис:</h3>
          <p class="footer__location">📍 Новосибирск</p>
          <p>ул. Бориса Богаткова, 208/2, офис 4, 5</p>
        </div>

        <div class="footer__phones">
          <a href="tel:+79139121809" class="footer__phone">
            (913) 912-18-09
          </a>
        </div>

        <p class="footer__email">
          <a href="mailto:info@abc-school.ru">info@abc-school.ru</a>
        </p>

        <div class="footer__docs">
          <a href="/docs/Politika_obrabotki_personalnykh_dannykh.docx" class="footer__doc-link" target="_blank">
            Политика конфиденциальности
          </a>
          <a href="/docs/Soglasie_polzovatelia_saita_na_obrabotku_personalnykh_dannykh.docx" class="footer__doc-link" target="_blank">
            Согласие на обработку персональных данных
          </a>
        </div>

        <button class="footer__btn" @click="scrollToFeedback">
          Обратная связь
        </button>
      </div>

      <!-- Правая колонка: карта с филиалами -->
      <div class="footer__right">
        <iframe
          class="footer__map"
          src="https://yandex.ru/map-widget/v1/?um=constructor%3A2176bde44a3a0278af824b3d4e41f7e66ef0d049a83924a08779f616ec73ade1&amp;source=constructor"
          frameborder="0"
          allowfullscreen
        ></iframe>
        <p class="map-note">
          👆 На карте отмечены все 22 филиала ABC School
        </p>
      </div>
    </div>

    <!-- Все филиалы списком -->
    <details class="footer__branches">
      <summary class="footer__branches-title">
        Все места обучения (22 филиала)
      </summary>

      <div class="branches-grid">
        <div class="branch" v-for="branch in branches" :key="branch.id">
          <h4>{{ branch.name }}</h4>
          <p class="branch__address">📍 {{ branch.address }}</p>
          <p class="branch__phone">
            <a :href="`tel:${branch.phone}`">{{ branch.phoneDisplay }}</a>
          </p>
          <RouterLink :to="`/courses?branch=${branch.id}`" class="branch__more">Подробнее →</RouterLink>
        </div>
      </div>
    </details>

    <div class="footer__copyright">
      <p>© 2026 ABC Language School. Все права защищены.</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

function scrollToFeedback() {
  const el = document.getElementById('feedback')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const branches = ref([
  { id: 1, name: 'Офис г. Новосибирск (главный)', address: 'ул. Бориса Богаткова, 208/2, офис 4, 5', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 2, name: 'Филиал в МАОУ Гимназия 11 «Гармония»', address: 'ул. Федосеева, д. 38', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 3, name: 'Филиал в МБОУ СОШ №56', address: 'ул. Планировочная, д. 7', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 4, name: 'Филиал в МБОУ СОШ №188', address: 'ул. Курганская, д. 36а', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 5, name: 'Филиал в МАОУ СОШ №218', address: 'Красный проспект, д. 320/1', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 6, name: 'Филиал в МАОУ «Гимназия №7 «Сибирская»', address: 'ул. Зорге, д. 42а', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 7, name: 'Филиал в МБОУ СОШ №186', address: 'ул. Бориса Богаткова, д. 189', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 8, name: 'Филиал в МБОУ СОШ №11', address: 'ул. Бориса Богаткова, д. 187', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 9, name: 'Филиал в МБОУ СОШ №2', address: 'ул. Чехова, д. 271', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 10, name: 'Филиал в МБОУ СОШ №199', address: 'ул. Лазурная, д. 27', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 11, name: 'Филиал в МБОУ СОШ №155', address: 'Ключ-Камышенское Плато, д. 1А', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 12, name: 'Филиал в МАОУ ЛИТ', address: 'ул. Римского-Корсакова, д. 13', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 13, name: 'Филиал в МБОУ СОШ №195', address: 'ул. В. Высоцкого, д. 1', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 14, name: 'Филиал в МАОУ НГПЛ', address: 'ул. Декабристов, д. 86', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 15, name: 'Филиал в МБОУ Гимназия №9', address: 'ул. Калинина, д. 255', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 16, name: 'Филиал в МАОУ НЭЛ', address: 'ул. Крылова, д. 44', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 17, name: 'Филиал в МАОУ СОШ №216', address: 'ул. Виталия Потылицына, д. 9', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 18, name: 'Филиал в МАОУ СОШ №217', address: 'ул. Виктора Шевелева, д. 3', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 19, name: 'Филиал в МБОУ Гимназия №5', address: 'ул. Академическая, д. 9', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 20, name: 'Филиал в МБОУ СОШ №121 «Академическая»', address: 'ул. Тружеников, д. 10', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 21, name: 'Филиал в МБОУ СОШ №61 им. Н.М. Иванова', address: 'ул. Иванова, д. 9', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
  { id: 22, name: 'Филиал в МАОУ СОШ №222', address: 'ул. Кубовая, д. 100', phone: '+79139121809', phoneDisplay: '(913) 912-18-09' },
])
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

.footer__branches {
  margin-top: 24px;
  background: rgba(255, 255, 255, 0.1);
  padding: 16px;
  border-radius: 12px;
}

.footer__branches-title {
  font-size: 20px;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
}

.branches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.branch {
  background: rgba(255, 255, 255, 0.08);
  padding: 12px;
  border-radius: 10px;
}

.branch h4 {
  font-size: 16px;
  margin-bottom: 6px;
}

.branch__address,
.branch__phone {
  font-size: 14px;
  margin: 4px 0;
}

.branch__phone a {
  color: #ffffff;
  text-decoration: none;
}

.branch__more {
  display: inline-block;
  margin-top: 8px;
  font-size: 13px;
  color: #ffe3cf;
  text-decoration: underline;
  transition: color 0.2s;
}
.branch__more:hover {
  color: #ffffff;
}

.footer__copyright {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  opacity: 0.8;
}
</style>
