<template>
  <div class="app">
    <Header />
    <main class="app-main">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import Header from './components/layout/Header.vue'
import Footer from './components/layout/Footer.vue'
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  color: var(--text-main);
  font-size: var(--font-size-base);
}

.app-main {
  flex: 1; /* растягиваем контент, футер падает вниз */
  padding: 16px;
}
</style>
