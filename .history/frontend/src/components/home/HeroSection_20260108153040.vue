<template>
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

      <LeadForm />
    </div>
  </section>
</template>

<script setup lang="ts">
import BaseButton from '@/components/ui/BaseButton.vue'
import LeadForm from './LeadForm.vue'

</script>

<style scoped>
.hero {
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
  margin-bottom: 16px;
}

.hero__subtitle {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .hero {
    padding: 72px 32px;
  }

  .hero__title {
    font-size: 40px;
  }
}
</style>
