<template>
  <section class="stats">
    <div class="stats__item">
      <strong class="stats__number">10+</strong>
      <span class="stats__label">лет опыта</span>
    </div>

    <div class="stats__item">
      <strong class="stats__number">1500+</strong>
      <span class="stats__label">учеников</span>
    </div>

    <div class="stats__item">
      <strong class="stats__number">98%</strong>
      <span class="stats__label">довольных клиентов</span>
    </div>
  </section>
</template>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  padding: 32px 16px;
  background: var(--bg-white);
  border-radius: 16px;
}

.stats__item {
  text-align: center;
}

.stats__number {
  display: block;
  font-size: 64px; /* как на скрине */
  font-weight: 900;
  color: var(--brand-red);
  line-height: 1;
  margin-bottom: 8px;
}

.stats__label {
  display: block;
  font-size: 18px;
  color: var(--text-secondary);
  font-weight: 500;
}

@media (min-width: 768px) {
  .stats {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
