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

      <ConsentCheckboxes
        v-model="consent"
        :privacy-url="privacyUrl"
        :consent-url="consentUrl"
      />

      <button class="submit-btn" type="submit" :disabled="!consent.privacy || !consent.personalData">
        Отправить
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import http from '@/api/http'
import ConsentCheckboxes from '@/components/ui/ConsentCheckboxes.vue'

const name = ref('')
const phone = ref('')
const email = ref('')
const message = ref('')
const consent = ref({ privacy: false, personalData: false })

const privacyUrl = '/privacy'
const consentUrl = '/consent'

async function submit() {
  if (!consent.value.privacy || !consent.value.personalData) {
    alert('Пожалуйста, подтвердите согласие.')
    return
  }
  try {
    await http.post('/forms/feedback', {
      name: name.value,
      phone: phone.value,
      email: email.value,
      message: message.value,
    })
    alert('Спасибо! Ваше сообщение отправлено. Мы свяжемся с вами.')
    name.value = ''
    phone.value = ''
    email.value = ''
    message.value = ''
    consent.value = { privacy: false, personalData: false }
  } catch (error) {
    alert('Ошибка отправки. Попробуйте позже.')
    console.error(error)
  }
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
  font-size: 26px;
  margin-bottom: 12px;
  text-align: center;
  font-weight: 700;
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
  font-size: 15px;
  margin-bottom: 4px;
  font-weight: 500;
}

.feedback__form input,
.feedback__form textarea {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 15px;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  border-radius: 999px;
  border: none;
  background: var(--brand-orange);
  color: #fff;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
