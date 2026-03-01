<template>
  <section class="courses">
    <h2 class="section-title">Наши курсы</h2>

    <div class="courses-grid">
      <div class="course-card">
        <span class="level">A1–A2</span>
        <h3>Английский для детей</h3>
        <p>Игровое обучение и развитие речи</p>
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
</template>

<style scoped>
.courses {
  padding: 0;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
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
  background: var(--brand-orange);
  color: #ffffff;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 12px;
}

.course-card h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.course-card p {
  font-size: 16px;
  color: var(--text-secondary);
}

@media (min-width: 768px) {
  .courses-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
