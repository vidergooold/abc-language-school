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
  right: 16px;
  bottom: 24px;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  border: none;
  background: var(--brand-orange);
  color: #fff;
  font-size: 22px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
</style>
