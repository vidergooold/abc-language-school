<template>
  <div v-if="!isAccount" class="floating-cta">
    <RouterLink to="/enroll" class="cta-btn cta-btn--enroll">
      <span class="cta-btn__title">Запишись</span>
      <span class="cta-btn__subtitle">на первое занятие</span>
    </RouterLink>
    <RouterLink to="/testing" class="cta-btn cta-btn--level">
      <span class="cta-btn__title">Узнай свой</span>
      <span class="cta-btn__subtitle">уровень</span>
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'

const route = useRoute()
const isAccount = computed(() => route.path.startsWith('/account') || route.path.startsWith('/login'))
</script>

<style scoped>
.floating-cta {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  z-index: 100;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
}
.cta-btn {
  padding: 16px 20px;
  text-align: center;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}
.cta-btn:hover { transform: translateY(-4px); }
.cta-btn--enroll {
  background: linear-gradient(135deg, var(--brand-red), var(--brand-orange));
  color: #fff;
}
.cta-btn--level {
  background: #fff;
  color: var(--brand-red);
  border-left: 1px solid #e0e0e0;
}
.cta-btn__title { font-size: 20px; font-weight: 700; margin-bottom: 2px; }
.cta-btn__subtitle { font-size: 16px; font-weight: 600; }
.cta-btn--level .cta-btn__subtitle { color: var(--brand-orange); }
</style>
