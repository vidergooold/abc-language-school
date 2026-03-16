<template>
  <div class="org-section">
    <h2 class="section-title">Основные сведения</h2>

    <h3>Об образовательной организации</h3>
    <p>
      <strong>Полное и сокращенное наименование:</strong><br />
      Частное учреждение дополнительного образования Лингвоцентр "Эй Би Си"
      (ЧУДО Лингвоцентр "Эй Би Си")
    </p>
    <p>
      <strong>Дата создания:</strong><br />
      08.06.2005
    </p>

    <h3>Учредители образовательной организации</h3>
    <p><strong>Министерство образования Новосибирской области</strong></p>
    <p>
      <strong>Адрес:</strong> 630007, Новосибирская область, город Новосибирск,
      Красный пр-кт, д. 18<br />
      <strong>Телефон:</strong>
      <a href="tel:+73832387320">(383) 238-73-20</a> (приемная)<br />
      <strong>Сайт:</strong>
      <a href="https://minobr.nso.ru/" target="_blank">https://minobr.nso.ru/</a>
    </p>

    <h3>Место нахождения образовательной организации</h3>
    <p>
      <strong>Юридический адрес:</strong><br />
      630089, Российская Федерация, Сибирский федеральный округ, Новосибирская
      обл., г. Новосибирск, ул. Бориса Богаткова, дом 208, корпус 2
    </p>

    <div class="map-container">
      <iframe
        src="https://yandex.ru/map-widget/v1/?um=constructor%3A2176bde44a3a0278af824b3d4e41f7e66ef0d049a83924a08779f616ec73ade1&amp;source=constructor"
        width="100%"
        height="400"
        frameborder="0"
      ></iframe>
    </div>

    <h3>Режим и график работы</h3>
    <p>
      <strong>Режим работы:</strong><br />
      ПН - ПТ: с 09:00 до 20:00<br />
      СБ: с 10:00 до 15:00<br />
      ВС: выходной
    </p>

    <h3>Контакты</h3>
    <p>
      <strong>Контактный телефон:</strong><br />
      <a href="tel:+73832091990">(383) 209-19-90</a><br />
      <a href="tel:2141809">214-18-09</a>
    </p>
    <p>
      <strong>Адрес электронной почты:</strong><br />
      <a href="mailto:school.abc@mail.ru">school.abc@mail.ru</a>
    </p>
    <p>
      <strong>Адрес официального сайта:</strong><br />
      <a href="http://abc-school.ru/" target="_blank">http://abc-school.ru/</a>
    </p>

    <h3>Лицензия на осуществление образовательной деятельности</h3>
    <p>Лицензия на осуществление образовательной деятельности ЧУДО Лингвоцентр "Эй Би Си"</p>

    <div class="license-gallery">
      <div
        v-for="(img, i) in licenseImages"
        :key="i"
        class="license-thumb"
        @click="openLightbox(i)"
      >
        <img :src="img" :alt="'Лицензия, стр. ' + (i + 1)" />
        <span class="license-page">Стр. {{ i + 1 }}</span>
      </div>
    </div>

    <!-- Lightbox -->
    <div v-if="lightboxIndex !== null" class="lightbox" @click.self="closeLightbox">
      <button class="lightbox__close" @click="closeLightbox">×</button>
      <button class="lightbox__prev" @click="prevImage" v-if="lightboxIndex > 0">‹</button>
      <img class="lightbox__img" :src="licenseImages[lightboxIndex]" :alt="'Лицензия, стр. ' + (lightboxIndex + 1)" />
      <button class="lightbox__next" @click="nextImage" v-if="lightboxIndex < licenseImages.length - 1">›</button>
    </div>

    <h3>Государственная аккредитация</h3>
    <p>Государственная аккредитация не требуется.</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const licenseImages = [
  '/docs/license/l1.jpg',
  '/docs/license/l2.jpg',
  '/docs/license/l3.jpg',
  '/docs/license/l4.jpg',
]

const lightboxIndex = ref<number | null>(null)

function openLightbox(i: number) {
  lightboxIndex.value = i
  document.body.style.overflow = 'hidden'
}

function closeLightbox() {
  lightboxIndex.value = null
  document.body.style.overflow = ''
}

function prevImage() {
  if (lightboxIndex.value !== null && lightboxIndex.value > 0) lightboxIndex.value--
}

function nextImage() {
  if (lightboxIndex.value !== null && lightboxIndex.value < licenseImages.length - 1) lightboxIndex.value++
}
</script>

<style scoped>
.org-section {
  font-size: 17px;
  line-height: 1.6;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 20px;
}

h3 {
  font-size: 20px;
  font-weight: 700;
  margin-top: 24px;
  margin-bottom: 12px;
}

p {
  margin-bottom: 16px;
}

a {
  color: var(--brand-orange);
  text-decoration: none;
}
a:hover { text-decoration: underline; }

.map-container {
  margin: 24px 0;
  border-radius: 16px;
  overflow: hidden;
}

/* License gallery */
.license-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.license-thumb {
  cursor: pointer;
  border-radius: 10px;
  overflow: hidden;
  border: 2px solid #ffe3cf;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  background: #fff;
}

.license-thumb:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.license-thumb img {
  width: 100%;
  display: block;
  object-fit: cover;
  aspect-ratio: 3/4;
}

.license-page {
  display: block;
  text-align: center;
  padding: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-purple);
  background: #fff7f0;
}

/* Lightbox */
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.88);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox__img {
  max-height: 90vh;
  max-width: 90vw;
  border-radius: 10px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5);
}

.lightbox__close {
  position: absolute;
  top: 20px;
  right: 28px;
  background: none;
  border: none;
  color: #fff;
  font-size: 40px;
  cursor: pointer;
  line-height: 1;
}

.lightbox__prev,
.lightbox__next {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.15);
  border: none;
  color: #fff;
  font-size: 48px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: background 0.2s;
}
.lightbox__prev { left: 20px; }
.lightbox__next { right: 20px; }
.lightbox__prev:hover,
.lightbox__next:hover { background: rgba(255,255,255,0.3); }
</style>
