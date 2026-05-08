<template>
  <div class="profile-page">
    <h1>👤 Профиль</h1>

    <div v-if="loading" class="skeleton-list">
      <div class="skeleton-field" v-for="n in 4" :key="n"></div>
    </div>

    <div v-else class="profile-wrap">
      <!-- Аватар -->
      <div class="avatar-block">
        <div class="avatar">
          {{ initials }}
        </div>
        <div class="avatar-info">
          <div class="avatar-name">{{ auth.user?.full_name || auth.user?.email }}</div>
          <span class="role-badge" :class="'role-' + auth.user?.role">
            {{ roleLabel }}
          </span>
        </div>
      </div>

      <div v-if="auth.user?.role === 'admin'" class="admin-note">
        <strong>Важно:</strong> при регистрации сотрудника его аккаунт создаётся со статусом «ученик». Администратор вручную назначит роль после проверки.
      </div>

      <!-- Форма -->
      <div class="profile-form">
        <div class="form-section">
          <h2>Личные данные</h2>
          <div class="form-grid">
            <div class="field">
              <label>Полное имя</label>
              <input v-model="form.full_name" placeholder="Иванов Иван Иванович" :disabled="saving" />
            </div>
            <div class="field">
              <label>Email</label>
              <input :value="auth.user?.email" disabled placeholder="email@example.com" />
              <span class="field-hint">Email изменить нельзя — это ваш логин</span>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h2>Смена пароля</h2>
          <div class="form-grid">
            <div class="field">
              <label>Новый пароль</label>
              <input v-model="form.new_password" type="password" placeholder="Минимум 8 символов" :disabled="saving" />
            </div>
            <div class="field">
              <label>Повторите пароль</label>
              <input v-model="form.confirm_password" type="password" placeholder="Повторите пароль" :disabled="saving" />
              <span v-if="passwordMismatch" class="field-error">Пароли не совпадают</span>
            </div>
          </div>
        </div>

        <div v-if="successMsg" class="alert-success">✅ {{ successMsg }}</div>
        <div v-if="errorMsg" class="alert-error">❌ {{ errorMsg }}</div>

        <div class="form-actions">
          <button class="btn-save" :disabled="saving || passwordMismatch" @click="save">
            {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import http from '@/api/http'

const auth = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const form = ref({
  full_name: '',
  new_password: '',
  confirm_password: '',
})

const initials = computed(() => {
  const name = auth.user?.full_name || auth.user?.email || '?'
  return name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
})

const roleLabel = computed(() => {
  const r = auth.user?.role
  return r ? { admin: '🔑 Администратор', teacher: '👨‍🏫 Учитель', student: '🎓 Студент' }[r] ?? r : '—'
})

const passwordMismatch = computed(() =>
  !!form.value.confirm_password && form.value.new_password !== form.value.confirm_password
)

onMounted(() => {
  form.value.full_name = auth.user?.full_name || ''
})

async function save() {
  if (passwordMismatch.value) return
  saving.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    const payload: any = { full_name: form.value.full_name }
    if (form.value.new_password) {
      payload.password = form.value.new_password
    }
    await http.patch('/users/me', payload)
    auth.user!.full_name = form.value.full_name
    form.value.new_password = ''
    form.value.confirm_password = ''
    successMsg.value = 'Данные успешно обновлены!'
    setTimeout(() => successMsg.value = '', 4000)
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || 'Ошибка при сохранении'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.profile-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 28px; }

/* Skeleton */
.skeleton-list { display: flex; flex-direction: column; gap: 14px; }
.skeleton-field { height: 52px; border-radius: 10px; background: linear-gradient(90deg,#fff0e8 25%,#ffe8d6 50%,#fff0e8 75%); background-size: 200% 100%; animation: shimmer 1.5s ease-in-out infinite; }
@keyframes shimmer { 0%{background-position:-200% 0}100%{background-position:200% 0} }

.profile-wrap { display: flex; flex-direction: column; gap: 28px; max-width: 700px; }

/* Avatar */
.avatar-block { display: flex; align-items: center; gap: 20px; background: #fff7f0; border-radius: 16px; padding: 20px; border: 2px solid #ffe3cf; }
.avatar { width: 64px; height: 64px; border-radius: 50%; background: var(--brand-orange); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; flex-shrink: 0; }
.avatar-info { display: flex; flex-direction: column; gap: 6px; }
.avatar-name { font-size: 18px; font-weight: 700; color: var(--brand-purple); }
.role-badge { display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: 13px; font-weight: 700; }
.role-admin   { background: #ffeaea; color: var(--brand-red, #d63031); }
.role-teacher { background: #ffe3cf; color: var(--brand-orange); }
.role-student { background: #e8f4ff; color: #2a7bbf; }

/* Form */
.profile-form { background: #fff; border-radius: 16px; padding: 24px; border: 2px solid #ffe3cf; }
.form-section { margin-bottom: 24px; }
.form-section:last-of-type { margin-bottom: 0; }
.form-section h2 { font-size: 16px; font-weight: 700; color: var(--brand-purple); margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid #ffe3cf; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 13px; font-weight: 600; color: #555; }
.field input { padding: 10px 14px; border-radius: 10px; border: 1.5px solid #e0d5ff; font-size: 15px; outline: none; transition: border-color 0.2s; }
.field input:focus { border-color: var(--brand-orange); }
.field input:disabled { background: #f5f5f5; color: #aaa; cursor: not-allowed; }
.field-hint { font-size: 12px; color: #aaa; }
.field-error { font-size: 12px; color: #e03c3c; font-weight: 600; }

.alert-success { background: #e6f9ef; color: #22a55b; padding: 12px 16px; border-radius: 10px; font-weight: 600; font-size: 14px; margin-top: 16px; }
.alert-error   { background: #fdeaea; color: #e03c3c; padding: 12px 16px; border-radius: 10px; font-weight: 600; font-size: 14px; margin-top: 16px; }

.admin-note {
  background: #fff4db;
  border: 1px solid #ffe3af;
  color: #5f3e0b;
  border-radius: 14px;
  padding: 16px 18px;
  margin-top: 16px;
  line-height: 1.6;
}

.form-actions { margin-top: 20px; }
.btn-save { background: var(--brand-orange); color: #fff; border: none; padding: 12px 28px; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
.btn-save:hover:not(:disabled) { background: var(--brand-red, #d63031); }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
