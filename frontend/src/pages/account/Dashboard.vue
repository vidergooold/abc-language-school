<template>
  <div class="dashboard-card-page">
    <div class="card-shell">
      <section class="profile-hero">
        <div class="hero-copy">
          <p class="hero-kicker">Личный кабинет</p>
          <h1>Профиль</h1>
          <p class="hero-name">{{ displayName }}</p>
          <p class="hero-subtitle">Управляйте основными данными профиля в одном месте.</p>

          <div class="hero-badges">
            <span class="hero-badge role">{{ roleLabel }}</span>
            <span class="hero-badge">Аккаунт активен</span>
          </div>
        </div>

        <div class="hero-avatar">
          <span>{{ initials }}</span>
        </div>
      </section>

      <section class="profile-summary">
        <article class="summary-card accent-login">
          <span class="summary-label">Логин</span>
          <strong class="summary-value">{{ auth.user?.email || '—' }}</strong>
          <p class="summary-note">Используется для входа в кабинет</p>
        </article>

        <article class="summary-card accent-group">
          <span class="summary-label">Группа</span>
          <strong class="summary-value">{{ groupLabel }}</strong>
          <p class="summary-note">Текущая учебная группа</p>
        </article>

        <article class="summary-card accent-contact">
          <span class="summary-label">Телефон</span>
          <strong class="summary-value">{{ form.phone || 'не указан' }}</strong>
          <p class="summary-note">Контакт для связи со школой</p>
        </article>
      </section>

      <section v-if="isStudent && paymentSummary" class="payment-attendance-block">
        <div class="block-head">
          <h2>Оплата и посещаемость</h2>
          <span v-if="paymentSummary.payment_required" class="payment-alert">Необходимо оплатить обучение</span>
        </div>

        <div class="block-grid">
          <article class="mini-card">
            <span class="mini-label">К оплате</span>
            <strong class="mini-value">{{ money(paymentSummary.amount_remaining_to_pay_now) }}</strong>
          </article>
          <article class="mini-card">
            <span class="mini-label">Уже оплачено</span>
            <strong class="mini-value">{{ money(paymentSummary.total_paid) }}</strong>
          </article>
          <article class="mini-card">
            <span class="mini-label">Посещено занятий</span>
            <strong class="mini-value">{{ paymentSummary.lessons_attended }}</strong>
          </article>
          <article class="mini-card">
            <span class="mini-label">Осталось занятий</span>
            <strong class="mini-value">{{ paymentSummary.lessons_remaining }}</strong>
          </article>
        </div>

        <div class="calc-line">
          <span>Стоимость 1 занятия: <strong>{{ money(paymentSummary.cost_per_lesson) }}</strong></span>
          <span>Начислено на текущий момент: <strong>{{ money(paymentSummary.amount_should_be_paid_now) }}</strong></span>
          <span>Текущий долг: <strong>{{ money(paymentSummary.current_debt) }}</strong></span>
        </div>
      </section>

      <form @submit.prevent="save" class="card-form">
        <section class="form-section">
          <div class="section-head">
            <h2>Основные данные</h2>
            <p>Обновите информацию, которая отображается в карточке пользователя.</p>
          </div>

          <div class="form-grid">
            <div class="form-row">
              <label>Имя *</label>
              <input v-model="form.first_name" required :disabled="saving" />
            </div>
            <div class="form-row">
              <label>Фамилия *</label>
              <input v-model="form.last_name" required :disabled="saving" />
            </div>
          </div>

          <div class="form-grid single-column">
            <div class="form-row full">
              <label>Email *</label>
              <input :value="auth.user?.email || ''" disabled />
            </div>

            <div class="form-row full">
              <label>Моб. телефон</label>
              <input v-model="form.phone" :disabled="saving" placeholder="Например: +7 999 123-45-67" />
            </div>

            <div class="form-row full">
              <label>Доп. инфо</label>
              <textarea v-model="form.notes" rows="4" :disabled="saving" placeholder="Краткая информация, пожелания, заметки"></textarea>
            </div>
          </div>
        </section>

        <section class="form-section security-section">
          <div class="section-head">
            <h2>Безопасность</h2>
            <p>Пароль можно оставить пустым, если менять его сейчас не нужно.</p>
          </div>

          <div class="form-grid single-column">
            <div class="form-row full">
              <label>Новый пароль <span class="hint">только если хотите изменить</span></label>
              <input v-model="form.new_password" type="password" :disabled="saving" />
            </div>

            <div class="form-row full">
              <label>Подтверждение пароля *</label>
              <input v-model="form.confirm_password" type="password" :disabled="saving" />
              <div v-if="passwordMismatch" class="field-error">Пароли не совпадают</div>
            </div>
          </div>
        </section>

        <div class="form-actions">
          <button type="submit" class="btn-save" :disabled="saving || passwordMismatch">
            {{ saving ? 'Сохранение...' : 'Сохранить изменения' }}
          </button>
        </div>

        <div v-if="successMsg" class="alert-success">{{ successMsg }}</div>
        <div v-if="errorMsg" class="alert-error">{{ errorMsg }}</div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const form = ref({
  first_name: '',
  last_name: '',
  phone: '',
  notes: '',
  new_password: '',
  confirm_password: '',
})

const groupLabel = computed(() => {
  return 'не назначена'
})

const displayName = computed(() => auth.user?.full_name || auth.user?.email || 'Пользователь')
const isStudent = computed(() => auth.user?.role === 'student')

const paymentSummary = ref<null | {
  total_paid: number
  amount_remaining_to_pay_now: number
  lessons_attended: number
  lessons_remaining: number
  payment_required: boolean
  cost_per_lesson: number
  amount_should_be_paid_now: number
  current_debt: number
}>(null)

const initials = computed(() => {
  const source = (auth.user?.full_name || auth.user?.email || 'U').trim()
  const parts = source.split(/\s+/).filter(Boolean)
  if (parts.length >= 2) {
    return `${parts[0]?.charAt(0) ?? ''}${parts[1]?.charAt(0) ?? ''}`.toUpperCase()
  }
  return source.slice(0, 2).toUpperCase()
})

const roleLabel = computed(() => {
  const role = auth.user?.role
  if (role === 'admin') return 'Администратор'
  if (role === 'teacher') return 'Преподаватель'
  return 'Студент'
})

const passwordMismatch = computed(() =>
  !!form.value.confirm_password && form.value.new_password !== form.value.confirm_password
)

onMounted(() => {
  const fullName = auth.user?.full_name || ''
  const [first, ...rest] = fullName.split(' ')
  form.value.first_name = first || ''
  form.value.last_name = rest.join(' ') || ''
  form.value.phone = ''
  form.value.notes = ''

  if (isStudent.value) {
    loadPaymentAttendanceSummary()
  }
})

function money(value: number) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 2,
  }).format(value || 0)
}

async function loadPaymentAttendanceSummary() {
  try {
    const { data } = await http.get('/payments/my-summary')
    paymentSummary.value = data
  } catch {
    paymentSummary.value = null
  }
}

async function save() {
  if (passwordMismatch.value) return
  saving.value = true
  successMsg.value = ''
  errorMsg.value = ''

  try {
    const payload: any = {
      full_name: `${form.value.first_name.trim()} ${form.value.last_name.trim()}`.trim(),
      phone: form.value.phone,
      notes: form.value.notes,
    }
    if (form.value.new_password) payload.password = form.value.new_password

    await http.patch('/users/me', payload)
    auth.user!.full_name = payload.full_name
    form.value.new_password = ''
    form.value.confirm_password = ''
    successMsg.value = 'Данные успешно обновлены!'
    setTimeout(() => (successMsg.value = ''), 4000)
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Ошибка при сохранении данных'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.dashboard-card-page {
  max-width: 860px;
  margin: 0 auto;
}

.card-shell {
  position: relative;
  overflow: hidden;
  padding: 22px;
  border-radius: 22px;
  border: 1px solid rgba(193, 108, 11, 0.16);
  background:
    radial-gradient(circle at top right, rgba(255, 217, 159, 0.95), transparent 28%),
    radial-gradient(circle at left center, rgba(255, 245, 228, 0.8), transparent 32%),
    linear-gradient(145deg, #fff8ef 0%, #ffe3bb 48%, #ffd3a0 100%);
  box-shadow: 0 24px 60px rgba(128, 67, 5, 0.14);
}

.card-shell::after {
  content: '';
  position: absolute;
  inset: 12px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.45);
  pointer-events: none;
}

.profile-hero {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.hero-kicker {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: #c46b00;
}

.profile-hero h1 {
  margin-bottom: 8px;
  font-size: 30px;
  font-weight: 900;
  color: #2f1805;
  letter-spacing: -0.03em;
}

.hero-name {
  font-size: 18px;
  font-weight: 700;
  color: #4b2505;
  margin-bottom: 8px;
}

.hero-subtitle {
  max-width: 520px;
  font-size: 14px;
  color: rgba(72, 40, 10, 0.78);
  margin-bottom: 10px;
}

.hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(255, 184, 93, 0.55);
  font-size: 13px;
  font-weight: 700;
  color: #7a4304;
  backdrop-filter: blur(8px);
}

.hero-badge.role {
  background: linear-gradient(135deg, #ff922f, #ffb85b);
  color: #fff;
  border-color: transparent;
}

.hero-avatar {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 78px;
  height: 78px;
  border-radius: 20px;
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.65), rgba(255, 238, 208, 0.35)),
    linear-gradient(135deg, #ff8a1f, #ffcb78);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55), 0 18px 30px rgba(178, 92, 10, 0.2);
}

.hero-avatar span {
  font-size: 26px;
  font-weight: 900;
  color: #fffaf2;
  letter-spacing: 0.04em;
}

.profile-summary {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.summary-card {
  padding: 12px;
  border-radius: 14px;
  background: rgba(255, 252, 247, 0.7);
  border: 1px solid rgba(215, 154, 92, 0.22);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.summary-card.accent-login {
  background: linear-gradient(180deg, rgba(255, 248, 236, 0.95), rgba(255, 236, 204, 0.84));
}

.summary-card.accent-group {
  background: linear-gradient(180deg, rgba(255, 247, 232, 0.96), rgba(255, 225, 186, 0.86));
}

.summary-card.accent-contact {
  background: linear-gradient(180deg, rgba(255, 243, 231, 0.96), rgba(255, 216, 176, 0.82));
}

.summary-label {
  display: block;
  margin-bottom: 8px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #b46300;
}

.summary-value {
  display: block;
  font-size: 16px;
  line-height: 1.35;
  color: #341a04;
  word-break: break-word;
}

.summary-note {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(69, 38, 9, 0.72);
}

.payment-attendance-block {
  position: relative;
  z-index: 1;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(211, 150, 87, 0.24);
  background: rgba(255, 252, 247, 0.78);
  margin-bottom: 12px;
}

.block-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.block-head h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: #3a1d00;
}

.payment-alert {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: #fff0c7;
  color: #92400e;
  font-size: 12px;
  font-weight: 700;
}

.block-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.mini-card {
  padding: 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(214, 164, 109, 0.24);
}

.mini-label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #8a4b08;
  margin-bottom: 6px;
}

.mini-value {
  font-size: 16px;
  color: #301604;
}

.calc-line {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;
  color: rgba(69, 38, 9, 0.82);
}

.card-form {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 12px;
}

.form-section {
  padding: 14px;
  border-radius: 16px;
  background: rgba(255, 253, 250, 0.76);
  border: 1px solid rgba(211, 150, 87, 0.2);
  backdrop-filter: blur(10px);
}

.security-section {
  background: rgba(255, 247, 237, 0.7);
}

.section-head {
  margin-bottom: 10px;
}

.section-head h2 {
  margin-bottom: 6px;
  font-size: 16px;
  font-weight: 800;
  color: #3a1d00;
}

.section-head p {
  font-size: 13px;
  color: rgba(77, 45, 15, 0.7);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.form-grid.single-column {
  grid-template-columns: 1fr;
}

.form-row {
  display: grid;
  gap: 6px;
}

.form-row.full {
  grid-column: 1 / -1;
}

.form-row label {
  font-size: 13px;
  font-weight: 800;
  color: #5b2d00;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.form-row .hint {
  font-size: 11px;
  font-weight: 700;
  color: #a56217;
}

.form-row input,
.form-row textarea {
  width: 100%;
  min-height: 42px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1.5px solid rgba(210, 145, 74, 0.4);
  background: rgba(255, 255, 255, 0.9);
  color: #1e1304;
  font-size: 15px;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.form-row input:focus,
.form-row textarea:focus {
  border-color: #f08c1a;
  box-shadow: 0 0 0 4px rgba(240, 140, 26, 0.12);
  outline: none;
}

.form-row textarea {
  min-height: 84px;
  resize: vertical;
}

.form-row input:disabled,
.form-row textarea:disabled {
  background: rgba(247, 241, 233, 0.95);
  color: rgba(60, 40, 20, 0.72);
  cursor: not-allowed;
}

.field-error {
  font-size: 13px;
  font-weight: 700;
  color: #b42318;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  margin-top: 4px;
}

.btn-save {
  min-height: 42px;
  padding: 9px 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #f47f00, #ff9f33);
  box-shadow: 0 14px 24px rgba(210, 118, 18, 0.24);
  color: #fff;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 18px 28px rgba(210, 118, 18, 0.28);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.alert-success,
.alert-error {
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
}

.alert-success {
  background: rgba(232, 247, 234, 0.96);
  color: #166534;
}

.alert-error {
  background: rgba(254, 226, 226, 0.96);
  color: #b91c1c;
}

@media (max-width: 840px) {
  .profile-hero,
  .profile-summary,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .block-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .profile-hero {
    flex-direction: column;
  }

  .hero-avatar {
    width: 88px;
    height: 88px;
    border-radius: 24px;
  }
}

@media (max-width: 680px) {
  .card-shell {
    padding: 16px;
    border-radius: 16px;
  }

  .profile-hero h1 {
    font-size: 24px;
  }

  .summary-card,
  .form-section {
    padding: 12px;
    border-radius: 12px;
  }

  .block-grid {
    grid-template-columns: 1fr;
  }
}
</style>
