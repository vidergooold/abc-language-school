<template>
  <div class="enroll-page">
    <h1 class="page-title">Стать участником</h1>
    <p class="page-subtitle">
      Заполните анкету, и мы свяжемся с вами для записи на занятия
    </p>

    <!-- Табы -->
    <div class="tabs">
      <button
        :class="['tab', { active: activeTab === 'child' }]"
        @click="activeTab = 'child'"
      >
        Анкета школьника
      </button>
      <button
        :class="['tab', { active: activeTab === 'adult' }]"
        @click="activeTab = 'adult'"
      >
        Анкета взрослого
      </button>
      <button
        :class="['tab', { active: activeTab === 'preschool' }]"
        @click="activeTab = 'preschool'"
      >
        Анкета дошкольника
      </button>
    </div>

    <!-- Форма школьника -->
    <form v-if="activeTab === 'child'" class="form" @submit.prevent="submitChild">
      <section class="form-section">
        <h2>Информация о ребенке</h2>
        <div class="field">
          <label>ФИО *</label>
          <input v-model="childForm.fio" type="text" required />
        </div>
        <div class="field-row">
          <div class="field">
            <label>Возраст *</label>
            <input v-model="childForm.age" type="number" required />
          </div>
          <div class="field">
            <label>Дата рождения</label>
            <input v-model="childForm.birthdate" type="date" />
          </div>
        </div>
        <div class="field">
          <label>Школа *</label>
          <input v-model="childForm.school" type="text" required />
        </div>
        <div class="field-row">
          <div class="field">
            <label>Класс *</label>
            <input v-model="childForm.grade" type="text" required />
          </div>
          <div class="field">
            <label>Смена</label>
            <select v-model="childForm.shift">
              <option value="first">первая (утро)</option>
              <option value="second">вторая (день)</option>
            </select>
          </div>
          <div class="field checkbox-field">
            <label>
              <input v-model="childForm.extended" type="checkbox" />
              Продленка
            </label>
          </div>
        </div>
      </section>

      <section class="form-section">
        <h2>Информация о родителях</h2>
        <div class="field">
          <label>ФИО *</label>
          <input v-model="childForm.parentFio" type="text" required />
        </div>
        <div class="field">
          <label>Место работы</label>
          <textarea v-model="childForm.parentWork" rows="2"></textarea>
        </div>
      </section>

      <section class="form-section">
        <h2>Контактные данные</h2>
        <div class="field">
          <label>Телефон *</label>
          <input v-model="childForm.phone" type="tel" required />
        </div>
        <div class="field">
          <label>Адрес *</label>
          <input v-model="childForm.address" type="text" required />
        </div>
        <div class="field">
          <label>Email</label>
          <input v-model="childForm.email" type="email" />
        </div>
      </section>

      <section class="form-section">
        <h2>Дополнительная информация</h2>
        <div class="field">
          <label>Изучали язык раньше?</label>
          <input v-model="childForm.studiedBefore" type="text" />
        </div>
        <div class="field">
          <label>Где и как долго?</label>
          <textarea v-model="childForm.whereHow" rows="3"></textarea>
        </div>
        <div class="field">
          <label>Заметки, пожелания</label>
          <textarea v-model="childForm.notes" rows="3"></textarea>
        </div>
      </section>

      <button class="submit-btn" type="submit">Отправить</button>
    </form>

    <!-- Форма взрослого -->
    <form v-if="activeTab === 'adult'" class="form" @submit.prevent="submitAdult">
      <section class="form-section">
        <h2>Общая информация</h2>
        <div class="field">
          <label>ФИО *</label>
          <input v-model="adultForm.fio" type="text" required />
        </div>
        <div class="field-row">
          <div class="field">
            <label>Возраст *</label>
            <input v-model="adultForm.age" type="number" required />
          </div>
          <div class="field">
            <label>Дата рождения</label>
            <input v-model="adultForm.birthdate" type="date" />
          </div>
        </div>
        <div class="field">
          <label>Место работы</label>
          <textarea v-model="adultForm.work" rows="2"></textarea>
        </div>
      </section>

      <section class="form-section">
        <h2>Контактные данные</h2>
        <div class="field">
          <label>Телефон *</label>
          <input v-model="adultForm.phone" type="tel" required />
        </div>
        <div class="field">
          <label>Адрес *</label>
          <input v-model="adultForm.address" type="text" required />
        </div>
        <div class="field">
          <label>Email</label>
          <input v-model="adultForm.email" type="email" />
        </div>
      </section>

      <section class="form-section">
        <h2>Дополнительная информация</h2>
        <div class="field">
          <label>Изучали язык раньше?</label>
          <input v-model="adultForm.studiedBefore" type="text" />
        </div>
        <div class="field">
          <label>Где и как долго?</label>
          <textarea v-model="adultForm.whereHow" rows="3"></textarea>
        </div>
        <div class="field">
          <label>Заметки, пожелания</label>
          <textarea v-model="adultForm.notes" rows="3"></textarea>
        </div>
      </section>

      <button class="submit-btn" type="submit">Отправить</button>
    </form>

    <!-- Форма дошкольника -->
    <form v-if="activeTab === 'preschool'" class="form" @submit.prevent="submitPreschool">
      <section class="form-section">
        <h2>Информация о ребенке</h2>
        <div class="field">
          <label>ФИО *</label>
          <input v-model="preschoolForm.fio" type="text" required />
        </div>
        <div class="field-row">
          <div class="field">
            <label>Возраст *</label>
            <input v-model="preschoolForm.age" type="number" required />
          </div>
          <div class="field">
            <label>Дата рождения</label>
            <input v-model="preschoolForm.birthdate" type="date" />
          </div>
        </div>
        <div class="field">
          <label>Дет. сад *</label>
          <input v-model="preschoolForm.kindergarten" type="text" required />
        </div>
        <div class="field">
          <label>Группа *</label>
          <input v-model="preschoolForm.group" type="text" required />
        </div>
      </section>

      <section class="form-section">
        <h2>Информация о родителях</h2>
        <div class="field">
          <label>ФИО *</label>
          <input v-model="preschoolForm.parentFio" type="text" required />
        </div>
        <div class="field">
          <label>Место работы</label>
          <textarea v-model="preschoolForm.parentWork" rows="2"></textarea>
        </div>
      </section>

      <section class="form-section">
        <h2>Контактные данные</h2>
        <div class="field">
          <label>Телефон (дом./моб.) *</label>
          <input v-model="preschoolForm.phone" type="tel" required />
        </div>
        <div class="field">
          <label>Адрес *</label>
          <input v-model="preschoolForm.address" type="text" required />
        </div>
        <div class="field">
          <label>Email</label>
          <input v-model="preschoolForm.email" type="email" />
        </div>
      </section>

      <section class="form-section">
        <h2>Дополнительная информация</h2>
        <div class="field">
          <label>Во сколько обычно забираете ребенка из д/сада?</label>
          <input v-model="preschoolForm.pickupTime" type="text" />
        </div>
        <div class="field">
          <label>
            Заметки, пожелания (особенности Вашего ребенка, которые педагогу
            необходимо учесть)
          </label>
          <textarea v-model="preschoolForm.notes" rows="3"></textarea>
        </div>
      </section>

      <button class="submit-btn" type="submit">Отправить</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('child')

const childForm = ref({
  fio: '',
  age: '',
  birthdate: '',
  school: '',
  grade: '',
  shift: 'first',
  extended: false,
  parentFio: '',
  parentWork: '',
  phone: '',
  address: '',
  email: '',
  studiedBefore: '',
  whereHow: '',
  notes: '',
})

const adultForm = ref({
  fio: '',
  age: '',
  birthdate: '',
  work: '',
  phone: '',
  address: '',
  email: '',
  studiedBefore: '',
  whereHow: '',
  notes: '',
})

const preschoolForm = ref({
  fio: '',
  age: '',
  birthdate: '',
  kindergarten: '',
  group: '',
  parentFio: '',
  parentWork: '',
  phone: '',
  address: '',
  email: '',
  pickupTime: '',
  notes: '',
})

function submitChild() {
  alert('Анкета школьника отправлена!')
  console.log('Данные школьника:', childForm.value)
}

function submitAdult() {
  alert('Анкета взрослого отправлена!')
  console.log('Данные взрослого:', adultForm.value)
}

function submitPreschool() {
  alert('Анкета дошкольника отправлена!')
  console.log('Данные дошкольника:', preschoolForm.value)
}
</script>

<style scoped>
.enroll-page {
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
  border-bottom
