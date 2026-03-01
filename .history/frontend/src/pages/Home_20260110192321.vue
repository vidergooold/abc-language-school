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

    <!-- Превью курсов (можно оставить как было, если уже есть) -->
    <section class="section">
      <h2 class="section__title">Наши курсы</h2>
      <CoursesPreview />
    </section>

    <!-- Блок статистики/преимуществ (если есть) -->
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

.hero {
  background: #3b2ea8; /* фиолетовый блок, как на примере */
  color: #fff;
  border-radius: 16px;
  padding: 32px 24px;
}

.hero__title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
}

.hero__text {
  font-size: 16px;
  margin-bottom: 20px;
  max-width: 480px;
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
  padding: 10px 18px;
  border-radius: 999px;
  font-size: 15px;
  text-decoration: none;
  cursor: pointer;
}

.btn-primary {
  background: var(--brand-orange);
  color: #fff;
}

.btn-secondary {
  border: 1px solid #fff;
  color: #fff;
  background: transparent;
}

.section {
  background: var(--bg-white);
  border-radius: 16px;
  padding: 24px;
}

.section__title {
  font-size: 22px;
  margin-bottom: 16px;
}

.feedback-section {
  background: transparent;
  padding: 0;
}
</style>
