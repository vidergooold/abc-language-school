<template>
  <div class="grid">
    <CourseCard
      v-for="course in courses"
      :key="course.id"
      :course="course"
    />
  </div>
</template>

<script setup lang="ts">
import CourseCard from './CourseCard.vue'

defineProps<{
  courses: {
    id: number
    title: string
    description: string
    level: string
  }[]
}>()
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
