<template>
  <div class="jobs-page">
    <h1 class="page-title">Стать преподавателем</h1>
    <p class="page-subtitle">Заполните анкету, и мы рассмотрим вашу кандидатуру</p>

    <form class="form" @submit.prevent="submit">
      <div class="field">
        <label>ФИО *</label>
        <input v-model="form.fio" type="text" required />
      </div>

      <div class="field">
        <label>Дата и место рождения *</label>
        <textarea v-model="form.birthInfo" rows="2" required></textarea>
      </div>

      <div class="field">
        <label>Семейное положение *</label>
        <input v-model="form.maritalStatus" type="text" required />
      </div>

      <div class="field">
        <label>Образование (в том числе курсы) *</label>
        <textarea v-model="form.education" rows="4" required></textarea>
      </div>

      <div class="field">
        <label>Трудовой опыт (организация, период работы, должность) *</label>
        <textarea v-model="form.workExperience" rows="4" required></textarea>
      </div>

      <div class="field">
        <label>Уровень владения иностранными языками *</label>
        <input v-model="form.languageLevel" type="text" required />
      </div>

      <div class="field">
        <label>Проф. навыки</label>
        <textarea v-model="form.skills" rows="4"></textarea>
      </div>

      <div class="field">
        <label>Личные качества</label>
        <textarea v-model="form.qualities" rows="4"></textarea>
      </div>

      <div class="field">
        <label>Адрес *</label>
        <input v-model="form.address" type="text" required />
      </div>

      <div class="field">
        <label>Телефон *</label>
        <input v-model="form.phone" type="tel" required />
      </div>

      <div class="field">
        <label>Email *</label>
        <input v-model="form.email" type="email" required />
      </div>

      <div class="field-row">
        <div class="field">
          <label>Код с рисунка *</label>
          <input v-model="form.captcha" type="text" required />
        </div>
        <div class="captcha-image">
          <span class="captcha-text">{{ captchaCode }}</span>
        </div>
      </div>

      <div class="consent-block">
        <div class="field checkbox-field">
          <label>
            <input v-model="consent.privacy" type="checkbox" required />
            Я ознакомился(-ась) с
            <RouterLink to="/privacy" target="_blank">Политикой конфиденциальности</RouterLink>
            и принимаю её условия
          </label>
        </div>
        <div class="field checkbox-field">
          <label>
            <input v-model="consent.personalData" type="checkbox" required />
            Я даю
            <RouterLink to="/consent" target="_blank">согласие на обработку персональных данных</RouterLink>
          </label>
        </div>
      </div>

      <button class="submit-btn" type="submit" :disabled="!consent.privacy || !consent.personalData">Отправить</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'

const form = ref({
  fio: '',
  birthInfo: '',
  maritalStatus: '',
  education: '',
  workExperience: '',
  languageLevel: '',
  skills: '',
  qualities: '',
  address: '',
  phone: '',
  email: '',
  captcha: '',
})

const consent = ref({ privacy: false, personalData: false })

const captchaCode = computed(() => {
  return Math.random().toString(36).substring(2, 8).toUpperCase()
})

function submit() {
  if (form.value.captcha.toUpperCase() !== captchaCode.value) {
    alert('Неверный код с рисунка!')
    return
  }
  alert('Анкета преподавателя отправлена! Мы свяжемся с вами.')
}
</script>

<style scoped>
.jobs-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.form {
  background: #ffe3cf;
  padding: 24px;
  border-radius: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 14px;
}

.field label {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.field input,
.field textarea {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 15px;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  margin-bottom: 14px;
  align-items: end;
}

.captcha-image {
  background: #f0f0f0;
  padding: 12px 24px;
  border-radius: 8px;
  border: 2px dashed #999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.captcha-text {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 4px;
  color: #555;
  font-family: 'Courier New', monospace;
  text-decoration: line-through;
  text-decoration-color: #999;
}

.consent-block {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin: 16px 0 8px;
}

.checkbox-field {
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 10px;
}

.checkbox-field input[type='checkbox'] {
  margin-right: 8px;
  margin-top: 3px;
  flex-shrink: 0;
}

.checkbox-field label {
  font-size: 14px;
  font-weight: normal;
  line-height: 1.5;
}

.checkbox-field a {
  color: var(--brand-orange);
  text-decoration: underline;
}

.submit-btn {
  width: auto;
  padding: 12px 32px;
  background: var(--brand-orange);
  color: #fff;
  border: none;
  border-radius: 999px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 16px;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #e55a10;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
