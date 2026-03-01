<template>
  <div class="feedback">
    <h2 class="feedback__title">Обратная связь</h2>

    <p class="feedback__org">
      Частное учреждение дополнительного образования<br />
      «Лингвоцентр &quot;Эй Би Си&quot;»
    </p>

    <p class="feedback__contact">
      <a href="tel:+73832091990">(383) 209-19-90</a><br />
      Новосибирская обл., г. Новосибирск
    </p>

    <form class="feedback__form" @submit.prevent="submit">
      <div class="field">
        <label>Ваше имя *</label>
        <input v-model="name" type="text" required />
      </div>

      <div class="field">
        <label>Ваш телефон *</label>
        <input v-model="phone" type="tel" required />
      </div>

      <div class="field">
        <label>Ваш e‑mail</label>
        <input v-model="email" type="email" />
      </div>

      <div class="field">
        <label>Сообщение</label>
        <textarea v-model="message" rows="4" />
      </div>

      <button class="submit-btn" type="submit">
        Отправить
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const name = ref('')
const phone = ref('')
const email = ref('')
const message = ref('')

function submit() {
  // здесь позже можно добавить отправку на backend
  alert('Спасибо! Мы свяжемся с вами.')
}
</script>

<style scoped>
.feedback {
  max-width: 520px;
  margin: 0 auto;
  padding: 24px;
  background: #f5f0ff;
  border-radius: 16px;
}

.feedback__title {
  font-size: 24px;
  margin-bottom: 12px;
  text-align: center;
}

.feedback__org {
  font-size: 16px;
  text-align: center;
  margin-bottom: 8px;
}

.feedback__contact {
  font-size: 15px;
  text-align: center;
  margin-bottom: 20px;
}

.feedback__contact a {
  color: var(--brand-orange);
  text-decoration: none;
}

.feedback__form .field {
  display: flex;
  flex-direction: column;
  margin-bottom: 14px;
}

.feedback__form label {
  font-size: 14px;
  margin-bottom: 4px;
}

.feedback__form input,
.feedback__form textarea {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  border-radius: 999px;
  border: none;
  background: var(--brand-orange);
  color: #fff;
  font-size: 16px;
  cursor: pointer;
}
</style>
