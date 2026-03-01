<template>
  <button class="base-btn">
    <slot />
  </button>
</template>

<style scoped>
.base-btn {
  background: var(--brand-orange);
  color: #fff;
  border: none;
  padding: 14px 20px;
  border-radius: var(--border-radius);
  font-size: 16px;
  cursor: pointer;
  transition: var(--transition);
}

.base-btn:hover {
  background: #ea6a10;
}
</style>
