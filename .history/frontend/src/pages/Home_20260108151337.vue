<template>
  <main>
    <!-- HERO -->
    <section class="hero">
      <div class="hero__content">
        <span class="hero__badge">Английский язык • Новосибирск</span>
        <h1 class="hero__title">
          Школа английского языка<br />
          для детей и взрослых
        </h1>
        <p class="hero__subtitle">
          Обучение от A1 до C2 • Малые группы • Пробный урок бесплатно
        </p>

        <div class="hero__actions">
          <BaseButton>Записаться на пробный урок</BaseButton>
        </div>
      </div>
    </section>

    <!-- STATS -->
    <section class="stats">
      <div class="stats__item">
        <strong>10+</strong>
        <span>лет опыта</span>
      </div>
      <div class="stats__item">
        <strong>1500+</strong>
        <span>учеников</span>
      </div>
      <div class="stats__item">
        <strong>98%</strong>
        <span>довольных клиентов</span>
      </div>
    </section>

    <!-- COURSES PREVIEW -->
    <section class="courses-preview">
      <h2 class="section-title">Наши курсы</h2>

      <div class="courses-grid">
        <div class="course-card">
          <span class="level">A1–A2</span>
          <h3>Английский для детей</h3>
          <p>Игровое обучение и развитие разговорных навыков</p>
        </div>

        <div class="course-card">
          <span class="level">B1–B2</span>
          <h3>Английский для взрослых</h3>
          <p>Для работы, путешествий и общения</p>
        </div>

        <div class="course-card">
          <span class="level">C1–C2</span>
          <h3>Подготовка к экзаменам</h3>
          <p>IELTS, TOEFL, международные сертификаты</p>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import BaseButton from '@/components/ui/BaseButton.vue'
</script>

<style scoped>
/* HERO */
.hero {
  background: var(--bg-main);
  padding: 48px 16px;
}

.hero__badge {
  display: inline-block;
  background: var(--brand-yellow);
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  margin-bottom: 16px;
}

.hero__title {
  font-size: 28px;
  line-height: 1.2;
  margin-bottom: 16px;
}

.hero__subtitle {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.hero__actions {
  margin-top: 16px;
}

/* STATS */
.stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  padding: 32px 16px;
  background: var(--bg-white);
}

.stats__item {
  text-align: center;
}

.stats__item strong {
  font-size: 24px;
  color: var(--brand-orange);
}

.stats__item span {
  display: block;
  color: var(--text-secondary);
}

/* COURSES */
.courses-preview {
  padding: 48px 16px;
}

.section-title {
  font-size: 22px;
  margin-bottom: 24px;
}

.courses-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.course-card {
  background: var(--bg-white);
  padding: 20px;
  border-radius: var(--border-radius);
}

.course-card .level {
  display: inline-block;
  background: var(--brand-yellow);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 8px;
}

.course-card h3 {
  margin-bottom: 8px;
}

/* TABLET+ */
@media (min-width: 768px) {
  .hero {
    padding: 72px 32px;
  }

  .hero__title {
    font-size: 40px;
  }

  .stats {
    grid-template-columns: repeat(3, 1fr);
  }

  .courses-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
