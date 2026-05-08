<template>
  <div class="report-filters">
    <div class="filter-field">
      <label>Филиал</label>
      <select :value="branchIdValue" @change="onBranchSelect">
        <option value="">-- Выберите филиал --</option>
        <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </div>

    <div class="filter-field">
      <label>Преподаватель</label>
      <select :value="teacherIdValue" @change="onTeacherSelect" :disabled="!branchId">
        <option value="">-- Выберите преподавателя --</option>
        <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
      </select>
    </div>

    <div class="filter-field">
      <label>Группа</label>
      <select :value="groupIdValue" @change="onGroupSelect" :disabled="!teacherId">
        <option value="">-- Выберите группу --</option>
        <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PropType } from 'vue'

type NullableNumber = number | null

const props = defineProps({
  branchId: { type: Number as PropType<NullableNumber>, default: null },
  teacherId: { type: Number as PropType<NullableNumber>, default: null },
  groupId: { type: Number as PropType<NullableNumber>, default: null },
  branches: { type: Array as PropType<Array<{ id: number; name: string }>>, default: () => [] },
  teachers: { type: Array as PropType<Array<{ id: number; full_name: string }>>, default: () => [] },
  groups: { type: Array as PropType<Array<{ id: number; name: string }>>, default: () => [] },
})

const emit = defineEmits<{
  (e: 'update:branchId', value: NullableNumber): void
  (e: 'update:teacherId', value: NullableNumber): void
  (e: 'update:groupId', value: NullableNumber): void
  (e: 'branch-change', value: NullableNumber): void
  (e: 'teacher-change', value: NullableNumber): void
  (e: 'group-change', value: NullableNumber): void
}>()

const branchIdValue = computed(() => props.branchId ?? '')
const teacherIdValue = computed(() => props.teacherId ?? '')
const groupIdValue = computed(() => props.groupId ?? '')

function parseId(value: string): NullableNumber {
  if (value === '' || value === null || value === undefined) return null
  const parsed = Number(value)
  return Number.isNaN(parsed) ? null : parsed
}

function onBranchSelect(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  const id = parseId(value)
  emit('update:branchId', id)
  emit('update:teacherId', null)
  emit('update:groupId', null)
  emit('branch-change', id)
}

function onTeacherSelect(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  const id = parseId(value)
  emit('update:teacherId', id)
  emit('update:groupId', null)
  emit('teacher-change', id)
}

function onGroupSelect(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  const id = parseId(value)
  emit('update:groupId', id)
  emit('group-change', id)
}
</script>

<style scoped>
.report-filters {
  background: #fff7f0;
  border: 1px solid #ffe3cf;
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 14px 20px;
  align-items: flex-end;
  margin-bottom: 16px;
}
.filter-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 180px;
}
.filter-field label {
  font-size: 12px;
  font-weight: 700;
  color: var(--brand-orange);
  text-transform: uppercase;
  letter-spacing: .05em;
}
.filter-field select,
.filter-field input[type="date"],
.filter-field input[type="text"] {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1.5px solid #ffe3cf;
  font-size: 14px;
  font-family: inherit;
  background: #fff;
  outline: none;
}
.filter-field select:focus,
.filter-field input:focus {
  border-color: var(--brand-orange);
}

@media (max-width: 760px) {
  .report-filters {
    flex-direction: column;
  }
}
</style>
