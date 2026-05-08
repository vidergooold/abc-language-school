<template>
  <header class="account-header">
    <RouterLink to="/" class="logo">
      <img src="/logo.png" alt="ABC Лингвоцентр" class="logo-img" />
    </RouterLink>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.account-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #ffffff;
  border-bottom: 3px solid var(--brand-orange);
  position: sticky;
  top: 0;
  z-index: 100;
}
.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: opacity 0.2s;
}
.logo:hover {
  opacity: 0.8;
}
.logo-img {
  height: 70px;
  width: auto;
  object-fit: contain;
}
</style>
