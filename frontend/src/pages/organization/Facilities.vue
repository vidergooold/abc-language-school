<template>
  <div class="org-section">
    <h2 class="section-title">
      Материально-техническое обеспечение и оснащенность образовательного процесса
    </h2>

    <h3>О наличии оборудованных учебных кабинетов</h3>
    <div class="facility-card">
      <p><strong>Количество филиалов:</strong> {{ facilities.length }}</p>
      <p><strong>Кабинеты:</strong> указаны в каноническом перечне ниже.</p>
    </div>

    <div class="branches-list">
      <div v-for="facility in facilities" :key="facility.branch" class="facility-card">
        <h4>{{ facility.branch }}</h4>
        <p><strong>Кабинеты:</strong> {{ facility.classrooms.join(', ') }}</p>
      </div>
    </div>

    <h3>Об условиях охраны здоровья</h3>
    <p>
      Помещения соответствуют санитарным и противопожарным нормам, требованиям охраны
      труда. Условия доступности для инвалидов и лиц с ОВЗ обеспечиваются по месту
      проведения занятий.
    </p>
  </div>
</template>

<script setup lang="ts">
const facilities = [
  { branch: 'Гимназия 11 «Гармония»', classrooms: ['каб. 113', 'каб. 114'] },
  { branch: 'Гимназия №7 «Сибирская»', classrooms: ['каб. 119'] },
  { branch: 'МАОУ ЛИТ', classrooms: ['каб. библиотека', 'каб. 116'] },
  { branch: 'МАОУ НГПЛ', classrooms: ['каб. 115'] },
  { branch: 'МАОУ НЭЛ', classrooms: ['каб. 205'] },
  { branch: 'МАОУ СОШ №216', classrooms: ['каб. 317', 'каб. 410'] },
  { branch: 'МАОУ СОШ №217', classrooms: ['каб. 314А'] },
  { branch: 'МАОУ СОШ №218', classrooms: ['каб. АВС'] },
  { branch: 'МАОУ СОШ №221', classrooms: ['каб. 128', 'каб. 311'] },
  { branch: 'МАОУ СОШ №222', classrooms: ['каб. 128', 'каб. 311'] },
  { branch: 'МБОУ Гимназия №5', classrooms: ['каб. 191'] },
  { branch: 'МБОУ Гимназия №9', classrooms: ['каб. 37', 'каб. 41'] },
  { branch: 'МБОУ СОШ №11', classrooms: ['каб. 203'] },
  { branch: 'МБОУ СОШ №121 «Академическая»', classrooms: ['каб. 214'] },
  { branch: 'МБОУ СОШ №13', classrooms: ['каб. 18'] },
  { branch: 'МБОУ СОШ №155', classrooms: ['каб. 426'] },
  { branch: 'МБОУ СОШ №167', classrooms: ['каб. 211'] },
  { branch: 'МБОУ СОШ №186', classrooms: ['каб. 211'] },
  { branch: 'МБОУ СОШ №188', classrooms: ['каб. 409', 'каб. АВС'] },
  { branch: 'МБОУ СОШ №195', classrooms: ['каб. 229'] },
  { branch: 'МБОУ СОШ №56', classrooms: ['каб. 3', 'каб. 10'] },
]
</script>

<style scoped>
.org-section {
  font-size: 17px;
  line-height: 1.6;
}
.section-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 20px;
}
h3 {
  font-size: 20px;
  font-weight: 700;
  margin-top: 24px;
  margin-bottom: 12px;
}
h4 {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-orange);
  margin-bottom: 10px;
}
p {
  margin-bottom: 16px;
}
.branches-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}
.facility-card {
  background: #ffe3cf;
  padding: 20px;
  border-radius: 12px;
}
</style>
