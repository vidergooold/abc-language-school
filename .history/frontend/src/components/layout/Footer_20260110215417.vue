<template>
  <footer class="footer">
    <div class="footer__content">
      <!-- Левая колонка: контакты -->
      <div class="footer__left">
        <h2 class="footer__title">Контактная информация</h2>

        <div class="footer__office">
          <h3>Наш офис:</h3>
          <p class="footer__location">📍 Новосибирск</p>
          <p>Новосибирская обл., г. Новосибирск</p>
        </div>

        <div class="footer__phones">
          <a href="tel:+73832091990" class="footer__phone">
            📞 +7 (383) 209-19-90
          </a>
        </div>

        <p class="footer__email">
          📧 <a href="mailto:info@abc-school.ru">info@abc-school.ru</a>
        </p>

        <div class="footer__schedule">
          <p>🕐 Пн–Пт: 09:00–20:00</p>
          <p>Сб: 11:00–15:00</p>
          <p>Вс: выходной</p>
        </div>

        <button class="footer__btn" @click="scrollToFeedback">
          Обратная связь
        </button>
      </div>

      <!-- Правая колонка: карта со всеми филиалами -->
      <div class="footer__right">
        <div id="map" class="footer__map"></div>
      </div>
    </div>

    <!-- Все филиалы списком -->
    <details class="footer__branches">
      <summary class="footer__branches-title">Все места обучения (22 филиала)</summary>

      <div class="branches-grid">
        <div class="branch" v-for="branch in branches" :key="branch.id">
          <h4>{{ branch.name }}</h4>
          <p class="branch__address">📍 {{ branch.address }}</p>
          <p class="branch__phone">
            📞 <a :href="`tel:${branch.phone}`">{{ branch.phoneDisplay }}</a>
          </p>
          <p class="branch__schedule">🕐 {{ branch.schedule }}</p>
        </div>
      </div>
    </details>

    <div class="footer__copyright">
      <p>© 2026 ABC Language School. Все права защищены.</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

function scrollToFeedback() {
  const el = document.getElementById('feedback')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const branches = ref([
  { id: 1, name: 'Офис (главный)', address: 'ул. Бориса Богаткова, 208/2', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн–Пт 9:00–20:00', coords: [55.028739, 82.927384] },
  { id: 2, name: 'МАОУ Гимназия 11', address: 'ул. Федосеева, д. 38', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн–Пт 9:50–18:30', coords: [54.987234, 82.897456] },
  { id: 3, name: 'МБОУ СОШ №56', address: 'ул. Планировочная, д. 7', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн/Чт 11:30–15:30', coords: [54.955123, 83.101234] },
  { id: 4, name: 'МБОУ СОШ №188', address: 'ул. Курганская, д. 36а', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн–Пт 11:00–19:30', coords: [55.012345, 82.934567] },
  { id: 5, name: 'МАОУ СОШ №218', address: 'Красный проспект, 320/1', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн–Чт 10:30–16:00', coords: [54.983456, 82.896789] },
  // добавь остальные филиалы с примерными координатами
])

onMounted(() => {
  loadYandexMap()
})

function loadYandexMap() {
  const script = document.createElement('script')
  script.src = 'https://api-maps.yandex.ru/2.1/?apikey=YOUR_API_KEY&lang=ru_RU'
  script.onload = initMap
  document.head.appendChild(script)
}

function initMap() {
  // @ts-ignore
  ymaps.ready(() => {
    // @ts-ignore
    const map = new ymaps.Map('map', {
      center: [55.028739, 82.927384], // центр Новосибирска
      zoom: 11,
    })

    branches.value.forEach((branch) => {
      // @ts-ignore
      const placemark = new ymaps.Placemark(
        branch.coords,
        {
          balloonContent: `<strong>${branch.name}</strong><br>${branch.address}<br>${branch.schedule}`,
        },
        {
          preset: 'islands#redDotIcon',
        }
      )
      map.geoObjects.add(placemark)
    })
  })
}
</script>

<style scoped>
.footer {
  background: linear-gradient(135deg, var(--brand-purple), #1e1770);
  color: #ffffff;
  padding: 32px 24px;
  margin-top: 40px;
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

.footer__schedule {
  margin: 16px 0;
  font-size: 16px;
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
.branch__phone,
.branch__schedule {
  font-size: 14px;
  margin: 4px 0;
}

.branch__phone a {
  color: #ffffff;
  text-decoration: none;
}

.footer__copyright {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  opacity: 0.8;
}
</style>
