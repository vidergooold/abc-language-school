<template>
  <div class="profile">
    <h1>👤 Профиль</h1>

    <!-- Инфо-карточка -->
    <div class="profile-card">
      <div class="profile-avatar">{{ avatarLetter }}</div>
      <div class="profile-info">
        <div class="profile-name">{{ auth.user?.full_name || 'Имя не указано' }}</div>
        <div class="profile-email">{{ auth.user?.email }}</div>
        <div class="profile-role-badge" :class="roleClass">{{ roleLabel }}</div>
      </div>
    </div>

    <!-- Форма редактирования -->
    <div class="profile-section">
      <h2>Изменить данные</h2>
      <form @submit.prevent="saveProfile" class="profile-form">
        <div class="form-group">
          <label>Имя и фамилия</label>
          <input v-model="form.full_name" type="text" placeholder="Введите имя" />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input :value="auth.user?.email" type="email" disabled class="input-disabled" />
          <span class="hint">Для смены email обратитесь к администратору</span>
        </div>
        <div v-if="profileSuccess" class="alert-success">✔ Имя успешно обновлено</div>
        <div v-if="profileError" class="alert-error">{{ profileError }}</div>
        <button type="submit" class="btn-save" :disabled="profileLoading">
          {{ profileLoading ? 'Сохранение…' : 'Сохранить изменения' }}
        </button>
      </form>
    </div>

    <!-- Смена пароля -->
    <div class="profile-section">
      <h2>Сменить пароль</h2>
      <form @submit.prevent="savePassword" class="profile-form">
        <div class="form-group">
          <label>Текущий пароль</label>
          <input v-model="pwForm.current_password" type="password" placeholder="••••••••" />
        </div>
        <div class="form-group">
          <label>Новый пароль</label>
          <input v-model="pwForm.new_password" type="password" placeholder="Не менее 8 символов" />
        </div>
        <div class="form-group">
          <label>Повторите новый пароль</label>
          <input v-model="pwForm.confirm_password" type="password" placeholder="Повторите пароль" />
        </div>
        <div v-if="pwSuccess" class="alert-success">✔ Пароль успешно изменён</div>
        <div v-if="pwError" class="alert-error">{{ pwError }}</div>
        <button type="submit" class="btn-save" :disabled="pwLoading">
          {{ pwLoading ? 'Сохранение…' : 'Изменить пароль' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import http from '@/api/http'

const auth = useAuthStore()

const avatarLetter = computed(() => {
  const name = auth.user?.full_name || auth.user?.email || '?'
  return name.charAt(0).toUpperCase()
})

const role = computed(() => auth.user?.role)
const roleLabel = computed(() => {
  if (role.value === 'admin') return '🔑 Администратор'
  if (role.value === 'teacher') return '👨‍🏫 Учитель'
  return '🎓 Студент'
})
const roleClass = computed(() => {
  if (role.value === 'admin') return 'role-admin'
  if (role.value === 'teacher') return 'role-teacher'
  return 'role-student'
})

// --- Имя ---
const form = reactive({ full_name: auth.user?.full_name || '' })
const profileLoading = ref(false)
const profileSuccess = ref(false)
const profileError = ref('')

async function saveProfile() {
  profileLoading.value = true
  profileSuccess.value = false
  profileError.value = ''
  try {
    const res = await http.patch('/auth/me', { full_name: form.full_name })
    auth.user = { ...auth.user, ...res.data }
    profileSuccess.value = true
    setTimeout(() => profileSuccess.value = false, 3000)
  } catch (e: any) {
    profileError.value = e?.response?.data?.detail || 'Ошибка при сохранении'
  } finally {
    profileLoading.value = false
  }
}

// --- Пароль ---
const pwForm = reactive({ current_password: '', new_password: '', confirm_password: '' })
const pwLoading = ref(false)
const pwSuccess = ref(false)
const pwError = ref('')

async function savePassword() {
  pwError.value = ''
  pwSuccess.value = false
  if (pwForm.new_password.length < 8) {
    pwError.value = 'Пароль должен содержать не менее 8 символов'
    return
  }
  if (pwForm.new_password !== pwForm.confirm_password) {
    pwError.value = 'Пароли не совпадают'
    return
  }
  pwLoading.value = true
  try {
    await http.patch('/auth/me', {
      current_password: pwForm.current_password,
      new_password: pwForm.new_password,
    })
    pwSuccess.value = true
    pwForm.current_password = ''
    pwForm.new_password = ''
    pwForm.confirm_password = ''
    setTimeout(() => pwSuccess.value = false, 3000)
  } catch (e: any) {
    pwError.value = e?.response?.data?.detail || 'Ошибка при смене пароля'
  } finally {
    pwLoading.value = false
  }
}
</script>

<style scoped>
.profile h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 24px; }

.profile-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: #fff7f0;
  border: 2px solid #ffe3cf;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
}
.profile-avatar {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: var(--brand-orange);
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.profile-name { font-size: 20px; font-weight: 700; color: var(--brand-purple); }
.profile-email { font-size: 14px; color: var(--text-secondary, #888); margin: 4px 0 8px; }
.profile-role-badge {
  display: inline-block;
  padding: 2px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}
.role-admin { background: #ffeaea; color: var(--brand-red); }
.role-teacher { background: #ffe3cf; color: var(--brand-orange); }
.role-student { background: #e8f4ff; color: #2a7bbf; }

.profile-section {
  background: #fff;
  border: 2px solid #ffe3cf;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}
.profile-section h2 { font-size: 18px; font-weight: 700; color: var(--brand-purple); margin-bottom: 20px; }

.profile-form { display: flex; flex-direction: column; gap: 16px; max-width: 440px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 14px; font-weight: 600; color: #444; }
.form-group input {
  padding: 10px 14px;
  border: 2px solid #ffe3cf;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}
.form-group input:focus { border-color: var(--brand-orange); }
.input-disabled { background: #f5f5f5; color: #aaa; cursor: not-allowed; }
.hint { font-size: 12px; color: var(--text-secondary, #aaa); }

.btn-save {
  padding: 11px 24px;
  background: var(--brand-orange);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
  width: fit-content;
}
.btn-save:hover { background: var(--brand-purple); }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.alert-success {
  padding: 10px 14px;
  background: #edfaf1;
  border: 1.5px solid #6fcf97;
  border-radius: 8px;
  color: #27ae60;
  font-size: 14px;
  font-weight: 600;
}
.alert-error {
  padding: 10px 14px;
  background: #ffeaea;
  border: 1.5px solid var(--brand-red);
  border-radius: 8px;
  color: var(--brand-red);
  font-size: 14px;
  font-weight: 600;
}
</style>
