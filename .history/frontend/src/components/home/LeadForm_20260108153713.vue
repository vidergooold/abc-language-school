<template>
  <form class="lead-form" @submit.prevent="submit">
    <h3 class="lead-form__title">Записаться на пробный урок</h3>

    <div class="field">
      <label>Имя</label>
      <input v-model="name" type="text" placeholder="Ваше имя" />
      <span v-if="errors.name" class="error">{{ errors.name }}</span>
    </div>

    <div class="field">
      <label>Телефон</label>
      <input v-model="phone" type="tel" placeholder="+7 (___) ___-__-__" />
      <span v-if="errors.phone" class="error">{{ errors.phone }}</span>
    </div>

    <div class="field">
      <label>Комментарий</label>
      <textarea
        v-model="comment"
        placeholder="Возраст, уровень, удобное время"
      />
    </div>

    <BaseButton type="submit">
      {{ loading ? 'Отправка...' : 'Отправить заявку' }}
    </BaseButton>

    <p v-if="success" class="success">
      Заявка успешно отправлена!
    </p>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const name = ref('')
const phone = ref('')
const comment = ref('')

const errors = ref<{ name?: string; phone?: string }>({})

function validate() {
  errors.value = {}

  if (!name.value) {
    errors.value.name = 'Введите имя'
  }

  if (!phone.value) {
    errors.value.phone = 'Введите телефон'
  }

  return Object.keys(errors.value).length === 0
}

function submit() {
  if (!validate()) return

  loading.value = true

  // имитация отправки (потом заменим на API)
  setTimeout(() => {
    loading.value = false
    success.value = true

    name.value = ''
    phone.value = ''
    comment.value = ''
  }, 1000)
}
</script>

<style scoped>
.lead-form {
  background: var(--bg-white);
  padding: 24px;
  border-radius: var(--border-radius);
  max-width: 420px;
  margin: 0 auto;
}

.lead-form__title {
  font-size: 20px;
  margin-bottom: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.field label {
  font-size: 14px;
  margin-bottom: 4px;
}

.field input,
.field textarea {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
}

.error {
  color: var(--brand-red);
  font-size: 12px;
  margin-top: 4px;
}

.success {
  margin-top: 16px;
  color: green;
}
</style>
