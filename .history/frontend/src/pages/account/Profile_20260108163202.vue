<template>
  <div>
    <h1>Профиль</h1>

    <div class="card">
      <p><strong>Email:</strong> {{ user.email }}</p>
    </div>

    <h2>Мои заявки</h2>

    <ul class="enrollments">
      <li v-for="e in enrollments" :key="e.id">
        {{ e.name }} — {{ e.phone }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
const user = {
  email: 'student@example.com',
}

const enrollments = [
  { id: 1, name: 'Анна', phone: '+7 900 123-45-67' },
  { id: 2, name: 'Анна', phone: '+7 900 765-43-21' },
]
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
</style>
