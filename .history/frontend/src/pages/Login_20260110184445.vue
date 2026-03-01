<template>
  <main class="login-page">
    <form class="login-form" @submit.prevent="submit">
      <h1 class="login-title">Вход в личный кабинет</h1>

      <div class="field">
        <label>Email</label>
        <input
          v-model="email"
          type="email"
          placeholder="student@example.com"
          required
        />
      </div>

      <div class="field">
        <label>Пароль</label>
        <input
          v-model="password"
          type="password"
          placeholder="Введите пароль"
          required
        />
      </div>

      <button class="login-btn" type="submit">
        Войти
      </button>

      <p v-if="error" class="error">
        {{ error }}
      </p>
    </form>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')

const error = ref<string | null>(null)

const authStore = useAuthStore()
const router = useRouter()

async function submit() {
  error.value = null

  try {
    await authStore.login(email.value, password.value)
    router.push('/account')
  } catch (e) {
    error.value = 'Неверный email или пароль'
  }
}
</script>

<style scoped>
.login-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.login-form {
  width: 100%;
  max-width: 360px;
  background: var(--bg-white);
  padding: 24px;
  border-radius: var(--border-radius);
}

.login-title {
  font-size: 22px;
  margin-bottom: 20px;
  text-align: center;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.field label {
  font-size: 1px;
  margin-bottom: 4px;
}

.field input {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 14px;
}

.login-btn {
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
</style>
