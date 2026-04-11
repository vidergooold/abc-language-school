<template>
  <main class="auth-page">
    <form class="auth-form" @submit.prevent="submit">
      <h1 class="auth-title">Регистрация</h1>

      <!-- Выбор роли -->
      <div class="role-selector">
        <button
          type="button"
          :class="['role-btn', role === 'student' ? 'active' : '']"
          @click="role = 'student'"
        >
          <span class="role-icon">🎓</span>
          <span class="role-label">Ученик / Родитель</span>
          <span class="role-desc">Запись на курсы, расписание, успехи</span>
        </button>
        <button
          type="button"
          :class="['role-btn', role === 'staff' ? 'active' : '']"
          @click="role = 'staff'"
        >
          <span class="role-icon">👩‍🏫</span>
          <span class="role-label">Сотрудник</span>
          <span class="role-desc">Управление расписанием и группами</span>
        </button>
      </div>

      <div class="field">
        <label>Имя и фамилия</label>
        <input v-model="fullName" type="text" placeholder="Иванова Мария" required />
      </div>

      <div class="field">
        <label>Email</label>
        <input v-model="email" type="email" placeholder="example@mail.ru" required />
      </div>

      <div class="field">
        <label>Пароль</label>
        <input v-model="password" type="password" placeholder="Минимум 6 символов" required />
      </div>

      <!-- Поле для сотрудника -->
      <div v-if="role === 'staff'" class="staff-note">
        <span>🔒</span>
        <span>Аккаунт сотрудника будет создан со статусом «ученик». Администратор вручную назначит роль после проверки.</span>
      </div>

      <button class="auth-btn" type="submit" :disabled="loading">
        {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">✅ Регистрация выполнена! Перенаправляем на вход...</p>

      <p class="login-link">
        Уже есть аккаунт? <router-link to="/login">Войти</router-link>
      </p>
    </form>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import http from '@/api/http'
import { useRouter } from 'vue-router'

const role = ref<'student' | 'staff'>('student')
const fullName = ref('')
const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const success = ref(false)
const loading = ref(false)
const router = useRouter()

async function submit() {
  error.value = null
  success.value = false

  if (password.value.length < 6) {
    error.value = 'Пароль должен содержать не менее 6 символов'
    return
  }

  loading.value = true
  try {
    await http.post('/auth/register', {
      email: email.value,
      full_name: fullName.value,
      password: password.value,
    })
    success.value = true
    setTimeout(() => router.push('/login'), 1500)
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    error.value = typeof detail === 'string' ? detail : 'Не удалось зарегистрировать пользователя'
  } finally {
    loading.value = false
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
  max-width: 420px;
  background: var(--bg-white, #fff);
  padding: 32px 28px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
.auth-title {
  font-size: 26px;
  margin-bottom: 24px;
  text-align: center;
  font-weight: 700;
}

/* Role selector */
.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 24px;
}
.role-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 10px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.18s ease;
  text-align: center;
}
.role-btn:hover {
  border-color: var(--brand-orange, #f7691e);
  background: #fff7f0;
}
.role-btn.active {
  border-color: var(--brand-orange, #f7691e);
  background: #fff7f0;
  box-shadow: 0 0 0 3px rgba(247,105,30,0.15);
}
.role-icon { font-size: 28px; line-height: 1; }
.role-label { font-size: 14px; font-weight: 700; color: #333; }
.role-desc { font-size: 11px; color: #888; line-height: 1.3; }

.field {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}
.field label {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 5px;
  color: #444;
}
.field input {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 15px;
  transition: border-color 0.15s;
}
.field input:focus {
  outline: none;
  border-color: var(--brand-orange, #f7691e);
}

.staff-note {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13px;
  color: #7a5c00;
  margin-bottom: 16px;
  line-height: 1.4;
}

.auth-btn {
  width: 100%;
  padding: 13px;
  background: var(--brand-orange, #f7691e);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  margin-top: 4px;
}
.auth-btn:hover:not(:disabled) { background: #e55a10; }
.auth-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.error {
  margin-top: 12px;
  color: #c33;
  font-size: 14px;
  text-align: center;
  font-weight: 600;
}
.success {
  margin-top: 12px;
  color: #1a7a3f;
  font-size: 14px;
  text-align: center;
  font-weight: 600;
}
.login-link {
  text-align: center;
  margin-top: 18px;
  font-size: 14px;
  color: #666;
}
.login-link a {
  color: var(--brand-orange, #f7691e);
  font-weight: 600;
  text-decoration: none;
}
.login-link a:hover { text-decoration: underline; }
</style>
