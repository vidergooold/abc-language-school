<template>
  <div class="testing-page">
    <h1 class="page-title">Пройти тестирование</h1>
    <p class="page-subtitle">
      Определите свой уровень английского языка — это бесплатно
    </p>

    <!-- Табы -->
    <div class="tabs">
      <button
        :class="['tab', { active: activeTab === 'elementary' }]"
        @click="activeTab = 'elementary'"
      >
        Тест для 1–5 кл.
      </button>
      <button
        :class="['tab', { active: activeTab === 'middle' }]"
        @click="activeTab = 'middle'"
      >
        Тест для 6–8 кл.
      </button>
      <button
        :class="['tab', { active: activeTab === 'senior' }]"
        @click="activeTab = 'senior'"
      >
        Тест для 9–11 кл., взрослых групп
      </button>
    </div>

    <!-- Форма для 1-5 классов -->
    <form
      v-if="activeTab === 'elementary'"
      class="form"
      @submit.prevent="submitTest('elementary')"
    >
      <h2 class="form-title">Тест для 1–5 кл.</h2>
      <p class="form-description">Введите, пожалуйста, свои данные</p>

      <div class="field">
        <label>ФИО *</label>
        <input v-model="elementaryForm.fio" type="text" required />
      </div>

      <div class="field-row">
        <div class="field">
          <label>Возраст *</label>
          <input v-model="elementaryForm.age" type="number" required />
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label>Школа *</label>
          <input v-model="elementaryForm.school" type="text" required />
        </div>
        <div class="field">
          <label>Класс *</label>
          <input v-model="elementaryForm.grade" type="text" required />
        </div>
      </div>

      <div class="field">
        <label>Телефон *</label>
        <input v-model="elementaryForm.phone" type="tel" required />
      </div>

      <button class="submit-btn" type="submit">Отправить</button>
      <p class="note">* - обязательное для заполнения поле</p>
    </form>

    <!-- Форма для 6-8 классов -->
    <form
      v-if="activeTab === 'middle'"
      class="form"
      @submit.prevent="submitTest('middle')"
    >
      <h2 class="form-title">Тест для 6–8 кл.</h2>
      <p class="form-description">Введите, пожалуйста, свои данные</p>

      <div class="field">
        <label>ФИО *</label>
        <input v-model="middleForm.fio" type="text" required />
      </div>

      <div class="field-row">
        <div class="field">
          <label>Возраст *</label>
          <input v-model="middleForm.age" type="number" required />
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label>Школа *</label>
          <input v-model="middleForm.school" type="text" required />
        </div>
        <div class="field">
          <label>Класс *</label>
          <input v-model="middleForm.grade" type="text" required />
        </div>
      </div>

      <div class="field">
        <label>Телефон *</label>
        <input v-model="middleForm.phone" type="tel" required />
      </div>

      <button class="submit-btn" type="submit">Отправить</button>
      <p class="note">* - обязательное для заполнения поле</p>
    </form>

    <!-- Форма для 9-11 классов, взрослых -->
    <form
      v-if="activeTab === 'senior'"
      class="form"
      @submit.prevent="submitTest('senior')"
    >
      <h2 class="form-title">Тест для 9–11 кл., взрослых групп</h2>
      <p class="form-description">Введите, пожалуйста, свои данные</p>

      <div class="field">
        <label>ФИО *</label>
        <input v-model="seniorForm.fio" type="text" required />
      </div>

      <div class="field-row">
        <div class="field">
          <label>Возраст *</label>
          <input v-model="seniorForm.age" type="number" required />
        </div>
      </div>

      <div class="field-row">
        <div class="field">
          <label>Школа *</label>
          <input v-model="seniorForm.school" type="text" required />
        </div>
        <div class="field">
          <label>Класс *</label>
          <input v-model="seniorForm.grade" type="text" required />
        </div>
      </div>

      <div class="field">
        <label>Телефон *</label>
        <input v-model="seniorForm.phone" type="tel" required />
      </div>

      <button class="submit-btn" type="submit">Отправить</button>
      <p class="note">* - обязательное для заполнения поле</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import http from '@/api/http'

const activeTab = ref('elementary')

const elementaryForm = ref({
  fio: '',
  age: '',
  school: '',
  grade: '',
  phone: '',
})

const middleForm = ref({
  fio: '',
  age: '',
  school: '',
  grade: '',
  phone: '',
})

const seniorForm = ref({
  fio: '',
  age: '',
  school: '',
  grade: '',
  phone: '',
})

async function submitTest(level: string) {
  const formData =
    level === 'elementary'
      ? elementaryForm.value
      : level === 'middle'
      ? middleForm.value
      : seniorForm.value

  try {
    await http.post('/forms/testing', {
      ...formData,
      testLevel: level,
    })
    alert(`Заявка на тестирование успешно отправлена! Мы свяжемся с вами.`)
    
    // Очищаем форму
    Object.keys(formData).forEach(key => {
      formData[key] = ''
    })
  } catch (error) {
    alert('Ошибка отправки заявки. Попробуйте позже.')
    console.error(error)
  }
}
</script>


<style scoped>
.testing-page {
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

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #ddd;
}

.tab {
  padding: 12px 20px;
  border: none;
  background: transparent;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab.active {
  color: var(--brand-orange);
  border-bottom-color: var(--brand-orange);
}

.form {
  background: #ffe3cf;
  padding: 24px;
  border-radius: 20px;
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--brand-orange);
  margin-bottom: 8px;
}

.form-description {
  font-size: 16px;
  margin-bottom: 20px;
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

.field input {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 15px;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 14px;
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
}

.submit-btn:hover {
  background: #e55a10;
}

.note {
  margin-top: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}
</style>
