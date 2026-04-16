<template>
  <div class="app" :class="{ 'no-cta': isAccount }">
    <AccountHeader v-if="isAccount" />
    <Header v-else />
    <main class="app-main">
      <router-view />
    </main>
    <Footer v-if="!isAccount" />
    <ScrollToTop />
    <FloatingCTA v-if="!isAccount" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from './components/layout/Header.vue'
import AccountHeader from './components/layout/AccountHeader.vue'
import Footer from './components/layout/Footer.vue'
import ScrollToTop from './components/ui/ScrollToTop.vue'
import FloatingCTA from './components/ui/FloatingCTA.vue'

const route = useRoute()
const isAccount = computed(() =>
  route.path.startsWith('/account') ||
  route.path.startsWith('/login') ||
  route.path.startsWith('/blanks')
)
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  color: var(--text-main);
  font-size: var(--font-size-base);
  padding-bottom: 80px;
}

.app.no-cta {
  padding-bottom: 0;
}

.app-main {
  flex: 1;
  padding: 16px;
}
</style>
