<template>
  <button
    v-if="visible"
    class="scroll-top"
    @click="scrollToTop"
    aria-label="Наверх"
  >
    ↑
  </button>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'

const visible = ref(false)

function onScroll() {
  visible.value = window.scrollY > 300
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  window.addEventListener('scroll', onScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
.scroll-top {
  position: fixed;
  right: 24px;
  bottom: 32px;
  width: 56px;  /* было 40px */
  height: 56px; /* было 40px */
  border-radius: 999px;
  border: none;
  background: var(--brand-orange);
  color: #fff;
  font-size: 32px; /* было 22px */
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s, box-shadow 0.2s;
}

.scroll-top:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}
</style>
