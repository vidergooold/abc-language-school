<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero__content">
        <img src="/logo.png" alt="Логотип ABC Language School" class="hero__logo" />
        <h1 class="hero__title">
          Добро пожаловать<br/>в ABC Language School!
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

    <!-- Новости -->
    <section class="section">
      <NewsSection />
    </section>

    <!-- Превью курсов -->
    <section class="section">
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
import CoursesPreview from '@/components/home/CoursesPreview.vue'
import StatsBlock from '@/components/home/StatsBlock.vue'
import FeedbackForm from '@/components/home/FeedbackForm.vue'
import NewsSection from '@/components/home/NewsSection.vue'
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Hero */
.hero {
  background: linear-gradient(135deg, var(--brand-red), var(--brand-orange));
  color: #ffffff;
  border-radius: 24px;
  padding: 48px 32px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
}

.hero__logo {
  width: 120px;
  height: auto;
  margin-bottom: 24px;
  display: block;
}

.hero__title {
  font-size: clamp(32px, 5vw, 52px);
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.hero__text {
  font-size: 20px;
  margin-bottom: 28px;
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
  padding: 14px 26px;
  border-radius: 999px;
  font-size: 17px;
  text-decoration: none;
  cursor: pointer;
  font-weight: 600;
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

/* Секции */
.section {
  background: #ffe3cf;
  border-radius: 20px;
  padding: 24px;
}

.feedback-section {
  background: transparent;
  padding: 0;
}
</style>
