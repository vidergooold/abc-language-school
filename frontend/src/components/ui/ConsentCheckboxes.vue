<template>
  <div class="consent-block">
    <label class="consent-row">
      <input
        type="checkbox"
        :checked="modelValue.privacy"
        @change="emit('update:modelValue', { ...modelValue, privacy: ($event.target as HTMLInputElement).checked })"
        required
      />
      <span>
        Подтверждаю, что ознакомлен(а) с
        <a :href="privacyUrl" target="_blank" class="consent-link">Политикой конфиденциальности</a>
      </span>
    </label>
    <label class="consent-row">
      <input
        type="checkbox"
        :checked="modelValue.personalData"
        @change="emit('update:modelValue', { ...modelValue, personalData: ($event.target as HTMLInputElement).checked })"
        required
      />
      <span>
        Подтверждаю
        <a :href="consentUrl" target="_blank" class="consent-link">согласие на обработку персональных данных</a>
      </span>
    </label>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: { privacy: boolean; personalData: boolean }
  privacyUrl?: string
  consentUrl?: string
}>()
const emit = defineEmits(['update:modelValue'])
</script>

<style scoped>
.consent-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 16px 0;
}
.consent-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 15px;
  cursor: pointer;
  line-height: 1.5;
}
.consent-row input[type="checkbox"] {
  width: 18px;
  height: 18px;
  min-width: 18px;
  margin-top: 2px;
  accent-color: var(--brand-orange);
  cursor: pointer;
}
.consent-link {
  color: var(--brand-orange);
  text-decoration: underline;
  font-weight: 600;
  transition: color 0.2s;
}
.consent-link:hover {
  color: var(--brand-red);
}
</style>
