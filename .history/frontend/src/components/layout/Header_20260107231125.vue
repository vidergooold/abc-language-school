<template>
  <header class="header">
    <div class="logo">ABC School</div>
    <nav class="nav">
      <a href="/">Главная</a>
      <a href="/courses">Курсы</a>
      <a href="/login" class="cta">Войти</a>
    </nav>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-white);
}

.logo {
  font-weight: 700;
  font-size: 18px;
}

.nav a {
  margin-left: 12px;
  text-decoration: none;
  color: var(--text-main);
}

.cta {
  padding: 8px 12px;
  background: var(--brand-orange);
  color: white;
  border-radius: var(--border-radius);
}
</style>
