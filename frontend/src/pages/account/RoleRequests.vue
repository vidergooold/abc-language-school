<template>
  <div class="role-requests-page">
    <h1>Проверка сотрудников</h1>
    <p class="subtitle">Назначьте роль после проверки данных сотрудника.</p>

    <div class="toolbar">
      <label class="checkbox">
        <input v-model="showOnlyStudents" type="checkbox" />
        <span>Показывать только со статусом "ученик"</span>
      </label>
      <button class="refresh-btn" @click="loadUsers" :disabled="loading">
        {{ loading ? 'Обновление...' : 'Обновить' }}
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="filteredUsers.length" class="users-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Имя</th>
          <th>Email</th>
          <th>Текущая роль</th>
          <th>Статус</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in filteredUsers" :key="u.id">
          <td>{{ u.id }}</td>
          <td>{{ u.full_name || '—' }}</td>
          <td>{{ u.email }}</td>
          <td>
            <span class="role-badge" :class="`role-${u.role}`">{{ roleLabel(u.role) }}</span>
          </td>
          <td>
            <span :class="['status', u.is_active ? 'active' : 'inactive']">
              {{ u.is_active ? 'Активен' : 'Заблокирован' }}
            </span>
          </td>
          <td class="actions">
            <button
              class="btn teacher"
              @click="setRole(u.id, 'teacher')"
              :disabled="u.role === 'teacher' || assigningId === u.id"
            >
              Назначить преподавателем
            </button>
            <button
              class="btn admin"
              @click="setRole(u.id, 'admin')"
              :disabled="u.role === 'admin' || assigningId === u.id"
            >
              Назначить админом
            </button>
            <button
              class="btn student"
              @click="setRole(u.id, 'student')"
              :disabled="u.role === 'student' || assigningId === u.id"
            >
              Оставить учеником
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="empty">Нет пользователей для отображения.</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import http from '@/api/http'

type Role = 'student' | 'teacher' | 'admin'

type UserItem = {
  id: number
  email: string
  full_name: string | null
  role: Role
  is_active: boolean
}

const users = ref<UserItem[]>([])
const loading = ref(false)
const assigningId = ref<number | null>(null)
const error = ref('')
const showOnlyStudents = ref(true)

const filteredUsers = computed(() => {
  const list = showOnlyStudents.value
    ? users.value.filter((u) => u.role === 'student')
    : users.value
  return [...list].sort((a, b) => b.id - a.id)
})

onMounted(loadUsers)

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    const res = await http.get('/admin/users')
    users.value = Array.isArray(res.data) ? res.data : []
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Не удалось загрузить список пользователей'
    users.value = []
  } finally {
    loading.value = false
  }
}

async function setRole(userId: number, role: Role) {
  assigningId.value = userId
  error.value = ''
  try {
    await http.patch(`/admin/users/${userId}/role`, { role })
    await loadUsers()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Не удалось назначить роль'
  } finally {
    assigningId.value = null
  }
}

function roleLabel(role: Role) {
  if (role === 'admin') return 'Администратор'
  if (role === 'teacher') return 'Преподаватель'
  return 'Ученик'
}
</script>

<style scoped>
.role-requests-page {
  max-width: 100%;
}

h1 {
  color: var(--brand-purple);
  margin-bottom: 8px;
}

.subtitle {
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.refresh-btn {
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fff;
  padding: 8px 12px;
  font-weight: 600;
  cursor: pointer;
}

.error {
  margin: 12px 0;
  color: #b00020;
  font-weight: 600;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.users-table th,
.users-table td {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: top;
  text-align: left;
}

.role-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.role-student {
  background: #e8f4ff;
  color: #2a7bbf;
}

.role-teacher {
  background: #fff4e8;
  color: #d96a00;
}

.role-admin {
  background: #ffe9e9;
  color: #c02626;
}

.status.active {
  color: #2b8a3e;
  font-weight: 600;
}

.status.inactive {
  color: #999;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.btn {
  border: none;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  cursor: pointer;
  font-weight: 600;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.teacher {
  background: #ffe9cf;
  color: #995200;
}

.btn.admin {
  background: #ffd9d9;
  color: #9b1f1f;
}

.btn.student {
  background: #e8f1ff;
  color: #2f5fa8;
}

.empty {
  color: #888;
  margin-top: 12px;
}
</style>
