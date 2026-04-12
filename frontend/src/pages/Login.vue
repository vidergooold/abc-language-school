<template>
  <main class="login-page">
    <div class="login-card">
      <div class="login-card__icon">🔐</div>
      <h1 class="login-title">Личный кабинет</h1>

      <form @submit.prevent="submit">
        <div class="field">
          <label>Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="Введите ваш email"
            autocomplete="username"
            required
          />
        </div>

        <div class="field">
          <label>Пароль</label>
          <div class="password-wrap">
            <input
              v-model="password"
              :type="showPass ? 'text' : 'password'"
              placeholder="Введите пароль"
              autocomplete="current-password"
              required
            />
            <button type="button" class="toggle-pass" @click="showPass = !showPass">
              {{ showPass ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <p v-if="error" class="error">⚠️ {{ error }}</p>

        <button class="login-btn" type="submit" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? 'Вхожу...' : 'Войти' }}
        </button>
      </form>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const showPass = ref(false)
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
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background: linear-gradient(135deg, #f5f0ff 0%, #fff7f0 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  padding: 40px 36px;
  border-radius: 20px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.1);
  text-align: center;
}

.login-card__icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.login-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--brand-purple);
  margin-bottom: 28px;
}

.field {
  display: flex;
  flex-direction: column;
  text-align: left;
  margin-bottom: 18px;
}

.field label {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--brand-purple);
}

.field input {
  padding: 12px 14px;
  border-radius: 10px;
  border: 1.5px solid #e0d5ff;
  font-size: 15px;
  transition: border-color 0.2s;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}

.field input:focus {
  border-color: var(--brand-orange);
}

.password-wrap {
  position: relative;
}

.password-wrap input {
  padding-right: 44px;
}

.toggle-pass {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
  line-height: 1;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: var(--brand-orange);
  color: #fff;
  border: none;
  border-radius: 999px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 8px;
  transition: background 0.2s, transform 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.login-btn:hover:not(:disabled) {
  background: var(--brand-red);
  transform: translateY(-1px);
}
.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.error {
  color: var(--brand-red);
  font-size: 14px;
  text-align: left;
  margin-bottom: 8px;
  background: #fff0f0;
  padding: 10px 12px;
  border-radius: 8px;
  border-left: 3px solid var(--brand-red);
}
</style>
