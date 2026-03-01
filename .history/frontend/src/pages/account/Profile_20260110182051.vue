<template>
  <div>
    <h1>Профиль</h1>

    <div class="card">
      <p><strong>Email:</strong> {{ email }}</p>
    </div>

    <h2>Мои заявки</h2>

    <p v-if="enrollmentsStore.loading">Загрузка…</p>
    <p v-else-if="enrollmentsStore.error" class="error">
      {{ enrollmentsStore.error }}
    </p>

    <ul v-else class="enrollments">
      <li v-for="e in enrollmentsStore.enrollments" :key="e.id">
        <strong>{{ e.name }}</strong> — {{ e.phone }}
        <span v-if="e.comment"> ({{ e.comment }})</span>
      </li>
    </ul>

    <p
      v-if="
        !enrollmentsStore.loading &&
        !enrollmentsStore.error &&
        !enrollmentsStore.enrollments.length
      "
    >
      У вас пока нет заявок
    </p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useMyEnrollmentsStore } from '@/stores/myEnrollments'

const enrollmentsStore = useMyEnrollmentsStore()

const email = '—' // позже можно заменить на реальный /auth/me

onMounted(() => {
  enrollmentsStore.fetchMyEnrollments()
})
</script>


<style scoped>
.card {
  background: var(--bg-white);
  padding: 16px;
  border-radius: var(--border-radius);
  margin-bottom: 24px;
}

.enrollments {
  list-style: none;
  padding: 0;
}

.error {
  color: var(--brand-red);
}
</style>
