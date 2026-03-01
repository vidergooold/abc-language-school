<template>
  <div class="app">
    <Header />
    <main class="app-main">
      <router-view />
    </main>
    <Footer />
    <ScrollToTop />
    <FloatingCTA />
  </div>
</template>

<script setup lang="ts">
import Header from './components/layout/Header.vue'
import Footer from './components/layout/Footer.vue'
import ScrollToTop from './components/ui/ScrollToTop.vue'
import FloatingCTA from './components/ui/FloatingCTA.vue'
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  color: var(--text-main);
  font-size: var(--font-size-base);
  padding-bottom: 80px; /* отступ снизу под фиксированные кнопки */
}

.app-main {
  flex: 1;
  padding: 16px;
}
</style>
