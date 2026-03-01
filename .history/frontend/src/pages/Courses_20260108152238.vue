<template>
  <main class="courses-page">
    <h1 class="page-title">Курсы английского языка</h1>

    <CoursesFilter
      :levels="levels"
      v-model:selectedLevel="selectedLevel"
    />

    <CoursesGrid :courses="filteredCourses" />
  </main>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CoursesFilter from '@/components/courses/CoursesFilter.vue'
import CoursesGrid from '@/components/courses/CoursesGrid.vue'

type Course = {
  id: number
  title: string
  description: string
  level: string
}

const courses = ref<Course[]>([
  {
    id: 1,
    title: 'Английский для детей',
    description: 'Игровое обучение, развитие речи и восприятия языка',
    level: 'A1–A2',
  },
  {
    id: 2,
    title: 'Английский для взрослых',
    description: 'Для работы, путешествий и повседневного общения',
    level: 'B1–B2',
  },
  {
    id: 3,
    title: 'Подготовка к экзаменам',
    description: 'IELTS, TOEFL, международные сертификаты',
    level: 'C1–C2',
  },
])

const levels = ['Все', 'A1–A2', 'B1–B2', 'C1–C2']
const selectedLevel = ref('Все')

const filteredCourses = computed(() => {
  if (selectedLevel.value === 'Все') {
    return courses.value
  }
  return courses.value.filter(c => c.level === selectedLevel.value)
})
</script>

<style scoped>
.courses-page {
  padding: 32px 16px;
}

.page-title {
  font-size: 26px;
  margin-bottom: 24px;
}
</style>
