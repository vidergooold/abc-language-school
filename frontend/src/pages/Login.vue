<template>
  <main class="login-page">
    <form class="login-form" @submit.prevent="submit">
      <h1 class="login-title">Вход для сотрудников</h1>
      <p class="login-notice">Личный кабинет доступен только для администраторов и преподавателей. Если вы являетесь сотрудником школы и у вас нет аккаунта, обратитесь к администратору.</p>

      <div class="field">
        <label>Email</label>
        <input
          v-model="email"
          type="email"
          placeholder="staff@abc-school.ru"
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

      <button class="login-btn" type="submit" :disabled="loading">
        {{ loading ? 'Вход...' : 'Войти' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
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
const loading = ref(false)

const authStore = useAuthStore()
const router = useRouter()

async function submit() {
  error.value = null
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/account')
  } catch {
    error.value = 'Неверный email или пароль'
  } finally {
    loading.value = false
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
  max-width: 400px;
  background: var(--bg-white);
  padding: 32px;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.login-title {
  font-size: 24px;
  margin-bottom: 8px;
  text-align: center;
  color: var(--brand-purple);
}

.login-notice {
  font-size: 13px;
  color: #888;
  text-align: center;
  margin-bottom: 20px;
  line-height: 1.5;
}

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.field label {
  font-size: 15px;
  margin-bottom: 4px;
  font-weight: 500;
}

.field input {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 15px;
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
  font-weight: 600;
  transition: background 0.2s;
}
.login-btn:hover { background: var(--brand-red); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.error {
  margin-top: 12px;
  color: var(--brand-red);
  font-size: 14px;
  text-align: center;
}
</style>
