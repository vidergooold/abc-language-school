<template>
  <div class="card">
    <span class="level">{{ course.level }}</span>
    <h3>{{ course.title }}</h3>
    <p>{{ course.description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  course: {
    title: string
    description: string
    level: string
  }
}>()
</script>

<style scoped>
.card {
  background: var(--bg-white);
  padding: 20px;
  border-radius: var(--border-radius);
}

.level {
  display: inline-block;
  background: var(--brand-yellow);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 8px;
}
</style>
