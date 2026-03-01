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
  bottom: 100px; /* было 32px — подняли над фиксированными кнопками */
  width: 56px;
  height: 56px;
  border-radius: 999px;
  border: none;
  background: var(--brand-orange);
  color: #fff;
  font-size: 32px;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s, box-shadow 0.2s;
  z-index: 101; /* выше FloatingCTA */
}

.scroll-top:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}
</style>
