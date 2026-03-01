<template>
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
</template>

<style scoped>
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

@media (min-width: 768px) {
  .stats {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
