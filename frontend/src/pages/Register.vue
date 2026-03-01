<template>
  <main class="auth-page">
    <form class="auth-form" @submit.prevent="submit">
      <h1 class="auth-title">Регистрация</h1>

      <div class="field">
        <label>Email</label>
        <input v-model="email" type="email" required />
      </div>

      <div class="field">
        <label>Пароль</label>
        <input v-model="password" type="password" required />
      </div>

      <button class="auth-btn" type="submit">
        Зарегистрироваться
      </button>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">Регистрация выполнена, теперь войдите.</p>
    </form>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import http from '@/api/http'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const success = ref(false)
const router = useRouter()

async function submit() {
  error.value = null
  success.value = false
  try {
    await http.post('/auth/register', { email: email.value, password: password.value })
    success.value = true
    setTimeout(() => router.push('/login'), 1000)
  } catch {
    error.value = 'Не удалось зарегистрировать пользователя'
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.auth-form {
  width: 100%;
  max-width: 380px;
  background: var(--bg-white);
  padding: 24px;
  border-radius: var(--border-radius);
}

.auth-title {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.field label {
  font-size: 15px;
  margin-bottom: 4px;
}

.field input {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 15px;
}

.auth-btn {
  width: 100%;
  padding: 12px;
  background: var(--brand-orange);
  color: #fff;
  border: none;
  border-radius: var(--border-radius);
  font-size: 16px;
  cursor: pointer;
}

.error {
  margin-top: 12px;
  color: var(--brand-red);
  font-size: 14px;
  text-align: center;
}

.success {
  margin-top: 12px;
  color: green;
  font-size: 14px;
  text-align: center;
}
</style>
