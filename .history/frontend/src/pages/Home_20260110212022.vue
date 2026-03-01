<template>
  <div class="home">
    <!-- Hero -->
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

    <!-- Двойной блок: Запишись / Узнай уровень -->
    <section class="cta-cards">
      <div class="cta-card cta-card--enroll" @click="goToEnroll">
        <p class="cta-card__title">Запишись</p>
        <p class="cta-card__subtitle">на первое занятие</p>
      </div>

      <div class="cta-card cta-card--level" @click="goToTesting">
        <p class="cta-card__title">Узнай свой</p>
        <p class="cta-card__subtitle">
          <span>уровень</span>
          <span class="accent">английского языка</span>
        </p>
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
import { RouterLink, useRouter } from 'vue-router'
import CoursesPreview from '@/components/home/CoursesPreview.vue'
import StatsBlock from '@/components/home/StatsBlock.vue'
import FeedbackForm from '@/components/home/FeedbackForm.vue'

const router = useRouter()

function goToEnroll() {
  router.push('/enroll')
}

function goToTesting() {
  router.push('/testing')
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Hero */
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

/* Две крупные плитки */
.cta-cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

.cta-card {
  border-radius: 24px;
  padding: 32px 28px;
  cursor: pointer;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.08);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.cta-card--enroll {
  background: linear-gradient(135deg, var(--brand-purple), #35c0c7);
  color: #ffffff;
}

.cta-card--level {
  background: #ffffff;
  color: var(--brand-purple);
}

.cta-card__title {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 6px;
}

.cta-card__subtitle {
  font-size: 20px;
  font-weight: 600;
}

.cta-card__subtitle .accent {
  color: var(--brand-orange);
}

.cta-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
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
