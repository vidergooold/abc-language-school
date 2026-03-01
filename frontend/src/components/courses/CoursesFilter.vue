<template>
  <div class="filter">
    <button
      v-for="level in levels"
      :key="level"
      :class="['filter-btn', { active: level === selectedLevel }]"
      @click="$emit('update:selectedLevel', level)"
    >
      {{ level }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  levels: string[]
  selectedLevel: string
}>()

defineEmits<{
  (e: 'update:selectedLevel', value: string): void
}>()
</script>

<style scoped>
.filter {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.filter-btn {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid var(--brand-orange);
  background: transparent;
  color: var(--brand-orange);
  cursor: pointer;
}

.filter-btn.active {
  background: var(--brand-orange);
  color: #fff;
}
</style>
