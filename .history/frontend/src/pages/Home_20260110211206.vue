<template>
  <div class="home">
    <!-- Hero / основной блок -->
    <section class="hero">
      <div class="hero__content">
        <h1 class="hero__title">
          Добро пожаловать в ABC Language School!
        </h1>
        <p class="hero__text">
          Помогаем школьникам и взрослым уверенно заговорить
          на иностранных языках.
        </p>

        <div class="hero__actions">
          <RouterLink to="/enroll" class="btn btn-primary">
            Стать участником
          </RouterLink>
          <RouterLink to="/testing" class="btn btn-secondary">
            Пройти тестирование
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Превью курсов -->
    <section class="section">
      <h2 class="section__title">Наши курсы</h2>
      <CoursesPreview />
    </section>

    <!-- Блок преимуществ / статистики -->
    <section class="section">
      <StatsBlock />
    </section>

    <!-- Обратная связь -->
    <section id="feedback" class="section feedback-section">
      <FeedbackForm />
    </section>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import CoursesPreview from '@/components/home/CoursesPreview.vue'
import StatsBlock from '@/components/home/StatsBlock.vue'
import FeedbackForm from '@/components/home/FeedbackForm.vue'
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Яркий блок: фиолетово-оранжевый градиент */
.hero {
  background: linear-gradient(135deg, var(--brand-purple), var(--brand-orange));
  color: #ffffff;
  border-radius: 24px;
  padding: 36px 24px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
}

.hero__title {
  font-size: var(--font-size-h1);
  font-weight: 700;
  margin-bottom: 12px;
}

.hero__text {
  font-size: 18px;
  margin-bottom: 24px;
  max-width: 520px;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 22px;
  border-radius: 999px;
  font-size: 16px;
  text-decoration: none;
  cursor: pointer;
}

.btn-primary {
  background: var(--brand-orange);
  color: #ffffff;
}

.btn-secondary {
  border: 2px solid #ffffff;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

/* Оранжевые секции */
.section {
  background: #ffe3cf;
  border-radius: 20px;
  padding: 24px;
}

.section__title {
  font-size: var(--font-size-h2);
  font-weight: 700;
  margin-bottom: 16px;
}

.feedback-section {
  background: transparent;
  padding: 0;
}
</style>
