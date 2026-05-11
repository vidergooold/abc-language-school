<template>
  <section class="courses">
    <h2 class="section-title">Наши курсы</h2>

    <div class="courses-grid">
      <div class="course-card">
        <span class="level">A1–A2</span>
        <h3>Английский для детей</h3>
        <p>Игровое обучение и развитие речи</p>
        <div class="course-groups">
          <span class="course-group">Дошкольники</span>
          <span class="course-group">FH1</span>
          <span class="course-group">AS1</span>
          <span class="course-group">AS2</span>
        </div>
      </div>

      <div class="course-card">
        <span class="level">A2–B1</span>
        <h3>Английский для школьников</h3>
        <p>Подготовка к ОГЭ, ЕГЭ и уверенное владение языком</p>
        <div class="course-groups">
          <span class="course-group">AS3</span>
          <span class="course-group">AS4</span>
          <span class="course-group">GWA1+</span>
          <span class="course-group">GWA2</span>
        </div>
      </div>

      <div class="course-card">
        <span class="level">B1–C1</span>
        <h3>Английский для взрослых</h3>
        <p>Для работы, путешествий и общения</p>
        <div class="course-groups">
          <span class="course-group">GWB1</span>
          <span class="course-group">GWB1+</span>
          <span class="course-group">GWB2</span>
          <span class="course-group">GWB2+</span>
          <span class="course-group">GWC1</span>
          <span class="course-group">Взрослые групповые</span>
        </div>
      </div>

      <div class="course-card">
        <span class="level">Любой уровень</span>
        <h3>Индивидуально и мини-группы</h3>
        <p>Максимальный фокус на вашем прогрессе</p>
        <div class="course-groups">
          <span class="course-group">Мини-группа (2 чел.)</span>
          <span class="course-group">Индивидуальные занятия</span>
        </div>
      </div>

      <div class="course-card">
        <span class="level">HSK 1–3</span>
        <h3>Китайский язык</h3>
        <p>Для начинающих и продолжающих, разговорный и письменный</p>
        <div class="course-groups">
          <span class="course-group">Китайский</span>
        </div>
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
  margin-bottom: 12px;
}

.course-groups {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.course-group {
  font-size: 12px;
  line-height: 1.2;
  padding: 4px 8px;
  border-radius: 999px;
  background: #fff3eb;
  color: var(--brand-red);
}

@media (min-width: 768px) {
  .courses-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
