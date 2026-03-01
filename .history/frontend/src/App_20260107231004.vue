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
  background: var(--bg-main);
  color: var(--text-main);
}

.app-main {
  padding: 16px;
}
</style>
