<template>
  <div class="clients-section">
    <h2 class="section-title">Оформление налогового вычета</h2>

    <h3 class="notice-title">Уважаемые родители!</h3>
    <p>
      Для оформления налогового вычета и получения от нас справки об оплате Вам
      необходимо оставить заявку (форма заявки ниже)
      <strong
        >не менее чем за 30 календарных дней до подачи документов в Налоговый
        Орган</strong
      >.
    </p>

    <p>
      <strong>Обращаем особое внимание</strong> на то, что в летние и зимние
      каникулы мы не работаем, соответственно
      <strong>справки не выпускаются</strong>.
    </p>

    <p>
      В период <strong>с 25 мая по 15 октября</strong>, справки не выпускаются, в
      связи с занятостью сотрудников при окончании/запуске учебного года.
    </p>

    <p>
      <strong>С 15 октября</strong> справки выпускаются по мере возможности
      <strong>(до 30 календарных дней ожидания)</strong>.
    </p>

    <h3>Заявка на получение справки</h3>
    <form class="tax-form" @submit.prevent="submitTaxForm">
      <h4>Данные плательщика</h4>
      <div class="field">
        <label>ФИО *</label>
        <input v-model="form.payerFio" type="text" required />
      </div>
      <div class="field">
        <label>ИНН *</label>
        <input v-model="form.payerInn" type="text" required />
      </div>
      <div class="field">
        <label>Дата рождения *</label>
        <input v-model="form.payerBirthdate" type="date" required />
      </div>
      <div class="field-row">
        <div class="field">
          <label>Серия паспорта *</label>
          <input v-model="form.payerPassportSeries" type="text" required />
        </div>
        <div class="field">
          <label>Номер паспорта *</label>
          <input v-model="form.payerPassportNumber" type="text" required />
        </div>
      </div>
      <div class="field">
        <label>Дата выдачи паспорта *</label>
        <input v-model="form.payerPassportDate" type="date" required />
      </div>
      <div class="field">
        <label>Код подразделения *</label>
        <input v-model="form.payerDepartmentCode" type="text" required />
      </div>
      <div class="field">
        <label>Контактный телефон *</label>
        <input v-model="form.payerPhone" type="tel" required />
      </div>

      <h4>Данные обучающегося</h4>
      <div class="field">
        <label>ФИО *</label>
        <input v-model="form.studentFio" type="text" required />
      </div>
      <div class="field">
        <label>ИНН (при наличии)</label>
        <input v-model="form.studentInn" type="text" />
      </div>
      <div class="field">
        <label>Дата рождения *</label>
        <input v-model="form.studentBirthdate" type="date" required />
      </div>
      <div class="field">
        <label>Документ *</label>
        <select v-model="form.studentDocType" required>
          <option value="">-- Выберите --</option>
          <option value="passport">Паспорт</option>
          <option value="birth_cert">Свидетельство о рождении</option>
        </select>
      </div>
      <div class="field-row">
        <div class="field">
          <label>Серия документа *</label>
          <input v-model="form.studentDocSeries" type="text" required />
        </div>
        <div class="field">
          <label>Номер документа *</label>
          <input v-model="form.studentDocNumber" type="text" required />
        </div>
      </div>
      <div class="field">
        <label>Дата выдачи документа *</label>
        <input v-model="form.studentDocDate" type="date" required />
      </div>

      <h4>Период и стоимость обучения</h4>
      <div class="field-row">
        <div class="field">
          <label>Периоды обучения</label>
          <select v-model="form.period">
            <option value="2023-2024">2023 - 2024</option>
            <option value="2024-2025">2024 - 2025</option>
            <option value="2025-2026">2025 - 2026</option>
          </select>
        </div>
        <div class="field">
          <label>Стоимость</label>
          <input v-model="form.cost" type="text" />
        </div>
      </div>

      <div class="field checkbox-group">
        <label>У меня есть договоры на указанные периоды обучения</label>
        <div>
          <label>
            <input v-model="form.hasContracts" type="radio" value="yes" />
            Да
          </label>
          <label>
            <input v-model="form.hasContracts" type="radio" value="no" />
            Нет
          </label>
        </div>
      </div>

      <div class="field">
        <label>Прикрепить квитанции/чеки</label>
        <input type="file" accept=".png,.jpg,.jpeg,.pdf" multiple />
      </div>

      <h4>Получение справки</h4>
      <div class="field">
        <label>Получить справку *</label>
        <select v-model="form.deliveryMethod" required>
          <option value="">-- Выберите --</option>
          <option value="email">На адрес электронной почты</option>
          <option value="person">Лично</option>
        </select>
      </div>

      <div class="field checkbox-field">
        <label>
          <input v-model="form.consent1" type="checkbox" required />
          Подписывая настоящее заявление, я даю согласие на обработку
          персональных данных третьих лиц
        </label>
      </div>

      <div class="field checkbox-field">
        <label>
          <input v-model="form.consent2" type="checkbox" required />
          Достоверность сведений, указанных в настоящем заявлении подтверждаю
        </label>
      </div>

      <button class="submit-btn" type="submit">Отправить</button>
      <p class="note">* - обязательное для заполнения поле</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const form = ref({
  payerFio: '',
  payerInn: '',
  payerBirthdate: '',
  payerPassportSeries: '',
  payerPassportNumber: '',
  payerPassportDate: '',
  payerDepartmentCode: '',
  payerPhone: '',
  studentFio: '',
  studentInn: '',
  studentBirthdate: '',
  studentDocType: '',
  studentDocSeries: '',
  studentDocNumber: '',
  studentDocDate: '',
  period: '2025-2026',
  cost: '',
  hasContracts: 'yes',
  deliveryMethod: '',
  consent1: false,
  consent2: false,
})

function submitTaxForm() {
  alert('Заявка на получение справки отправлена!')
  console.log('Данные:', form.value)
}
</script>

<style scoped>
.clients-section {
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

h4 {
  font-size: 18px;
  font-weight: 700;
  margin-top: 20px;
  margin-bottom: 10px;
  color: var(--brand-orange);
}

